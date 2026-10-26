#!/usr/bin/env python3
"""Local Windows Claude/Codex PLANNING ONLY. Never executes a coding task."""
from __future__ import annotations
import argparse
from datetime import datetime, timedelta
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

from runner_safety import main_generated

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / ".agents/planner"
CONFIG = BASE / "config.json"
TZ = ZoneInfo("Europe/Berlin")
BANNED_ENV = ("OPENAI_API_KEY", "ANTHROPIC_API_KEY")
SKIP = (".agents/planner/runs/", ".agents/planner/checkpoint.json",
        ".agents/planner/cooldowns.json", ".agents/planner/daily/",
        ".agents/project/TASKS.md")

def invoke(argv, *, cwd=ROOT, stdin=None, timeout=120, check=True):
    proc = subprocess.run(argv, input=stdin, text=True, encoding="utf-8",
                          errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          cwd=cwd, timeout=timeout)
    if check and proc.returncode:
        raise RuntimeError("Command failed (" + " ".join(argv[:3]) + "): " + proc.stderr[-500:])
    return proc

def git(*args):
    return invoke(["git", *args]).stdout.strip()

def load(path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

def digest():
    """Exclude machine logs, checkpoints and generated dashboards."""
    h = hashlib.sha256()
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or ".git" in p.parts or ".godot" in p.parts:
            continue
        relative = p.relative_to(ROOT).as_posix()
        if relative.startswith((".agents/planner/", ".agents/tasks/")):
            if relative.startswith(SKIP) or p.suffix.lower() in (".png",".jpg",".jpeg",".webp",".gif",".svg"):
                continue
            # Only stable planning inputs and canonical task files.
            if relative.startswith(".agents/planner/") and not (
                relative.endswith(("goals.json", "goal.md", "state.json", "plan.json")) or
                "/requests/" in relative):
                continue
        else:
            continue
        h.update(relative.encode() + b"\0" + p.read_bytes())
    # Ground proposals in meaningful map and agent-code revisions, not automation logs.
    last = git("rev-list", "-1", "HEAD", "--", "map_factory", "tools", "scenes/map_factory_preview.gd", "AGENTS.md")
    h.update(last.encode())
    return h.hexdigest()

def context():
    parts = []
    paths = [ROOT/"AGENTS.md", ROOT/"INDEX.md", BASE/"PROMPT_RULES.md",
             BASE/"goals.json", ROOT/".agents/project/TASKS.md"]
    paths += sorted((BASE/"goals").glob("GOAL-*/goal.md"))
    paths += sorted((BASE/"goals").glob("GOAL-*/state.json"))
    paths += sorted((BASE/"requests").glob("REQ-*.json"))
    # Read only text, never reference files or production images.
    paths += sorted((ROOT/".agents/tasks").glob("TASK-*.md"))
    for path in paths:
        if path.is_file():
            rel = path.relative_to(ROOT).as_posix()
            body = path.read_text(encoding="utf-8")[:4500]
            parts.append("--- " + rel + " ---\n" + body)
    parts.append("--- recent git log ---\n" + git("log", "-5", "--format=%h %s"))
    return "\n\n".join(parts)[:28000]

def check_quota(stderr):
    return bool(re.search(r"rate.?limit|usage.?limit|quota.?exceed|429|too many requests|resets in", stderr, re.I))

def schema():
    return load(BASE/"proposal.schema.json", {})

def nullable(prop):
    kind = prop.get("type")
    if isinstance(kind, str):
        return {**prop, "type": [kind, "null"]}
    if isinstance(kind, list):
        return prop if "null" in kind else {**prop, "type": kind + ["null"]}
    return {"anyOf": [prop, {"type": "null"}]}

def strict_schema(node):
    """OpenAI strict outputs (codex): every property required, optional ones nullable."""
    if isinstance(node, list):
        return [strict_schema(n) for n in node]
    if not isinstance(node, dict):
        return node
    out = {k: strict_schema(v) for k, v in node.items()}
    if isinstance(out.get("properties"), dict):
        required = set(node.get("required", []))
        out["properties"] = {k: v if k in required else nullable(v) for k, v in out["properties"].items()}
        out["required"] = list(out["properties"])
        out["additionalProperties"] = False
    return out

def drop_nulls(items):
    return [{k: v for k, v in i.items() if v is not None} if isinstance(i, dict) else i for i in items]

def clean_data(raw, agent):
    data = json.loads(raw)
    if agent == "claude":
        if isinstance(data, dict) and "structured_output" in data:
            data = data["structured_output"]
        elif isinstance(data, dict) and isinstance(data.get("result"), str):
            data = json.loads(data["result"])
    if not isinstance(data, dict) or set(data) != {"tasks", "updates"}:
        raise ValueError("Agent must return ONLY a JSON proposal")
    # Strict schemas send optional fields as null; goal_task_factory expects them absent.
    return {key: drop_nulls(value) if isinstance(value, list) else value for key, value in data.items()}

SECRET = re.compile(r"(?i)((?:(?:api[_-]?key|token|secret|password|authorization)\s*[:=]\s*)?bearer\s+"
                    r"|(?:api[_-]?key|token|secret|password|authorization)\s*[:=]\s*)\S+"
                    r"|\b(?:sk|ghp|gho|ghs|ghu|github_pat|xox[a-z])[-_A-Za-z0-9]{8,}")

def stderr_tail(text, limit=1200):
    """Last part of CLI stderr for the run log, with credentials redacted."""
    return SECRET.sub(lambda m: (m.group(1) or "") + "[REDACTED]", text or "")[-limit:].strip()

def local_ai(agent, prompt, conf):
    # Prevent accidental API-key billing; rely on existing logged-in CLI subscriptions.
    env_before = {key: os.environ.pop(key) for key in BANNED_ENV if key in os.environ}
    try:
        with tempfile.TemporaryDirectory(prefix="skl-readonly-plan-") as temp:
            temp = Path(temp)
            schema_path = temp/"schema.json"
            schema_path.write_text(json.dumps(strict_schema(schema())), encoding="utf-8", newline="\n")
            cwd = temp  # no production images or repository tools in the agent workspace
            started = time.monotonic()
            if agent == "claude":
                command = ["claude", "-p", "--permission-mode", "plan",
                           "--tools", "", "--effort", "low",
                           "--output-format", "json", "--json-schema", json.dumps(schema()), prompt]
                proc = invoke(command, cwd=cwd, timeout=conf["timeout_seconds"], check=False)
                raw = proc.stdout
                try:
                    meta = json.loads(raw)
                except ValueError:
                    meta = {}
                usage = meta.get("usage") if isinstance(meta, dict) else None
                cost = meta.get("total_cost_usd") if isinstance(meta, dict) else None
            else:
                result = temp/"result.json"
                command = ["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check",
                           "--output-schema", str(schema_path), "--output-last-message", str(result), "-"]
                proc = invoke(command, cwd=cwd, stdin=prompt, timeout=conf["timeout_seconds"], check=False)
                raw = result.read_text(encoding="utf-8") if result.is_file() else ""
                usage, cost = None, None
            return {"agent": agent, "exit": proc.returncode,
                    "stdout": raw[:100000], "error": proc.stderr[-1200:],
                    "duration_seconds": round(time.monotonic()-started, 1),
                    "usage": usage, "api_equivalent_usd": cost}
    finally:
        os.environ.update(env_before)

def planning_path(path):
    return path.startswith((".agents/planner/", ".agents/tasks/")) and not main_generated(path)


def refresh_main(agent):
    """Local-only follow-up to a successfully merged plan. Never write in a PR branch."""
    from agent_runner import exclusive, main_commit
    with exclusive("main-merge"):
        if git("branch", "--show-current") != "main" or git("status", "--porcelain"):
            raise RuntimeError("Planner regeneration requires clean main")
        git("pull", "--ff-only", "origin", "main")
        main_commit("chore: refresh generated outputs after planning", agent, "planning", verify=True)


def run(requested=None, dry_run=False):
    conf = load(CONFIG, {})
    if not conf.get("planning_enabled", False):
        print("Local planner paused in config.json")
        return
    if os.name != "nt" and not dry_run:
        raise RuntimeError("Scheduled planning runs only on local Windows host")
    now = datetime.now(TZ)
    schedule = conf["schedule"]
    hour = now.strftime("%H:%M")
    agent = requested or next((s["agent"] for s in schedule if s["time"] == hour), None)
    if agent not in ("claude", "codex"):
        raise ValueError("Pass --agent claude|codex for a manual launch")
    if git("branch", "--show-current") != "main" or git("status", "--porcelain"):
        raise RuntimeError("Start from a clean main worktree")
    git("pull", "--ff-only", "origin", "main")
    # Owner-supplied art is processed by deterministic local tools only,
    # never by a model; disabled until supervised configuration.
    if conf.get("art_integration_enabled", False):
        invoke([sys.executable, "tools/art_delivery.py", "--integrate"], timeout=600)
    if conf.get("graphics_issue_enabled", False):
        invoke([sys.executable, "tools/art_requests.py", "notify"], timeout=180)
    sha = git("rev-parse", "HEAD")
    before = digest()
    run_id = now.strftime("%Y%m%d-%H%M%S") + "-" + agent
    branch = "planning/" + run_id
    merged = False
    try:
        if not dry_run:
            git("switch", "-c", branch)
            pulse_proc = invoke([sys.executable, "tools/goal_task_factory.py", "pulse"])
            pulse_result = json.loads(pulse_proc.stdout)
            save(BASE/"runs"/(run_id+"-pulse.json"), pulse_result)
            print("Milestone pulse: " + json.dumps(pulse_result))
        else:
            pulse_result = {"created": []}
        checkpoint = load(BASE/"checkpoint.json", {})
        skip_reason = "unchanged_inputs" if checkpoint.get("digest") == before else None
        cooldowns = load(BASE/"cooldowns.json", {})
        def cooling(a):
            stamp = cooldowns.get(a, {}).get("retry_after")
            return bool(stamp and datetime.fromisoformat(stamp) > now)
        if cooling(agent):
            agent = "codex" if agent == "claude" else "claude"
        if cooling(agent):
            skip_reason = "quota_cooldown"
        packet = context()
        instruction = ("You are a READ-ONLY task analyst. Return ONLY a JSON object matching the given schema "
                       "with keys tasks[] and updates[]. Do not request/edit files, do not inspect images, "
                       "never fabricate line numbers or evidence. At most 4 small new tasks, no art/gameplay/"
                       "character/UI tasks, only existing source file paths. Do not mark any task done or "
                       "claim in-progress work. Approved milestones already have deterministic pulse tasks; "
                       "only propose extra tasks or updates, never duplicate a goal step. "
                       "Text ART request records (.md/.json) and graphics QUEUE.md are allowed, never images or deliveries. "
                       "Ground tasks in the listed goals, tasks and git log. "
                       "No useful change => empty arrays. \n\n" + packet)
        outcome = {
            "agent": agent, "exit": 0, "stdout": '{"tasks":[],"updates":[]}',
            "error": "", "duration_seconds": 0, "usage": None, "api_equivalent_usd": None}
        if not dry_run and not skip_reason:
            try:
                outcome = local_ai(agent, instruction, conf)
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                outcome.update(exit=1, error=str(exc))
        if outcome["exit"] and check_quota(outcome["error"] + outcome["stdout"]):
            cooldowns[agent] = {"retry_after": (now+timedelta(hours=6)).isoformat(),
                                "reason": "CLI usage/rate limit; no retry loop"}
            agent2 = "codex" if agent == "claude" else "claude"
            if not cooling(agent2) and not dry_run:
                try:
                    outcome = local_ai(agent2, instruction, conf)  # one fallback only
                except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                    outcome.update(exit=1, error=str(exc))
            agent = outcome["agent"]
        result = {"run_id": run_id, "agent": agent, "base_sha": sha,
                  "input_digest": before, "duration_seconds": outcome["duration_seconds"],
                  "usage": outcome["usage"], "cost_usd_estimate": outcome["api_equivalent_usd"],
                  "exit": outcome["exit"], "status": "failed", "pulse": pulse_result}
        proposal = None
        if skip_reason:
            result.update(status="ai_skipped", reason=skip_reason)
        elif outcome["exit"] == 0:
            try:
                proposal = clean_data(outcome["stdout"], agent)
                result["status"] = "proposal_valid"
            except (ValueError, TypeError) as exc:
                result["reason"] = str(exc)[:300]
        else:
            result["reason"] = ("usage_limit" if check_quota(outcome["error"]) else "cli_error")
            result["stderr_tail"] = stderr_tail(outcome["error"])
        if dry_run:
            print(json.dumps(result))
            return
        if proposal is not None:
            proposal_path = BASE/"runs"/(run_id+"-proposal.json")
            save(proposal_path, proposal)
            applied = invoke([sys.executable, "tools/goal_task_factory.py",
                              "apply-proposal", str(proposal_path), "--run-key", run_id],
                             check=False)
            if applied.returncode != 0:
                result["status"] = "rejected"
                result["reason"] = applied.stderr[-400:]
            else:
                result["applied"] = json.loads(applied.stdout)
                result["status"] = "proposed"
        result["source_sha"] = sha
        result["completed_at"] = datetime.now(TZ).isoformat()
        save(BASE/"runs"/(run_id+".json"), result)
        save(BASE/"cooldowns.json", cooldowns)
        save(BASE/"checkpoint.json", {"main_sha": sha, "digest": digest(), "last_run": run_id})
        git("add", "-A", "--", ".agents/planner", ".agents/tasks")
        changed = git("diff", "--cached", "--name-only").splitlines()
        if not changed:
            return
        if any(not planning_path(p) for p in changed):
            raise RuntimeError("Planning diff outside safe allowlist")
        invoke([sys.executable, "tools/run_tests.py", "--changed"], timeout=1800)
        git("commit", "-m", "chore: local read-only planner results\n\nAgent: " + agent +
            "\nTask-ID: planning\nCost-USD: unknown")
        git("push", "-u", "origin", branch)
        pr = invoke(["gh", "pr", "create", "--base", "main", "--head", branch,
                     "--title", "Local plan " + run_id,
                     "--body", "Read-only local subscription planner result; validation and scope gate before merge."], timeout=120)
        print(pr.stdout)
        print("Created tasks: " + ", ".join(pulse_result["created"] + result.get("applied", {}).get("created", [])))
        if conf.get("auto_merge_planning", False):
            # Real CI must complete successfully. Do not merge if no checks configured,
            # a check fails, or the PR includes any non-planning path.
            check = invoke(["gh", "pr", "checks", branch, "--watch", "--fail-fast"],
                           timeout=conf.get("ci_wait_seconds", 600), check=False)
            if check.returncode == 0:
                names = invoke(["gh", "pr", "diff", branch, "--name-only"]).stdout.splitlines()
                if names and all(planning_path(n) for n in names):
                    latest = git("rev-parse", "HEAD")
                    invoke(["gh", "pr", "merge", branch, "--squash",
                            "--match-head-commit", latest], timeout=120)
                    merged = True
    finally:
        # Avoid deleting or resetting any uncommitted work on error.
        if not git("status", "--porcelain"):
            git("switch", "main")
        if merged:
            refresh_main(agent)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=("claude", "codex"))
    parser.add_argument("--dry-run", action="store_true")
    options = parser.parse_args()
    try:
        run(options.agent, options.dry_run)
    except (ValueError, RuntimeError, subprocess.TimeoutExpired, OSError) as e:
        print("local planner:", e, file=sys.stderr)
        sys.exit(1)
