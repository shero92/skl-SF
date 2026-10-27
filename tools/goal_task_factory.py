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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runner_safety import is_art, is_binary_path, normalize, normalize_test_text, touches as validate_touches  # noqa: E402

ROOT =Path(os.environ.get("SKL_PLANNER_ROOT", Path(__file__).resolve().parents[1]))
BASE = ROOT / ".agents/planner"
TASKS = ROOT / ".agents/tasks"
ZONE = ZoneInfo("Europe/Berlin")
PRIORITIES = {"critical": 0, "high": 1, "normal": 2, "low": 3}
KINDS = ("bug", "test", "feature", "architecture", "investigation", "refactor", "art")
MAX_NEW_PER_DAY = 3  # default when config.json sets no max_new_tasks_per_day
DEPENDENCY_BLOCK = "**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)"
SPECIALIST_BLOCK = "**Blocked by:** specialist step"  # never promoted by the pulse


def specialist_blockers(spec, dependencies, existing):
    """The real requirements a specialist step waits on, recorded in its task instead of a bare status."""
    reqs = ["a calibration/graphics specialist performs it (coding runners never claim it)"]
    reqs += [d + " is " + existing[d]["status"] for d in dependencies if existing[d]["status"] != "done"]
    if spec.get("new_graphics_required"):
        reqs.append("new graphics need an art request in .agents/graphics/requests/, independent visual review and owner approval")
    if isinstance(spec.get("source_gate_note"), str) and spec["source_gate_note"].strip():
        reqs.append(re.sub(r"[\r\n]+", " ", spec["source_gate_note"]).strip())
    return SPECIALIST_BLOCK + " — requires: " + "; ".join(reqs)

