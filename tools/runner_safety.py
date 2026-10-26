"""Safety guards shared by local execution and its tests. No side effects."""
from pathlib import Path
import re

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".bmp",
             ".tif", ".tiff", ".ico", ".aseprite", ".ase", ".psd", ".exr", ".avif"}
TEXT_EXT = {".md", ".json", ".py", ".gd", ".tscn", ".tres", ".godot",
            ".cfg", ".ini", ".txt", ".yaml", ".yml", ".toml", ".ps1",
            ".sh", ".uid", ".csv", ".tsv"}
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

def is_request_record(path, *, directory=False):
    p = normalize(path)
    if p == ".agents/graphics/QUEUE.md":
        return True
    base = ".agents/graphics/requests"
    return (directory and p == base) or (
        p.startswith(base + "/") and Path(p).suffix.lower() in {".md", ".json"})


def is_binary_path(path):
    # Fail closed for unknown formats; directory touches are checked on actual changes.
    return Path(normalize(path)).suffix.lower() not in TEXT_EXT


def is_art(path):
    p = normalize(path)
    return Path(p).suffix.lower() in IMAGE_EXT or (p.startswith(".agents/graphics/") and not is_request_record(p, directory=True)) or p.startswith(".agents/planner/goals/") or "/parts/" in p

def touches(raw):
    paths = [normalize(x.strip()) for x in raw.split(",") if x.strip()]
    if not paths or len(paths) != len(set(paths)):
        raise ValueError("Explicit nonduplicate touches required")
    for path in paths:
        if any(c in path for c in "*?[]") or is_art(path) or (is_generated(path) and not is_request_record(path)) or (Path(path).suffix and is_binary_path(path)) or path.startswith(("scenes/ui","tools/generate_character","tools/repaint_")):
            raise ValueError("No art or generated boards in coding touches: " + path)
        if not path.startswith(ALLOWED_PREFIXES) and not is_request_record(path, directory=True):
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
        if (is_generated(path) and not is_request_record(path)) or is_art(path) or is_binary_path(path) or path in ("AGENTS.md", "project.godot"):
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
    if argv[i:i+1] == ["tools/run_tests.py"]:
        rest = argv[i+1:]
        if rest and len(rest) % 2 == 0 and all(
                rest[n] == "--only" and rest[n+1] in {"map_layers", "map_factory", "godot_map_smoke"}
                for n in range(0, len(rest), 2)):
            return argv
        raise ValueError("Only allowlisted router tests permitted")
    if argv[i:i+2] != ["-m","unittest"]:
        raise ValueError("Only unittest task commands allowed")
    if any(x in argv for x in (";", "&&", "|", ">", "<")):
        raise ValueError("No shell operators")
    if len(argv)>12:
        raise ValueError("Test command too broad")
    return argv

TEST_MODULE=re.compile(r"tools[./\\]tests[./\\](test_\w+?)(?:\.py)?((?:\.[A-Za-z_]\w*)*)")

def normalize_test(argv):
    """tools/tests modules import their siblings (from test_map_factory import ...), which
    only resolves under `discover -s tools/tests`; rewrite a dotted or path module target
    (tools.tests.test_x[.Class[.method]]) into that form, keeping flags and narrowing via -k."""
    argv=list(argv)
    if "unittest" not in argv:
        return argv
    i=argv.index("unittest")+1
    rest=argv[i:]
    targets=[a for a in rest if not a.startswith("-")]
    match=TEST_MODULE.fullmatch(targets[0]) if len(targets)==1 else None
    if match is None:
        return argv
    out=argv[:i]+["discover","-s","tools/tests","-p",match.group(1)+".py"]
    out+=[a for a in rest if a.startswith("-")]
    if match.group(2):
        out+=["-k",match.group(2)[1:]]
    return out

def normalize_test_text(text):
    """Stored task form of normalize_test; non-unittest commands are returned unchanged."""
    smoke = "Godot smoke tools/map_factory_godot_smoke.gd"
    if text == smoke:
        return "py -3 tools/run_tests.py --only godot_map_smoke"
    if text.endswith(" and " + smoke):
        prefix = text[:-(len(smoke) + 5)]
        if prefix == "py -3 -m unittest tools.tests.test_map_layers":
            return "py -3 tools/run_tests.py --only map_layers --only godot_map_smoke"
        if prefix == "py -3 -m unittest tools.tests.test_map_factory tools.tests.test_map_layers":
            return "py -3 tools/run_tests.py --only map_factory --only map_layers --only godot_map_smoke"
    try:
        argv=safe_test(text.split())
    except (ValueError, IndexError):
        return text
    return " ".join(normalize_test(argv))

def supervised_problems(cfg, root):
    """Why this planner config may not enable execution. Empty list means consistent.

    execution_enabled needs supervised_e2e_passed, which needs runner-written evidence
    (agent_runner.py --supervised records it after post-merge validation) naming a task
    whose canonical file is done. Owners should never set supervised_e2e_passed by hand."""
    problems=[]
    if cfg.get("execution_enabled") and not cfg.get("supervised_e2e_passed"):
        problems.append("execution_enabled requires supervised_e2e_passed")
    if not cfg.get("supervised_e2e_passed"):
        return problems
    evidence=cfg.get("supervised_e2e")
    if not isinstance(evidence,dict):
        return problems+["supervised_e2e_passed requires runner evidence in supervised_e2e"]
    task=str(evidence.get("task",""))
    if not re.fullmatch(r"TASK-\d{4}",task):
        problems.append("supervised_e2e.task must be TASK-####")
    if not re.fullmatch(r"[0-9a-f]{40}",str(evidence.get("merge_sha",""))):
        problems.append("supervised_e2e.merge_sha must be a full commit SHA")
    if evidence.get("agent") not in ("claude","codex"):
        problems.append("supervised_e2e.agent must be claude or codex")
    if not evidence.get("verified_at"):
        problems.append("supervised_e2e.verified_at missing")
    if re.fullmatch(r"TASK-\d{4}",task):
        files=sorted((Path(root)/".agents/tasks").glob(task+"_*.md"))
        text=files[0].read_text(encoding="utf-8") if files else ""
        if not re.search(r"(?m)^status: done$",text):
            problems.append("supervised_e2e.task "+task+" is not done")
    return problems

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
