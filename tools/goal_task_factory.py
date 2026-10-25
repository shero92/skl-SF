#!/usr/bin/env python3
"""Evidence-first four-times-daily task queue for Map Factory. No AI calls."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo

ROOT = Path(os.environ.get("SKL_PLANNER_ROOT", Path(__file__).resolve().parents[1]))
BASE = ROOT / ".agents/planner"
TASKS = ROOT / ".agents/tasks"
ZONE = ZoneInfo("Europe/Berlin")
PRIORITIES = {"critical": 0, "high": 1, "normal": 2, "low": 3}
KINDS = ("bug", "test", "feature", "architecture", "investigation", "art")
MAX_NEW_PER_DAY = 3

def read(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.read_text(encoding="utf-8") != data:
        path.write_text(data, encoding="utf-8")

def target(path, line=None):
    if not isinstance(path, str) or not path or Path(path).is_absolute():
        raise ValueError("Need repository-relative file path")
    resolved = (ROOT / path).resolve()
    if not resolved.is_relative_to(ROOT.resolve()) or ".git" in Path(path).parts:
        raise ValueError("Unsafe path " + path)
    if line is not None:
        if type(line) is not int or line <= 0:
            raise ValueError("Line must be positive")
        p = ROOT / path
        if p.is_file() and line <= len(p.read_text(encoding="utf-8").splitlines()):
            return path, str(line)
        return path, "unverified (inspect source)"
    return path, "unspecified"

def records():
    result = {}
    for p in sorted(TASKS.glob("TASK-*.md")):
        raw = p.read_text(encoding="utf-8")
        fields = {}
        if raw.startswith("---\n"):
            for x in raw.split("---", 2)[1].splitlines():
                if ":" in x:
                    k, v = x.split(":", 1)
                    fields[k.strip()] = v.strip()
        if re.fullmatch(r"TASK-\d{4}", fields.get("id", "")):
            result[fields["id"]] = {"path": p, "raw": raw, **fields}
    return result

def route(spec):
    if spec.get("agent") in ("claude", "codex", "specialist"):
        return spec["agent"]
    if spec.get("kind") == "art":
        return "specialist"
    if spec.get("kind") in ("architecture", "investigation") or spec.get("complexity") == "high":
        return "claude"
    return "codex"

def deps(spec):
    value = spec.get("depends_on", [])
    if isinstance(value, str):
        value = value.split(",")
    return [x.strip() for x in value if x.strip() and x.strip() != "none"]

def sources():
    choices = []
    for p in sorted((BASE / "requests").glob("REQ-*.json")):
        req = read(p)
        if req.get("status", "open") == "open":
            choices.append(("request:" + p.stem, req))
    goals = read(BASE / "goals.json", {"goals": []}).get("goals", [])
    for goal in goals:
        if goal.get("status") != "active":
            continue
        for step in goal.get("steps", []):
            entry = dict(step)
            entry["goal_id"] = goal["id"]
            choices.append(("goal:" + goal["id"] + ":" + step["key"], entry))
    return sorted(choices, key=lambda v: (
        PRIORITIES.get(v[1].get("priority", "normal"), 2),
        0 if v[0].startswith("request:") else 1, v[0]))

def create(source, spec, existing, today):
    for k in ("title", "problem", "file", "done_when", "test"):
        if not isinstance(spec.get(k), str) or not spec[k].strip():
            raise ValueError(source + " missing " + k)
    if spec.get("kind", "feature") not in KINDS:
        raise ValueError("Unknown task kind")
    path, line = target(spec["file"], spec.get("line"))
    dependencies = deps(spec)
    missing = [d for d in dependencies if d not in existing]
    if missing:
        raise ValueError(source + " refers to missing dependencies " + ",".join(missing))
    ready = all(existing[d]["status"] == "done" for d in dependencies)
    agent = route(spec)
    state = "todo" if ready and agent != "specialist" else "blocked"
    used = {int(x[-4:]) for x in existing}
    num = next(i for i in range(1, 10000) if i not in used)
    task_id = "TASK-" + f"{num:04d}"
    title = re.sub(r"[\r\n]+", " ", spec["title"]).strip()
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:50] or "work"
    file = TASKS / (task_id + "_" + slug + ".md")
    limit = 30000 if agent == "claude" else 12000
    prompt = ("Outcome: " + spec["done_when"] + ". Evidence: " + spec["problem"]
              + ". Target: " + path + " (line " + line + "). Verify with: " + spec["test"]
              + ". Read AGENTS.md and this task, then only the target file. "
              "Verify the issue and location before changing code. Work only within Map Factory. "
              "Never generate artwork. Stop when evidence is missing. Commit the task, token receipt "
              "and summary on a PR branch, never main.")
    content = "\n".join([
        "---", "id: " + task_id, "status: " + state, "owner: unassigned",
        "branch: none", "depends_on: " + (",".join(dependencies) or "none"),
        "issue: none", "art_request: none", "---", "# " + title, "",
        "**Source:** " + source, "**Created:** " + today,
        "**Goal:** " + spec.get("goal_id", "manual request"),
        "**Type:** " + spec.get("kind", "feature"),
        "**Priority:** " + spec.get("priority", "normal"),
        "**Suggested agent:** " + agent + " (routing heuristic, not a performance claim)",
        "**File:** " + path, "**Line:** " + line,
        "**Problem:** " + spec["problem"], "", "## Acceptance",
        "- [ ] " + spec["done_when"], "- [ ] Test: " + spec["test"],
        "- [ ] PR and observed test evidence.", "", "## Agent prompt",
        prompt, "", "## Budget", "- Aim below " + str(limit)
        + " tokens; context estimate, not enforced cap.",
        "- Read only targeted files, then expand if necessary.", "",
        "## Evidence / handoff", "- Changed files: none.",
        "- Tests: not run.", "- PR: none.", "- Next: claim task after checking blockers.", ""
    ])
    save(file, content)
    existing[task_id] = {"path": file, "raw": content, "status": state,
                         "depends_on": ",".join(dependencies) or "none"}
    return task_id

def goal_done(goal, tasks):
    if goal.get("status") != "active" or goal.get("final_verified") is not True:
        return False
    ids = list(goal.get("task_ids", []))
    # Every milestone step must have an actual TASK record; no premature
    # success when the daily planner has not generated future steps yet.
    for step in goal.get("steps", []):
        marker = "**Source:** goal:" + goal["id"] + ":" + step["key"]
        matches = [i for i, row in tasks.items() if marker in row["raw"]]
        if len(matches) != 1:
            return False
        ids.extend(matches)
    ids = list(dict.fromkeys(ids))
    return bool(ids) and all(
        i in tasks and tasks[i]["status"] == "done" and
        re.search(r"(?m)^- PR: https://", tasks[i]["raw"]) for i in ids)

def pulse(day=None):
    now = (datetime.fromisoformat(day).replace(tzinfo=ZONE) if day else datetime.now(ZONE))
    today = now.strftime("%Y-%m-%d")
    tasks = records()
    known = {m.group(1) for r in tasks.values()
             if (m := re.search(r"(?m)^\*\*Source:\*\* (.+)$", r["raw"]))}
    count = sum("**Created:** " + today in x["raw"] for x in tasks.values())
    new = []
    for source, spec in sources():
        if source in known or count >= MAX_NEW_PER_DAY:
            continue
        new.append(create(source, spec, tasks, today))
        count += 1
        known.add(source)
    goals = read(BASE / "goals.json", {"goals": []}).get("goals", [])
    active = [g for g in goals if g.get("status") == "active"]
    done = [g for g in active if goal_done(g, tasks)]
    available = [i for i, rec in tasks.items() if rec["status"] == "todo" and all(
        d in tasks and tasks[d]["status"] == "done" for d in deps(rec))]
    lines = ["# Task analysis — " + today, "", "No AI/paid tokens used for this scan.",
             "Four daily checks; only 3 new tasks/day to limit costs.", "",
             "## Long-term goals"]
    lines += ["- " + g["id"] + ": " + g["title"] + (" [verified complete]" if g in done else " [in progress]")
              for g in active] or ["- No active long-term goal; configure goals.json."]
    lines += ["", "## Newly generated tasks"]
    lines += ["- " + n for n in new] or ["- None"]
    lines += ["", "## Ready tasks (maximum 3 shown)"]
    lines += ["- " + i + ": " + tasks[i]["path"].name for i in sorted(available)[:3]] or ["- None"]
    lines += ["", "## Blocked tasks"]
    lines += ["- " + i for i, rec in tasks.items() if rec["status"] == "blocked"] or ["- None"]
    lines += ["", "## Verified complete goals"]
    lines += ["- " + g["id"] + ": " + g["title"] for g in done] or ["- None"]
    lines += ["", "Updated: " + now.strftime("%Y-%m-%d %H:%M %Z"),
              "No code or artwork is generated by this planner.", ""]
    save(BASE / "daily" / (today + ".md"), "\n".join(lines))
    return {"created": new, "ready": sorted(available)[:3], "completed":
            [{"id": g["id"], "title": g["title"]} for g in done]}

def request(args):
    spec = {"status": "open", "title": args.title, "problem": args.problem,
            "file": args.file, "line": args.line, "done_when": args.done_when,
            "test": args.test, "priority": args.priority, "kind": args.kind,
            "agent": args.agent}
    target(args.file, args.line)
    blob = json.dumps(spec, ensure_ascii=False, sort_keys=True)
    ident = hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]
    p = BASE / "requests" / ("REQ-" + ident + ".json")
    save(p, json.dumps(spec, ensure_ascii=False, indent=2) + "\n")
    print(p.relative_to(ROOT).as_posix())

def claim(args):
    tasks = records()
    r = tasks.get(args.task)
    if not r or r["status"] != "todo" or r.get("owner") != "unassigned":
        raise ValueError("Task missing, blocked, or already claimed")
    if any(d not in tasks or tasks[d]["status"] != "done" for d in deps(r)):
        raise ValueError("Task dependencies not done")
    if args.branch in ("main", "master") or not re.fullmatch(r"[a-zA-Z0-9_./-]+", args.branch):
        raise ValueError("Task requires a dedicated branch")
    body = r["raw"].replace("status: todo", "status: in_progress", 1)
    body = body.replace("owner: unassigned", "owner: " + args.agent, 1)
    body = body.replace("branch: none", "branch: " + args.branch, 1)
    save(r["path"], body)
    print("Claimed " + args.task + " for " + args.agent)

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("pulse")
    run.add_argument("--date", help="YYYY-MM-DD")
    req = sub.add_parser("request")
    for k in ("title", "problem", "file", "done-when", "test"):
        req.add_argument("--" + k, required=True)
    req.add_argument("--line", type=int)
    req.add_argument("--kind", choices=KINDS, default="bug")
    req.add_argument("--priority", choices=list(PRIORITIES), default="normal")
    req.add_argument("--agent", choices=("auto", "claude", "codex", "specialist"), default="auto")
    cl = sub.add_parser("claim")
    cl.add_argument("task")
    cl.add_argument("--agent", choices=("claude", "codex"), required=True)
    cl.add_argument("--branch", required=True)
    pro = sub.add_parser("prompt")
    pro.add_argument("task")
    sub.add_parser("completed")
    args = p.parse_args()
    try:
        if args.cmd == "pulse":
            print(json.dumps(pulse(args.date), ensure_ascii=False))
        elif args.cmd == "request":
            request(args)
        elif args.cmd == "claim":
            claim(args)
        elif args.cmd == "prompt":
            r = records().get(args.task)
            if not r:
                raise ValueError("Unknown task")
            m = re.search(r"## Agent prompt\n(.+?)(?:\n\n|\Z)", r["raw"], re.S)
            print(m.group(1) if m else "Read AGENTS.md and " + r["path"].relative_to(ROOT).as_posix()
                  + "; validate relevant files and tests, then report cost receipts.")
        else:
            rows = records()
            goals = read(BASE / "goals.json", {"goals": []}).get("goals", [])
            print(json.dumps([{"id": g["id"], "title": g["title"]}
                              for g in goals if goal_done(g, rows)]))
        return 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as e:
        print("task factory:", e, file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
