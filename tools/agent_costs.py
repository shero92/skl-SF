#!/usr/bin/env python3
"""Task receipts for local Claude Code and Codex sessions."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid

ROOT = Path(os.environ.get("SKL_COST_ROOT", Path(__file__).resolve().parents[1]))
BASE = ROOT / ".agents" / "monitoring"
LOCAL = BASE / ".local"
FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens",
          "cache_creation_input_tokens", "cache_creation_1h_input_tokens")

def get(path, default=None):
    return json.loads(path.read_text(encoding="utf8")) if path.is_file() else default

def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf8", newline="\n")
    os.replace(tmp, path)

def usage(value, agent="codex"):
    if not isinstance(value, dict):
        return None
    if agent == "claude":
        # Anthropic separates uncached, cache reads, and cache writes.
        # Normalize input_tokens to INCLUDE all three for task comparison.
        required = ("input_tokens", "output_tokens")
        if not all(key in value for key in required):
            return None
        cc = value.get("cache_creation") or {}
        if not isinstance(cc, dict):
            cc = {}
        raw_in = value["input_tokens"]
        read = value.get("cache_read_input_tokens", 0)
        created = value.get("cache_creation_input_tokens", 0)
        one_hour = cc.get("ephemeral_1h_input_tokens", 0)
        values = (raw_in, read, created, one_hour, value["output_tokens"])
        if any(type(n) is not int or n < 0 for n in values) or one_hour > created:
            return None
        return {"input_tokens": raw_in + read + created,
                "cached_input_tokens": read, "output_tokens": value["output_tokens"],
                "reasoning_output_tokens": 0, "cache_creation_input_tokens": created,
                "cache_creation_1h_input_tokens": one_hour}
    nums = {k: value.get(k, 0) for k in FIELDS}
    if any(type(v) is not int or v < 0 for v in nums.values()):
        return None
    if nums["cached_input_tokens"] > nums["input_tokens"]:
        return None
    return nums

def cost_from_tokens(u, agent, model):
    if u is None or not isinstance(model, str):
        return None
    prices = get(BASE / "pricing.json", {}).get("models", {})
    # Date-suffixed Claude model identifiers use the same published model rates.
    key = "claude-opus-5-5" if agent == "claude" and model.startswith("claude-opus-5-5") else model
    rates = prices.get(key)
    if not rates:
        return None
    uncached = u["input_tokens"] - u["cached_input_tokens"] - u["cache_creation_input_tokens"]
    try:
        total = (uncached * rates["input_per_million"]
                 + u["cached_input_tokens"] * rates["cached_input_per_million"]
                 + u["output_tokens"] * rates["output_per_million"])
        if agent == "claude":
            total += ((u["cache_creation_input_tokens"] - u["cache_creation_1h_input_tokens"])
                      * rates["cache_creation_5m_per_million"])
            total += u["cache_creation_1h_input_tokens"] * rates["cache_creation_1h_per_million"]
        return round(total / 1000000, 6)
    except (KeyError, TypeError):
        return None

def read_transcript(path, agent):
    if not path or not Path(path).is_file():
        return None, None, None
    items, turns, last = {}, [], None
    model, first = None, None
    for i, line in enumerate(Path(path).open(encoding="utf8")):
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        first = first or row.get("timestamp")
        payload = row.get("payload") or {}
        if agent == "claude" and row.get("type") == "assistant":
            msg = row.get("message") or {}
            u = usage(msg.get("usage"), "claude")
            if u is not None:
                key = msg.get("id") or str(i)
                items[key] = u
            model = msg.get("model") or model
        if agent == "codex":
            if row.get("type") == "turn_context":
                model = payload.get("model") or model
            if row.get("type") == "turn.completed":
                u = usage(row.get("usage"))
                if u is not None:
                    turns.append(u)
            if row.get("type") == "event_msg" and payload.get("type") == "token_count":
                u = usage((payload.get("info") or {}).get("total_token_usage"))
                if u is not None:
                    last = u
    parts = list(items.values()) if agent == "claude" else ([last] if last is not None else turns)
    return ({k: sum(part[k] for part in parts) for k in FIELDS} if parts else None), model, first

def import_codex(args):
    """Import trusted codex exec --json turn.completed events, never their message content."""
    active = get(LOCAL / "active.json")
    if not active or active.get("agent") != "codex":
        raise ValueError("Start a Codex task with 'start --agent codex' first")
    path = Path(args.path)
    if not path.is_file():
        raise ValueError("Missing Codex --json output file")
    turns, thread_id, detected_model = [], None, None
    # Windows PowerShell 5.1 Tee-Object writes UTF-16LE with a BOM.
    with path.open("rb") as probe:
        bom = probe.read(4)
    encoding = "utf-16" if bom.startswith((bytes([255, 254]), bytes([254, 255]))) else "utf-8-sig"
    try:
        with path.open(encoding=encoding) as lines:
            for line in lines:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if obj.get("type") == "thread.started":
                    thread_id = obj.get("thread_id") or thread_id
                if obj.get("type") == "turn.completed":
                    u = usage(obj.get("usage"), "codex")
                    if u is not None:
                        turns.append(u)
                if obj.get("type") == "turn.started":
                    detected_model = obj.get("model") or detected_model
    except (OSError, UnicodeError) as exc:
        raise ValueError("Unable to read the JSONL usage file") from exc
    if not turns:
        raise ValueError("No valid turn.completed.usage records found; don't finish yet")
    totals = {k: sum(u[k] for u in turns) for k in FIELDS}
    identifier = str(thread_id) if thread_id else "import:" + str(path.resolve())
    filename = "session_" + hashlib.sha256(identifier.encode()).hexdigest()[:16] + ".json"
    dest = LOCAL / filename
    item = get(dest, {})
    item.update({"agent": "codex", "imported_usage": totals,
                 "model": args.model or detected_model or item.get("model")})
    put(dest, item)
    print("Imported Codex usage:", totals["input_tokens"], "input;",
          totals["output_tokens"], "output;", "model:", item.get("model") or "unknown")
    print("Only token totals are saved; raw --json logs stay local.")

def old_session(start, first):
    if not first:
        return False
    try:
        a = datetime.fromisoformat(first.replace("Z", "+00:00"))
        b = datetime.fromisoformat(start.replace("Z", "+00:00"))
        return (b-a).total_seconds() > 15
    except (TypeError, ValueError):
        return False

def report(check=False):
    rows = {}
    for file in sorted((BASE / "receipts").glob("TASK-*.json")):
        r = get(file)
        task = r["task_id"]
        row = rows.setdefault(task, {"task_id": task, "agents": set(), "known_usd": 0.0,
                                      "unknown_costs": 0, "unknown_token_receipts": 0,
                                      "input_tokens": 0, "cached_input_tokens": 0,
                                      "output_tokens": 0, "reasoning_output_tokens": 0,
                                      "receipts": 0})
        row["agents"].add(r["agent"])
        row["receipts"] += 1
        if r["cost_usd"] is None:
            row["unknown_costs"] += 1
        else:
            row["known_usd"] += r["cost_usd"]
        if r["tokens"]:
            row["input_tokens"] += r["tokens"]["input_tokens"]
            row["cached_input_tokens"] += r["tokens"]["cached_input_tokens"]
            row["output_tokens"] += r["tokens"]["output_tokens"]
            row["reasoning_output_tokens"] += r["tokens"]["reasoning_output_tokens"]
        else:
            row["unknown_token_receipts"] += 1
    data = list(rows.values())
    for row in data:
        row["agents"] = sorted(row["agents"])
        row["known_usd"] = round(row["known_usd"], 6)
    data.sort(key=lambda r: (-r["known_usd"], r["task_id"]))
    summary = {"tasks": data, "total_known_usd": round(sum(r["known_usd"] for r in data), 6),
               "missing_cost_receipts": sum(r["unknown_costs"] for r in data),
               "missing_token_receipts": sum(r["unknown_token_receipts"] for r in data)}
    json_text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    lines = ["# Agent task costs", "", "<!-- GENERATED by tools/agent_costs.py -->", "",
             "| Task | Agents | Known USD | Missing costs | Input tokens | Cached input | Output tokens | Reasoning | Missing tokens | Receipts |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in data:
        lines.append("| {} | {} | {:.6f} | {} | {} | {} | {} | {} | {} | {} |".format(
            r["task_id"], ", ".join(r["agents"]), r["known_usd"],
            r["unknown_costs"], r["input_tokens"], r["cached_input_tokens"],
            r["output_tokens"], r["reasoning_output_tokens"],
            r["unknown_token_receipts"], r["receipts"]))
    lines += ["", "Missing costs are unknown, not zero. Estimates are not subscription invoices.", ""]
    outputs = [(BASE/"summary.json", json_text), (BASE/"summary.md", "\n".join(lines))]
    for path, content in outputs:
        if check:
            if not path.exists() or path.read_text(encoding="utf8") != content:
                raise ValueError("Stale report; run python3 tools/agent_costs.py report")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf8", newline="\n")

def git(*parts):
    """Run only narrowly scoped git operations from the active project worktree."""
    result = subprocess.run(["git", "-C", str(ROOT), *parts],
                            capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise ValueError("git " + " ".join(parts[:2]) + ": "
                         + (result.stderr.strip() or result.stdout.strip()))
    return result.stdout.strip()

def complete_task(args):
    """Finalize token receipt, commit it with STAGED task work, push task branch."""
    active = get(LOCAL / "active.json")
    if not active or not re.fullmatch(r"TASK-\d{4}", active["task_id"]):
        raise ValueError("Start a real TASK-#### first; TEST tasks must never push")
    task = active["task_id"]
    if not list((ROOT / ".agents" / "tasks").glob(task + "_*.md")):
        raise ValueError("Missing canonical task record for " + task)
    branch = git("symbolic-ref", "--short", "HEAD")
    if branch in ("main", "master") or branch.startswith("release/"):
        raise ValueError("Refusing to commit/push to protected branch " + branch)
    staged = [x for x in git("diff", "--cached", "--name-only", "--diff-filter=ACMR").splitlines()
              if x.strip()]
    if any(x.startswith(".agents/monitoring/.local/") or x.lower().endswith(
            (".jsonl", ".env", ".pem", ".key")) for x in staged):
        raise ValueError("Unstage private logs/keys before completion")
    if not any(not x.startswith(".agents/monitoring/") for x in staged):
        raise ValueError("First git add the intentional task code/evidence files")
    if not args.message.strip():
        raise ValueError("Commit message cannot be empty")
    # Preflight must happen before deleting the active task snapshot.
    receipt, path = run(argparse.Namespace(command="finish", manual_cost_usd=None, defer_report=getattr(args, "no_summary", False)))
    rel = path.relative_to(ROOT).as_posix()
    if getattr(args, "no_summary", False):
        git("add", "--", rel)
    else:
        git("add", "--", rel, ".agents/monitoring/summary.json",
            ".agents/monitoring/summary.md")
    u = receipt["tokens"]
    trailers = [
        "Task-ID: " + task,
        "Agent: " + receipt["agent"],
        "Tokens-Input: " + (str(u["input_tokens"]) if u else "unknown"),
        "Tokens-Output: " + (str(u["output_tokens"]) if u else "unknown"),
        "Tokens-Cached-Input: " + (str(u["cached_input_tokens"]) if u else "unknown"),
        "Tokens-Reasoning: " + (str(u["reasoning_output_tokens"]) if u else "unknown"),
        "Cost-USD: " + (str(receipt["cost_usd"]) if receipt["cost_usd"] is not None else "unknown"),
        "Cost-Receipt: " + rel,
    ]
    git("commit", "-m", args.message.strip(), "-m", "\n".join(trailers))
    sha = git("rev-parse", "HEAD")
    print("Committed cost receipt with task work:", sha)
    if args.push:
        git("push", "origin", "HEAD:" + branch)
        print("Pushed to origin/" + branch)
    else:
        print("Push not requested; use git push origin " + branch)

def run(args):
    active_path = LOCAL/"active.json"
    if args.command == "start":
        task_id = args.task or ("TEST-" + uuid.uuid4().hex[:10])
        if not (re.fullmatch(r"TASK-\d{4}", task_id)
                or re.fullmatch(r"TEST-[0-9a-f]{10}", task_id)):
            raise ValueError("Expected TASK-#### or omit ID for a local-only test")
        if active_path.exists():
            raise ValueError("Finish the current task first")
        LOCAL.mkdir(parents=True, exist_ok=True)
        for file in LOCAL.glob("session_*.json"):
            file.unlink()
        put(active_path, {"task_id": task_id, "agent": args.agent,
                          "started_at": datetime.now(timezone.utc).isoformat()})
        print("Tracking " + task_id + (" (local test; do not commit)" if task_id.startswith("TEST-") else "") + "; open a FRESH " + args.agent + " session.")
        return
    if args.command == "hook":
        try:
            event = json.load(sys.stdin)
        except ValueError:
            return
        active = get(active_path)
        if not active or active["agent"] != args.agent:
            if args.statusline:
                print("Task: inactive")
            return
        sid = event.get("session_id") or event.get("thread-id")
        if not sid:
            return
        file = LOCAL / ("session_" + hashlib.sha256(str(sid).encode()).hexdigest()[:16] + ".json")
        item = get(file, {})
        item["transcript_path"] = event.get("transcript_path") or item.get("transcript_path")
        item["agent"] = args.agent
        if args.agent == "claude":
            cost = (event.get("cost") or {}).get("total_cost_usd")
            if type(cost) in (int, float) and 0 <= cost < float("inf"):
                item["cost_usd"] = cost
        model = event.get("model")
        model_id = model.get("id") if isinstance(model, dict) else model
        if isinstance(model_id, str) and model_id:
            item["model"] = model_id
        put(file, item)
        if args.statusline:
            print(active["task_id"] + " | session USD " + str(item.get("cost_usd", "unknown")))
        return
    if args.command == "report":
        report(args.check)
        return
    if args.command == "abort":
        # Stale tracking: discard without a receipt so no cost is attributed.
        active = get(active_path)
        if not active:
            raise ValueError("No active task")
        for file in LOCAL.glob("session_*.json"):
            file.unlink()
        active_path.unlink()
        print("Aborted tracking for " + active["task_id"] + "; no receipt written.")
        return
    if args.command == "import-codex":
        import_codex(args)
        return
    if args.command == "complete":
        complete_task(args)
        return
    if args.command == "diagnose":
        summary = []
        for path in sorted(LOCAL.glob("session_*.json")):
            info = get(path, {})
            transcript_path = info.get("transcript_path")
            transcript_found = bool(transcript_path and Path(transcript_path).is_file())
            u, model, _ = read_transcript(transcript_path, info.get("agent", "claude"))
            summary.append({"agent": info.get("agent"),
                            "has_transcript_path": bool(transcript_path),
                            "transcript_exists": transcript_found,
                            "tokens_found": u is not None or info.get("imported_usage") is not None,
                            "statusline_cost_found": info.get("cost_usd") is not None,
                            "model_found": bool(info.get("model") or model)})
        print(json.dumps({"active": bool(get(active_path)), "sessions": summary},
                         indent=2, sort_keys=True))
        return
    active = get(active_path)
    if not active:
        raise ValueError("No active task")
    agent, total_usd, missing, missing_tokens = active["agent"], 0.0, False, False
    totals = {k: 0 for k in FIELDS}
    models, sources, sessions = set(), set(), 0
    for file in LOCAL.glob("session_*.json"):
        item = get(file)
        if item["agent"] != agent:
            continue
        sessions += 1
        if agent == "codex" and item.get("imported_usage") is not None:
            u = usage(item["imported_usage"], "codex")
            model, first = item.get("model"), None
        else:
            u, model, first = read_transcript(item.get("transcript_path"), agent)
            model = item.get("model") or model
        if model:
            models.add(model)
        if old_session(active["started_at"], first):
            u, cost = None, None
            sources.add("old_session_unattributable")
        elif agent == "claude":
            cost = item.get("cost_usd")
            if cost is not None:
                sources.add("claude_statusline_estimate")
            else:
                cost = cost_from_tokens(u, agent, model)
                if cost is not None:
                    sources.add("claude_api_equivalent_estimate")
        else:
            cost = cost_from_tokens(u, agent, model)
            if cost is not None:
                sources.add("codex_api_equivalent_estimate")
        if u is None:
            missing_tokens = True
        else:
            for k in FIELDS:
                totals[k] += u[k]
        if cost is None:
            missing = True
        else:
            total_usd += cost
    if sessions == 0:
        missing = missing_tokens = True
    if args.manual_cost_usd is not None:
        if not 0 <= args.manual_cost_usd < float("inf"):
            raise ValueError("Manual USD must be nonnegative")
        total_usd, missing = args.manual_cost_usd, False
        sources.add("manual_estimate")
    receipt = {"schema": 1, "task_id": active["task_id"], "agent": agent,
               "started_at": active["started_at"], "ended_at": datetime.now(timezone.utc).isoformat(),
               "session_count": sessions, "models": sorted(models),
               "tokens": None if missing_tokens else totals,
               "cost_usd": None if missing else round(total_usd, 6),
               "source": sorted(sources) or ["unknown"],
               "coverage": "complete" if not (missing or missing_tokens) else "partial"}
    is_test = active["task_id"].startswith("TEST-")
    folder = LOCAL / "test_receipts" if is_test else BASE / "receipts"
    file = folder / (active["task_id"] + "_" + agent + "_" + uuid.uuid4().hex[:10] + ".json")
    put(file, receipt)
    active_path.unlink()
    # Local TEST sessions must not modify versioned reports. Otherwise
    # a smoke test makes git pull fail with a dirty summary file.
    if not is_test and not getattr(args, "defer_report", False):
        report()
    if is_test:
        print("Local TEST receipt (not committed; not included in leaderboard):", file.relative_to(ROOT))
    else:
        print("Commit this receipt WITH task code:", file.relative_to(ROOT))
    print("USD:", receipt["cost_usd"], "|", receipt["coverage"])
    if not is_test:
        print("Commit trailers: Task-ID:", active["task_id"], "| Agent:", agent, "| Cost-USD:", receipt["cost_usd"] if receipt["cost_usd"] is not None else "unknown")
    return receipt, file

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)
    s = sub.add_parser("start")
    s.add_argument("task", nargs="?", help="TASK-####; omit only for a local TEST receipt")
    s.add_argument("--agent", required=True, choices=("claude", "codex"))
    h = sub.add_parser("hook")
    h.add_argument("--agent", required=True, choices=("claude", "codex"))
    h.add_argument("--statusline", action="store_true")
    f = sub.add_parser("finish")
    f.add_argument("--manual-cost-usd", type=float)
    r = sub.add_parser("report")
    r.add_argument("--check", action="store_true")
    sub.add_parser("diagnose", help="Show privacy-safe local hook/session health")
    sub.add_parser("abort", help="Discard stale tracking without writing a receipt")
    done = sub.add_parser("complete", help="Commit tracked tokens with staged task code")
    done.add_argument("--message", required=True, help="Task commit subject")
    done.add_argument("--push", action="store_true", help="Push current task branch to origin")
    done.add_argument("--no-summary", action="store_true", help="Keep generated reports main-only for worktree runner")
    imp = sub.add_parser("import-codex", help="Import Codex exec --json token usage from a local JSONL file")
    imp.add_argument("path")
    imp.add_argument("--model", help="Codex model slug (required for pricing if not detected)")
    try:
        run(p.parse_args())
        return 0
    except (OSError, ValueError, TypeError, KeyError) as exc:
        print("agent costs:", exc, file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