def read(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

def daily_cap():
    """New tasks per day: config max_new_tasks_per_day, null meaning no daily cap."""
    cfg = read(BASE / "config.json", {}) or {}
    if "max_new_tasks_per_day" not in cfg:
        return MAX_NEW_PER_DAY
    value = cfg["max_new_tasks_per_day"]
    return None if value is None else int(value)

def reserved_ids():
    """Task IDs promised to goal steps (task_id/proposed_task_id), incl. a proposed revision."""
    out = set()
    for goal in read(BASE / "goals.json", {"goals": []}).get("goals", []):
        steps = list(goal.get("steps", [])) + list((goal.get("proposed_revision") or {}).get("steps", []))
        for step in steps:
            for key in ("task_id", "proposed_task_id"):
                if re.fullmatch(r"TASK-\d{4}", str(step.get(key, ""))):
                    out.add(step[key])
    return out

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.read_text(encoding="utf-8") != data:
        path.write_text(data, encoding="utf-8", newline="\n")

def target(path, line=None):
    if not isinstance(path, str) or not path or Path(path).is_absolute():
        raise ValueError("Need repository-relative file path")
    path = normalize(path)
    if is_art(path) or is_binary_path(path):
        raise ValueError("Forbidden artwork/binary target " + path)
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
        state = read(BASE / "goals" / goal["id"] / "state.json", {})
        if state.get("status") != "active" or state.get("milestones_approved") is not True:
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
    # Store a test command the runner can execute as written (tools/tests needs discover).
    spec = {**spec, "test": normalize_test_text(spec["test"])}
    path, line = target(spec["file"], spec.get("line"))
    if "touches" in spec:
        validate_touches(",".join(spec["touches"]))
    dependencies = deps(spec)
    missing = [d for d in dependencies if d not in existing]
    if missing:
        raise ValueError(source + " refers to missing dependencies " + ",".join(missing))
    ready = all(existing[d]["status"] == "done" for d in dependencies)
    agent = route(spec)
    state = "todo" if ready and agent != "specialist" else "blocked"
    # Keep the ID the plan promised; never hand another step's reserved ID to a new task.
    wanted = spec.get("proposed_task_id")
    if isinstance(wanted, str) and re.fullmatch(r"TASK-\d{4}", wanted) and wanted not in existing:
        task_id = wanted
    else:
        used = {int(x[-4:]) for x in existing} | {int(x[-4:]) for x in reserved_ids()}
        task_id = "TASK-" + f"{next(i for i in range(1, 10000) if i not in used):04d}"
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
        "branch: none", "agent: " + ("graphics" if agent == "specialist" else agent),
        "touches: " + ",".join(spec.get("touches", [path])),
        "test: " + spec["test"], "done_when: " + spec["done_when"],
        "started_at: unknown", "cost_usd: unknown",
        "depends_on: " + (",".join(dependencies) or "none"),
        "issue: none", "art_request: none", "---", "# " + title, "",
        "**Source:** " + source, "**Created:** " + today,
        "**Goal:** " + spec.get("goal_id", "manual request"),
        "**Type:** " + spec.get("kind", "feature"),
        "**Priority:** " + spec.get("priority", "normal"),
        "**Suggested agent:** " + agent + " (routing heuristic, not a performance claim)",
        "**File:** " + path, "**Line:** " + line,
        "**Problem:** " + spec["problem"],
        *([DEPENDENCY_BLOCK] if state == "blocked" and agent != "specialist" and not ready else []),
        *([specialist_blockers(spec, dependencies, existing)] if agent == "specialist" else []),
        "", "## Acceptance",
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
        matches = [i for i, row in tasks.items() if marker + "\n" in row["raw"]]
        if not matches and step.get("task_id") in tasks:
            matches = [step["task_id"]]
        if len(matches) != 1:
            return False
        ids.extend(matches)
    ids = list(dict.fromkeys(ids))
    return bool(ids) and all(
        i in tasks and tasks[i]["status"] == "done" and
        re.search(r"(?m)^- PR: https://", tasks[i]["raw"]) for i in ids)

def pulse(day=None, max_new=None):
    now = (datetime.fromisoformat(day).replace(tzinfo=ZONE) if day else datetime.now(ZONE))
    today = now.strftime("%Y-%m-%d")
    tasks = records()
    known = {m.group(1) for r in tasks.values()
             if (m := re.search(r"(?m)^\*\*Source:\*\* (.+)$", r["raw"]))}
    count = sum("**Created:** " + today in x["raw"] for x in tasks.values())
    by_source = {m.group(1): i for i, r in tasks.items()
                 if (m := re.search(r"(?m)^\*\*Source:\*\* (.+)$", r["raw"]))}
    cap = daily_cap()
    limit = read(BASE / "config.json", {}).get("max_tasks_per_run", 4)
    if cap is not None:
        limit = min(cap, limit)
    if max_new is not None:
        limit = min(limit, max_new)
    # Tasks that waited only on dependencies become claimable as soon as those are done.
    promoted = []
    for tid, rec in tasks.items():
        if rec.get("status") == "blocked" and DEPENDENCY_BLOCK in rec["raw"] and all(
                d in tasks and tasks[d].get("status") == "done" for d in deps(rec)):
            raw = re.sub(r"(?m)^status: blocked$", "status: todo", rec["raw"], count=1)
            raw = raw.replace(DEPENDENCY_BLOCK, "**Blocked by:** none (dependencies done; promoted on " + today + ")", 1)
            save(rec["path"], raw)
            rec.update(raw=raw, status="todo")
            promoted.append(tid)
    # Migrate only exact, unambiguous milestone annotations in older AI tasks.
    for source, spec in sources():
        if source.startswith("goal:") and source not in by_source:
            matches = [tid for tid, rec in tasks.items()
                       if "**Goal:** " + spec["goal_id"] + "\n" in rec["raw"]
                       and re.search(r"(?m)^\*\*Problem:\*\* .*\(goal step "
                                     + re.escape(spec["key"]) + r"\)", rec["raw"])]
            recorded = spec.get("task_id")
            if recorded in tasks and recorded not in matches:
                matches.append(recorded)
            if len(matches) == 1:
                by_source[source] = matches[0]
                known.add(source)
    new, refused = [], []
    for source, spec in sources():
        if source in known or (cap is not None and count >= cap) or len(new) >= limit:
            continue
        if spec.get("task_id") and spec["task_id"] not in tasks:
            continue  # reserved by a task record on an unmerged branch; it arrives with that merge
        # Milestone order: create a step only after every "after" step has a done task.
        after = ["goal:" + spec["goal_id"] + ":" + k for k in spec.get("after", [])] if "goal_id" in spec else []
        after_ids = [by_source.get(a) for a in after]
        if any(i is None or tasks[i]["status"] != "done" for i in after_ids):
            continue
        if after_ids:
            spec = {**spec, "depends_on": list(dict.fromkeys(deps(spec) + after_ids))}
        try:
            task_id = create(source, spec, tasks, today)
        except ValueError as exc:
            # One invalid step is refused and reported; it must not stop the independent tasks.
            refused.append({"source": source, "error": str(exc)})
            print("task factory: refused " + source + ": " + str(exc), file=sys.stderr)
            continue
        by_source[source] = task_id
        new.append(task_id)
        count += 1
        known.add(source)
    goals = read(BASE / "goals.json", {"goals": []}).get("goals", [])
    for goal in goals:
        for step in goal.get("steps", []):
            tid = by_source.get("goal:" + goal["id"] + ":" + step["key"])
            if tid:
                step["task_id"] = tid
    if (BASE / "goals.json").is_file():
        data = read(BASE / "goals.json")
        data["goals"] = goals
        save(BASE / "goals.json", json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    active = [g for g in goals if g.get("status") == "active"]
    done = [g for g in active if goal_done(g, tasks)]
    available = [i for i, rec in tasks.items() if rec["status"] == "todo" and all(
        d in tasks and tasks[d]["status"] == "done" for d in deps(rec))]
    lines = ["# Task analysis — " + today, "", "No AI/paid tokens used for this scan.",
             "Daily cap on new tasks: " + ("none (runners work until usage limits)" if cap is None
                                           else str(cap)) + "; " + str(limit) + " per pulse.", "",
             "## Long-term goals"]
    lines += ["- " + g["id"] + ": " + g["title"] + (" [verified complete]" if g in done else " [in progress]")
              for g in active] or ["- No active long-term goal; configure goals.json."]
    lines += ["", "## Newly generated tasks"]
    lines += ["- " + n for n in new] or ["- None"]
    lines += ["", "## Refused steps (fix the spec; nothing was created)"]
    lines += ["- " + r["source"] + ": " + r["error"] for r in refused] or ["- None"]
    lines += ["", "## Promoted to todo (dependencies done)"]
    lines += ["- " + n for n in promoted] or ["- None"]
    lines += ["", "## Ready tasks (maximum 3 shown)"]
    lines += ["- " + i + ": " + tasks[i]["path"].name for i in sorted(available)[:3]] or ["- None"]
    lines += ["", "## Blocked tasks"]
    lines += ["- " + i for i, rec in tasks.items() if rec["status"] == "blocked"] or ["- None"]
    lines += ["", "## Verified complete goals"]
    lines += ["- " + g["id"] + ": " + g["title"] for g in done] or ["- None"]
    lines += ["", "Updated: " + now.strftime("%Y-%m-%d %H:%M %Z"),
              "No code or artwork is generated by this planner.", ""]
    save(BASE / "daily" / (today + ".md"), "\n".join(lines))
    return {"created": new, "refused": refused, "promoted": promoted, "ready": sorted(available)[:3], "completed":
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
    active = [t for t in tasks.values() if t["status"] == "in_progress"]
    def overlap(a, b):
        return a == b or a.rstrip("/") + "/" == b[:len(a.rstrip("/"))+1] or b.rstrip("/") + "/" == a[:len(b.rstrip("/"))+1]
    my_paths = [p.strip() for p in r["touches"].split(",")]
    for current in active:
        if current.get("agent") == args.agent:
            raise ValueError("Agent already has an active task")
        if any(overlap(p, q) for p in my_paths for q in current["touches"].split(",")):
            raise ValueError("Touch conflict with " + current["id"])
    if r.get("agent") != args.agent:
        raise ValueError("Task routed to another agent")
    if args.branch in ("main", "master") or not re.fullmatch(r"[a-zA-Z0-9_./-]+", args.branch):
        raise ValueError("Task requires a dedicated branch")
    body = r["raw"].replace("status: todo", "status: in_progress", 1)
    body = body.replace("owner: unassigned", "owner: " + args.agent, 1)
    body = body.replace("branch: none", "branch: " + args.branch, 1)
    body = body.replace("started_at: unknown", "started_at: " + datetime.now(ZONE).isoformat(), 1)
    save(r["path"], body)
    print("Claimed " + args.task + " for " + args.agent)


# Local read-only LLM proposals are untrusted data, never commands.
def apply_proposal(payload, run_key):
    """Validate an entire proposal before any file write."""
    if not isinstance(payload, dict) or set(payload) != {"tasks", "updates"} or not isinstance(payload["tasks"], list) or not isinstance(payload["updates"], list):
        raise ValueError("Proposal needs tasks[] and updates[] only")
    if len(payload["tasks"]) > 4 or len(payload["updates"]) > 12:
        raise ValueError("Exceeded per-run limits")
    current = records()
    sources_seen = {m.group(1) for x in current.values()
                    if (m := re.search(r"(?m)^\*\*Source:\*\* (.+)$", x["raw"]))}
    pending = []
    for t in payload["tasks"]:
        required = {"title", "problem", "file", "done_when", "test", "priority", "kind", "agent", "depends_on"}
        if not isinstance(t, dict) or not required <= set(t) or (set(t) - (required | {"line", "touches", "goal_id"})):
            raise ValueError("Invalid task fields")
        if any(not isinstance(t[k], str) or not 1 <= len(t[k]) <= 500 for k in ("title", "problem", "done_when", "test")):
            raise ValueError("Invalid task text")
        goal_id = t.get("goal_id")
        if goal_id:
            if not re.fullmatch(r"GOAL-\d{4}", goal_id):
                raise ValueError("Invalid GOAL ID")
            state = read(BASE / "goals" / goal_id / "state.json", {})
            if state.get("status") != "active" or state.get("milestones_approved") is not True:
                raise ValueError("Goal milestones must be reviewed/approved before task creation")
        file, line = target(t["file"], t.get("line"))
        if not (ROOT / file).is_file() or file.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif")):
            raise ValueError("Task must target existing source file, not artwork")
        if not (file.startswith(("map_factory/", "tools/", ".agents/")) or file in ("project.godot", "scenes/map_factory_preview.gd", "scenes/map_factory_preview.tscn")):
            raise ValueError("Outside approved code scope")
        if any(bad in file.lower() for bad in ("/characters/", "/ui/", "generate_character", "repaint_", "/portraits/")):
            raise ValueError("Excluded characters, interface or art")
        if t["kind"] not in ("bug", "test", "feature", "architecture", "investigation", "refactor") or t["agent"] not in ("claude", "codex"):
            raise ValueError("Only coding tasks for coding agents")
        if t["priority"] not in PRIORITIES or not isinstance(t["depends_on"], list) or any(not re.fullmatch(r"TASK-\d{4}", d) for d in t["depends_on"]):
            raise ValueError("Bad priority/dependencies")
        if any(d not in current for d in t["depends_on"]):
            raise ValueError("Unknown task dependency")
        touches = t.get("touches", [file])
        if not isinstance(touches, list) or not touches:
            raise ValueError("Missing touches")
        validate_touches(",".join(touches))
        fingerprint = hashlib.sha256((file + "|" + t["problem"].strip().casefold()).encode()).hexdigest()[:16]
        source = "ai:" + fingerprint
        if source not in sources_seen:
            pending.append((source, t, touches))
            sources_seen.add(source)
    updates = []
    for u in payload["updates"]:
        if not isinstance(u, dict) or set(u) != {"task_id", "status", "reason", "depends_on"}:
            raise ValueError("Bad update schema")
        tid = u["task_id"]
        if tid not in current or current[tid]["status"] not in ("todo", "blocked") or u["status"] not in ("todo", "blocked"):
            raise ValueError("Cannot change claimed/completed tasks")
        if not isinstance(u["reason"], str) or not 5 <= len(u["reason"]) <= 500:
            raise ValueError("Missing update evidence")
        if not isinstance(u["depends_on"], list) or any(d not in current or d == tid for d in u["depends_on"]):
            raise ValueError("Bad dependency update")
        if u["status"] == "todo" and any(current[d]["status"] != "done" for d in u["depends_on"]):
            raise ValueError("Dependencies not done")
        updates.append(u)
    today = datetime.now(ZONE).strftime("%Y-%m-%d")
    count = sum("**Created:** " + today in x["raw"] for x in current.values())
    cap = min(4, read(BASE / "config.json", {}).get("max_tasks_per_run", 4))
    # Pulse-created tasks and AI extras share the run and daily budgets.
    used = read(BASE / "runs" / (run_key + "-pulse.json"), {}).get("created", [])
    daily = daily_cap()
    room = len(pending) if daily is None else daily - count
    pending = pending[:max(0, min(room, cap - len(used)))]
    created = []
    for source, t, touches in pending:
        task_id = create(source, t, current, datetime.now(ZONE).strftime("%Y-%m-%d"))
        rec = current[task_id]
        text = rec["raw"] + "\n## Allowed touches\n" + "\n".join("- " + p for p in touches) + "\n"
        save(rec["path"], text)
        created.append(task_id)
    for u in updates:
        rec = current[u["task_id"]]
        text = re.sub(r"(?m)^status: (todo|blocked)$", "status: " + u["status"], rec["raw"], count=1)
        text = re.sub(r"(?m)^depends_on: .+$", "depends_on: " + (",".join(u["depends_on"]) or "none"), text, count=1)
        text += "\n## Planner evidence\n- " + u["reason"].replace("\n", " ") + "\n"
        save(rec["path"], text)
    return {"created": created, "updated": [x["task_id"] for x in updates]}

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
    ap = sub.add_parser("apply-proposal")
    ap.add_argument("json_file")
    ap.add_argument("--run-key", required=True)
    args = p.parse_args()
    try:
        if args.cmd == "pulse":
            print(json.dumps(pulse(args.date), ensure_ascii=False))
        elif args.cmd == "apply-proposal":
            print(json.dumps(apply_proposal(read(Path(args.json_file)), args.run_key)))
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
