"""Safety guards shared by local execution and its tests. No side effects."""
from pathlib import Path
import re

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".bmp",
             ".tif", ".tiff", ".ico", ".aseprite", ".psd", ".exr", ".avif"}
GENERATED_NAMES = {"INDEX.md", "FILES.md", "TASKS.md", "ACTIVE.md",
                   "QUEUE.md", "summary.md", "summary.json"}
FORBIDDEN_PARTS = {"characters", "ui", "portraits", "gameplay"}
ALLOWED_PREFIXES = ("map_factory/", "tools/", "scenes/map_factory_preview.")

def normalize(path):
    if not isinstance(path, str) or not path:
        raise ValueError("Empty path")
    value = path.replace("\\", "/").strip("/")
    parts = value.split("/")
    if path.startswith(("/", "\\")) or ":" in value or ".." in parts or "." in parts or any(not x for x in parts):
        raise ValueError("Unsafe path: " + str(path))
    return value

def is_generated(path):
    p = normalize(path)
    return p.split("/")[-1] in GENERATED_NAMES or p.startswith(".agents/project/")

def is_art(path):
    p = normalize(path)
    return Path(p).suffix.lower() in IMAGE_EXT or p.startswith((".agents/graphics/", ".agents/planner/goals/")) or "/parts/" in p

def touches(raw):
    paths = [normalize(x.strip()) for x in raw.split(",") if x.strip()]
    if not paths or len(paths) != len(set(paths)):
        raise ValueError("Explicit nonduplicate touches required")
    for path in paths:
        if "*" in path or is_art(path) or is_generated(path) or path.startswith(("scenes/ui","tools/generate_character","tools/repaint_")):
            raise ValueError("No art or generated boards in coding touches: " + path)
        if not path.startswith(ALLOWED_PREFIXES):
            raise ValueError("Outside Map Factory coding scope: " + path)
        if FORBIDDEN_PARTS.intersection(path.lower().split("/")):
            raise ValueError("Character/gameplay/UI path not allowed: " + path)
    return paths

def overlaps(a,b):
    x,y=normalize(a),normalize(b)
    return x==y or x.startswith(y.rstrip("/")+"/") or y.startswith(x.rstrip("/")+"/")

def allowed_changed(changed, authorized):
    auth = [normalize(x) for x in authorized]
    for item in changed:
        path=normalize(item)
        low=path.lower()
        if FORBIDDEN_PARTS.intersection(low.split("/")) or low.startswith(("scenes/ui", "tools/generate_character", "tools/repaint_", "tools/generate_", "map_factory/parts/")):
            raise ValueError("Forbidden gameplay/art path: "+path)
        if is_generated(path) or is_art(path) or path in ("AGENTS.md", "project.godot"):
            raise ValueError("No art or generated/policy file edits: " + path)
        if not any(path==a or path.startswith(a.rstrip("/")+"/") for a in auth):
            raise ValueError("Changed path not in task touches: " + path)
    return True

def verify_claim(task, tasks):
    if task["status"] != "todo" or task["agent"] not in ("claude","codex"):
        raise ValueError("Unclaimable task")
    dependency = [d for d in task["depends_on"].split(",") if d.strip() and d.strip()!="none"]
    if any(d not in tasks or tasks[d]["status"]!="done" for d in dependency):
        raise ValueError("Unfinished task dependency")
    selected=touches(task["touches"])
    for other in tasks.values():
        if other["status"]!="in_progress":
            continue
        if other["agent"]==task["agent"]:
            raise ValueError("Only one active task per agent")
        if any(overlaps(a,b) for a in selected for b in touches(other["touches"])):
            raise ValueError("Touch conflict with active "+other["id"])
    return selected

def safe_test(argv):
    """Prevent task-controlled shell injection and arbitrary test commands."""
    if not isinstance(argv, list) or len(argv)<3:
        raise ValueError("Use explicit Python unittest command arguments")
    executable=Path(argv[0].replace("\\","/")).name.lower()
    if executable not in ("python", "python.exe", "python3", "python3.exe", "py", "py.exe"):
        raise ValueError("Task test command executable not allowed")
    i=1
    if executable.startswith("py") and argv[1]=="-3":
        i=2
    if argv[i:i+2] != ["-m","unittest"]:
        raise ValueError("Only unittest task commands allowed")
    if any(x in argv for x in (";", "&&", "|", ">", "<")):
        raise ValueError("No shell operators")
    if len(argv)>12:
        raise ValueError("Test command too broad")
    return argv

def receipt_goals(receipts, task_source):
    """Aggregate measured per-goal costs without treating unknown as zero."""
    result={}
    for rec in receipts:
        goal=task_source.get(rec.get("task_id"))
        if not goal:
            continue
        row=result.setdefault(goal, {"goal":goal,"input_tokens":0,"output_tokens":0,
             "known_usd":0.0,"unknown_cost_receipts":0,"unknown_token_receipts":0,"receipts":0})
        row["receipts"]+=1
        cost=rec.get("cost_usd")
        if cost is None:
            row["unknown_cost_receipts"]+=1
        else:
            row["known_usd"]+=float(cost)
        usage=rec.get("tokens")
        if usage is None:
            row["unknown_token_receipts"]+=1
        else:
            row["input_tokens"]+=usage.get("input_tokens",0)
            row["output_tokens"]+=usage.get("output_tokens",0)
    for x in result.values():
        x["known_usd"]=round(x["known_usd"],6)
    return sorted(result.values(),key=lambda x:x["goal"])
