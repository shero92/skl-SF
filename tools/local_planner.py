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
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

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

def clean_data(raw, agent):
    data = json.loads(raw)
    if agent == "claude":
        if isinstance(data, dict) and "structured_output" in data:
            data = data["structured_output"]
        elif isinstance(data, dict) and isinstance(data.get("result"), str):
            data = json.loads(data["result"])
    if not isinstance(data, dict) or set(data) != {"tasks", "updates"}:
        raise ValueError("Agent must return ONLY a JSON proposal")
    return data

def local_ai(agent, prompt, conf):
    # Prevent accidental API-key billing; rely on existing logged-in CLI subscriptions.
    env_before = {key: os.environ.pop(key) for key in BANNED_ENV if key in os.environ}
    try:
        with tempfile.TemporaryDirectory(prefix="skl-readonly-plan-") as temp:
            temp = Path(temp)
            schema_path = temp/"schema.json"
            schema_path.write_text(json.dumps(schema()), encoding="utf-8")
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
    sha = git("rev-parse", "HEAD")
    before = digest()
    checkpoint = load(BASE/"checkpoint.json", {})
    if checkpoint.get("digest") == before:
        print("No meaningful changes since analysis; skipping AI.")
        return
    cooldowns = load(BASE/"cooldowns.json", {})
    def cooling(a):
        stamp = cooldowns.get(a, {}).get("retry_after")
        return bool(stamp and datetime.fromisoformat(stamp) > now)
    if cooling(agent):
        agent = "codex" if agent == "claude" else "claude"
    if cooling(agent):
        print("Both coding agents are in quota cooldown.")
        return
    packet = context()
    instruction = ("You are a READ-ONLY task analyst. Return ONLY a JSON object matching the given schema "
                   "with keys tasks[] and updates[]. Do not request/edit files, do not inspect images, "
                   "never fabricate line numbers or evidence. At most 4 small new tasks, no art/gameplay/"
                   "character/UI tasks, only existing source file paths. Do not mark any task done or "
                   "claim in-progress work. Ground tasks in the listed goals, tasks and git log. "
                   "No useful change => empty arrays. \n\n" + packet)
    outcome = local_ai(agent, instruction, conf) if not dry_run else {
        "agent": agent, "exit": 0, "stdout": '{"tasks":[],"updates":[]}',
        "error": "", "duration_seconds": 0, "usage": None, "api_equivalent_usd": None}
    if outcome["exit"] and check_quota(outcome["error"] + outcome["stdout"]):
        cooldowns[agent] = {"retry_after": (now+timedelta(hours=6)).isoformat(),
                            "reason": "CLI usage/rate limit; no retry loop"}
        agent2 = "codex" if agent == "claude" else "claude"
        if not cooling(agent2) and not dry_run:
            outcome = local_ai(agent2, instruction, conf)  # one fallback to other agent only
        agent = outcome["agent"]
    run_id = now.strftime("%Y%m%d-%H%M%S") + "-" + agent
    result = {"run_id": run_id, "agent": agent, "base_sha": sha,
              "input_digest": before, "duration_seconds": outcome["duration_seconds"],
              "usage": outcome["usage"], "cost_usd_estimate": outcome["api_equivalent_usd"],
              "exit": outcome["exit"], "status": "failed"}
    proposal = None
    if outcome["exit"] == 0:
        try:
            proposal = clean_data(outcome["stdout"], agent)
            result["status"] = "proposal_valid"
        except (ValueError, TypeError) as exc:
            result["reason"] = str(exc)[:300]
    else:
        result["reason"] = ("usage_limit" if check_quota(outcome["error"]) else "cli_error")
    if dry_run:
        print(json.dumps(result))
        return
    branch = "planning/" + now.strftime("%Y%m%d-%H%M%S") + "-" + agent
    git("switch", "-c", branch)
    try:
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
        invoke([sys.executable, "tools/agent_workflow.py", "--write"])
        invoke([sys.executable, "tools/generate_project_indexes.py", "--write"])
        git("add", "-A", "--", ".agents/planner", ".agents/tasks", ".agents/project/TASKS.md",
            ":(glob)**/FILES.md")
        changed = git("diff", "--cached", "--name-only").splitlines()
        if not changed:
            return
        if any(not (p.startswith((".agents/planner/", ".agents/tasks/")) or
                    p == ".agents/project/TASKS.md" or p.endswith("/FILES.md")) for p in changed):
            raise RuntimeError("Planning diff outside safe allowlist")
        git("commit", "-m", "chore: local read-only planner results\n\nAgent: " + agent +
            "\nTask-ID: planning\nCost-USD: unknown")
        git("push", "-u", "origin", branch)
        pr = invoke(["gh", "pr", "create", "--base", "main", "--head", branch,
                     "--title", "Local plan " + run_id,
                     "--body", "Read-only local subscription planner result; validation and scope gate before merge."], timeout=120)
        print(pr.stdout)
        if conf.get("auto_merge_planning", False):
            # Real CI must complete successfully. Do not merge if no checks configured,
            # a check fails, or the PR includes any non-planning path.
            check = invoke(["gh", "pr", "checks", branch, "--watch", "--fail-fast"],
                           timeout=conf.get("ci_wait_seconds", 600), check=False)
            if check.returncode == 0:
                names = invoke(["gh", "pr", "diff", branch, "--name-only"]).stdout.splitlines()
                if names and all(n.startswith((".agents/planner/", ".agents/tasks/")) or
                                 n == ".agents/project/TASKS.md" or n.endswith("/FILES.md") for n in names):
                    latest = git("rev-parse", "HEAD")
                    invoke(["gh", "pr", "merge", branch, "--squash",
                            "--match-head-commit", latest], timeout=120)
    finally:
        # Avoid deleting or resetting any uncommitted work on error.
        if not git("status", "--porcelain"):
            git("switch", "main")

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
