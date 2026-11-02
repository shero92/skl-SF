#!/usr/bin/env python3
"""Windows-only local coding executor. DISABLED until supervised end-to-end signoff.

No API keys, no Cloud AI, no arbitrary shell commands from task text.
The local owner's authenticated Claude/Codex CLI is used only when enabled.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
import threading

_BUDGET = threading.local()
_MAIN_STATE = threading.RLock()
_MAIN_DEPTH = threading.local()
_CHILDREN_LOCK = threading.Lock()
_CHILDREN = {}

@contextmanager
def execution_budget(deadline, repair_attempts=1, cancel_event=None):
    """Thread-local absolute monotonic deadline for one coordinated task."""
    previous = getattr(_BUDGET, "value", None)
    _BUDGET.value = (float(deadline), min(1, max(0, int(repair_attempts))), cancel_event)
    try:
        yield
    finally:
        _BUDGET.value = previous

def remaining_timeout(timeout):
    budget = getattr(_BUDGET, "value", None)
    if budget is None:
        return timeout
    if len(budget) > 2 and budget[2] is not None and budget[2].is_set():
        raise RuntimeError("Coordinated execution cancelled")
    left = budget[0] - time.monotonic()
    if left <= 0:
        raise subprocess.TimeoutExpired("session deadline", 0)
    return min(timeout, left)

def cancel_budget(cancel_event):
    """Atomically stop new launches and terminate all trees sharing this cancellation."""
    with _CHILDREN_LOCK:
        cancel_event.set()
        children = list(_CHILDREN.get(cancel_event, ()))
    failures = []
    for child in children:
        try:
            terminate_tree(child)
        except (OSError, subprocess.SubprocessError) as exc:
            failures.append(str(exc))
    return failures


def terminate_tree(proc):
    """Terminate descendants before collecting a timed-out CLI process."""
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, timeout=15, check=False)
    else:
        import signal
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    if proc.poll() is None:
        proc.kill()

def requires_pr(paths):
    """Infrastructure always needs reviewed PRs, including mixed code tasks."""
    return any(normalize(p).startswith(("tools/", ".github/", ".agents/"))
               or normalize(p) in ("AGENTS.md", "project.godot") for p in paths)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runner_safety import MAIN_GENERATED_PATHS, main_generated, allowed_changed, is_art, is_generated, normalize, normalize_test, safe_test, supervised_problems, touches, verify_claim
import agent_file_bridge

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/".agents/planner/config.json"
LOCAL=ROOT/".agents/monitoring/.local"
WORKTREES=ROOT.parent/".skl-sf-worktrees"
IMAGE_GLOBS=["*.[pP][nN][gG]","*.[jJ][pP][gG]","*.[jJ][pP][eE][gG]",
 "*.[wW][eE][bB][pP]","*.[sS][vV][gG]","*.[gG][iI][fF]",
 "*.[bB][mM][pP]","*.[pP][sS][dD]","*.[aA][sS][eE][pP][rR][iI][tT][eE]"]
NO_KEYS=("OPENAI_API_KEY","ANTHROPIC_API_KEY")

def execute(argv,cwd=None,*,input=None,timeout=600,check=True):
    clean=os.environ.copy()
    for key in NO_KEYS:clean.pop(key,None)
    timeout = remaining_timeout(timeout)
    options = dict(cwd=str(cwd or ROOT), text=True, encoding="utf-8",
                   errors="replace", env=clean, shell=False)
    if getattr(_BUDGET, "value", None) is None:
        proc=subprocess.run([str(x) for x in argv], input=input,
                            capture_output=True, timeout=timeout, **options)
    else:
        group = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" else {"start_new_session": True}
        budget = _BUDGET.value
        cancel_event = budget[2] if len(budget) > 2 else None
        # Cancellation and launch/register share a lock: no process escapes the snapshot.
        with _CHILDREN_LOCK:
            timeout = remaining_timeout(timeout)
            child = subprocess.Popen([str(x) for x in argv], stdin=subprocess.PIPE if input is not None else subprocess.DEVNULL,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options, **group)
            if cancel_event is not None:
                _CHILDREN.setdefault(cancel_event, set()).add(child)
        try:
            try:
                stdout, stderr = child.communicate(input=input, timeout=timeout)
            except subprocess.TimeoutExpired:
                terminate_tree(child)
                child.communicate()
                raise
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError("Coordinated execution cancelled")
            proc = subprocess.CompletedProcess(argv, child.returncode, stdout, stderr)
        finally:
            if cancel_event is not None:
                with _CHILDREN_LOCK:
                    children = _CHILDREN.get(cancel_event)
                    if children is not None:
                        children.discard(child)
                        if not children:
                            _CHILDREN.pop(cancel_event, None)
    if check and proc.returncode:
        raise RuntimeError("command failed: "+" ".join(str(x) for x in argv[:3])+" ("+str(proc.returncode)+"): "
                           +(proc.stderr or "").strip()[-300:])
    return proc

def git(*args,cwd=None):
    return execute(["git",*args],cwd).stdout.strip()

def stamp():
    return datetime.now(timezone.utc).isoformat()

def read_json(path,default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

def records(root=None):
    root=root or ROOT
    out={}
    for p in (root/".agents/tasks").glob("TASK-*.md"):
        text=p.read_text(encoding="utf-8")
        if not text.startswith("---\n"):continue
        fm=text.split("---",2)[1]
        info={}
        for line in fm.splitlines():
            if ":" in line:
                k,v=line.split(":",1)
                info[k.strip()]=v.strip()
        if re.fullmatch(r"TASK-\d{4}",info.get("id","")):
            info.update({"file":p,"text":text})
            out[info["id"]]=info
    return out

def amend_status(tid,state,*,reason="",branch=None):
    p=next((ROOT/".agents/tasks").glob(tid+"_*.md"))
    raw=p.read_text(encoding="utf-8")
    raw=re.sub(r"(?m)^status: [^\r\n]+$","status: "+state,raw,count=1)
    if branch:raw=re.sub(r"(?m)^branch: [^\r\n]+$","branch: "+branch,raw,count=1)
    if reason:
        raw += "\n## Runner evidence\n- "+reason[:400].replace("\n"," ")+"\n"
    p.write_text(raw,encoding="utf-8",newline="\n")

MAIN_GENERATED = MAIN_GENERATED_PATHS

def index_main():
    execute([sys.executable,"tools/agent_workflow.py","--write"])
    execute([sys.executable,"tools/generate_project_indexes.py","--write"])
    execute([sys.executable,"tools/agent_costs.py","report"])
    execute([sys.executable,"tools/goal_costs.py","--write"])
    execute([sys.executable,"tools/run_tests.py","--write-index"])

def regenerated(path):
    """Outputs index_main() rebuilds from the tree; safe for the runner to commit on main."""
    return main_generated(path)

def dirty_paths(cwd=None):
    # Parse raw porcelain: git() strips, which would eat the first entry's status column.
    out=execute(["git","status","--porcelain=v1","-z","--untracked-files=all","--no-renames"],cwd).stdout
    return sorted({entry[3:] for entry in out.split("\0") if len(entry)>3})

def main_commit(subject,agent,tid,extra=None,*,verify=False):
    """Regenerate every generated file and commit it with the task records, leaving main clean."""
    index_main()
    allowed=[".agents/tasks/",*(extra or [])]
    changed=dirty_paths()
    stray=[p for p in changed if not (regenerated(p) or any(p==a or p.startswith(a) for a in allowed))]
    if stray:
        raise RuntimeError("Main has non-generated changes; refusing to commit: "+", ".join(stray[:10]))
    if changed:
        if verify:
            execute([sys.executable,"tools/run_tests.py","--changed"],timeout=1800)
        git("add","-A","--",*changed)
        git("commit","-m",subject,"-m","Task-ID: "+tid+"\nAgent: "+agent+"\nCost-USD: unknown")
        git("push","origin","main")
    if dirty_paths():
        raise RuntimeError("Main still dirty after "+subject)

def settle_main(tid,agent):
    """Leave main clean: commit regenerated-only drift, otherwise report what blocks it."""
    if git("branch","--show-current")!="main":
        return "Runner finished off main; check the checkout"
    changed=dirty_paths()
    if not changed:
        return None
    if all(regenerated(p) for p in changed):
        try:
            main_commit("chore: regenerate indexes after "+tid,agent,tid)
            return None
        except RuntimeError as exc:
            return str(exc)
    return "Main left dirty with non-generated changes: "+", ".join(changed[:10])

@contextmanager
def coordination_lock():
    """Serialize canonical main reads and mutations across worker threads/processes."""
    with _MAIN_STATE:
        depth = getattr(_MAIN_DEPTH, "value", 0)
        _MAIN_DEPTH.value = depth + 1
        try:
            if depth:
                yield
            else:
                with _exclusive_file("main-state"):
                    yield
        finally:
            _MAIN_DEPTH.value = depth

@contextmanager
def exclusive(label):
    with coordination_lock():
        yield

@contextmanager
def _exclusive_file(label):
    LOCAL.mkdir(parents=True,exist_ok=True)
    target=LOCAL/(label+".lock")
    # Exclusive create: fail closed on stale lock; owner must examine and clear.
    try:
        fd=os.open(str(target),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        raise RuntimeError("Another operation has lock "+str(target)+"; do not run concurrently")
    try:
        with os.fdopen(fd,"w",newline="\n") as handle:handle.write(str(os.getpid())+" "+stamp())
        yield
    finally:
        target.unlink(missing_ok=True)

def sanitized_session(agent,workdir,tid,timeout,repair_context=None):
    prompt=(
        "Implement "+tid+". Read AGENTS.md and the canonical task. "
        "Modify ONLY its touches paths; no characters, UI, gameplay or art. "
        "Never read, view, inspect or generate PNG/JPG/SVG or other images; "
        "goal reference images are not accessible. "
        "No shell commands, no git commits, no index/dashboard generation. "
        "Leave code changes in the worktree and describe code changes briefly. "
        "Stop if a file outside touches is needed. The runner handles tests, "
        "tokens, merge and rollback.")
    if repair_context:
        prompt += " Fix only the ordinary test failure within existing touches. Diagnostic: " + repair_context[:1200]
    if agent=="claude":
        args=["claude","-p","--permission-mode","acceptEdits","--tools",
              "Read,Edit,Write,Glob,Grep","--disallowedTools","Bash",
              "--strict-mcp-config","--no-chrome","--output-format","json",
              "--effort","low",prompt]
        proc=execute(args,workdir,timeout=timeout,check=False)
        return proc,None
    log=workdir/".agents/monitoring/.local/codex-exec.jsonl"
    log.parent.mkdir(parents=True,exist_ok=True)
    bridge=codex_bridge(workdir,tid)
    prompt+=(" Use ONLY the task_files MCP tools (read_file, write_file, replace_in_file) "
             "with repo-relative paths; reads: "+", ".join(bridge["reads"])+
             "; writes: "+", ".join(bridge["touches"])+".")
    args=["codex","exec","--sandbox","workspace-write","--cd",str(workdir),
          *bridge["config"],"--json","-"]
    proc=execute(args,workdir,input=prompt,timeout=timeout,check=False)
    with log.open("a" if repair_context else "w",encoding="utf-8",newline="\n") as handle:
        handle.write(proc.stdout)
    return proc,log

def codex_bridge(workdir,tid):
    """Preflight the scoped text bridge before launching a Codex worker."""
    task_file=next((Path(workdir)/".agents/tasks").glob(tid+"_*.md"),None)
    if task_file is None:
        raise RuntimeError("Codex file bridge unavailable: task file missing")
    match=re.search(r"(?m)^touches:\s*([^\r\n]*)$",task_file.read_text(encoding="utf-8"))
    allowed=[p.strip() for p in (match.group(1) if match else "").split(",")
             if p.strip() and p.strip()!="none"]
    reads=["AGENTS.md",task_file.relative_to(workdir).as_posix()]
    instruction_paths=("INDEX.md","tools/INDEX.md",".agents/INDEX.md",
                       ".agents/workflows/TASKS.md","map_factory/INDEX.md",
                       "map_factory/MAP_FACTORY_RULES.md")
    reads += [p for p in instruction_paths if (Path(workdir)/p).is_file()]
    problem=agent_file_bridge.preflight(workdir,allowed,reads,"AGENTS.md",timeout=remaining_timeout(30))
    if problem:
        raise RuntimeError("Codex file bridge unavailable: "+problem)
    argv=agent_file_bridge.command(workdir,allowed,reads)
    config=["-c","mcp_servers.task_files.command="+json.dumps(argv[0]),
            "-c","mcp_servers.task_files.args="+json.dumps(argv[1:])]
    return {"touches":allowed,"reads":reads,"config":config}

def codex_reason(log):
    """Return a short sanitized final Codex message for failure evidence."""
    try:
        lines=Path(log).read_text(encoding="utf-8").splitlines()
    except OSError:
        return ""
    message=""
    for line in lines:
        try:
            item=json.loads(line).get("item") or {}
        except (ValueError,AttributeError):
            continue
        if item.get("type")=="agent_message" and isinstance(item.get("text"),str):
            message=item["text"]
    message=re.sub(r"(sk-[A-Za-z0-9_-]{8,}|[A-Za-z]:[\\/][^\s'\"]*)","[redacted]",message)
    return " ".join("".join(c if c.isprintable() else " " for c in message).split())[:300]

def hide_images(workdir):
    # Agent sees a sparse checkout WITHOUT production or reference images.
    # After the AI session exits, full worktree is restored for REAL Godot tests.
    patterns=["/*"]
    for ext in IMAGE_GLOBS:
        patterns+=["!/"+ext,"!/**/"+ext]
    execute(["git","sparse-checkout","set","--no-cone","--stdin"],workdir,
            input="\n".join(patterns)+"\n")

def changed_paths(workdir):
    tracked=git("diff","--name-only","HEAD",cwd=workdir).splitlines()
    staged=git("diff","--cached","--name-only",cwd=workdir).splitlines()
    untracked=git("ls-files","--others","--exclude-standard",cwd=workdir).splitlines()
    return sorted(set(tracked+staged+untracked))

def tests(workdir,task,scope="--changed"):
    # Only expected unittest arguments; never execute arbitrary task-supplied shell.
    requested=safe_test(normalize_test(safe_test(shlex.split(task["test"],posix=False))))
    # Use current interpreter and trusted test modules regardless of task-controlled exe.
    step=requested[1:]
    if step[:1]==["-3"]:step=step[1:]
    # The router (tools/test_map.json) picks tests for changed paths, or all of them on main.
    commands=[
        [sys.executable,*step],
        [sys.executable,"tools/run_tests.py",scope]]
    failures=[]
    logs=[]
    for index,command in enumerate(commands):
        proc=execute(command,workdir,timeout=1800,check=False)
        if proc.returncode:
            stamp_text=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
            log=Path(workdir)/".agents/monitoring/.local/test-logs"/(task.get("id","task")+"_"+str(index)+"_"+stamp_text+".log")
            log.parent.mkdir(parents=True,exist_ok=True)
            combined=(proc.stdout or "")+(("\n" if proc.stdout and proc.stderr else "")+(proc.stderr or ""))
            log.write_text("command: "+" ".join(str(x) for x in command)+"\nexit code: "+str(proc.returncode)+"\n\n"+combined,encoding="utf-8",newline="\n")
            lines=combined.splitlines()
            details=[]
            for line in lines:
                value=line.strip()
                if (re.search(r"\b(?:FAIL|ERROR):\s+",value) or
                    re.search(r'File ".+", line \d+',value) or
                    re.match(r"(?:AssertionError|Error|Exception|RuntimeError):",value)):
                    if value not in details:details.append(value)
            label=" ".join(str(x) for x in command[1:3])
            suffix="; ".join(details[:5]) or "see full log"
            rel=log.relative_to(workdir).as_posix()
            failures.append(label+" exit "+str(proc.returncode)+": "+suffix+"; log: "+rel)
            logs.append(rel)
    if failures:raise RuntimeError("; ".join(failures))

def validate_with_repair(workdir, task, paths, agent, tid, timeout):
    """One bounded repair only for ordinary pre-commit test failures in manual mode."""
    try:
        tests(workdir, task)
        return None
    except RuntimeError as exc:
        budget = getattr(_BUDGET, "value", None)
        if budget is None or not budget[1]:
            raise
        # tests() emits only trusted command names and integer exit codes, no test output.
        diagnostic = re.sub(r"[^A-Za-z0-9 ._/:;=()\-]", "?", str(exc))[:1200]
    hide_images(workdir)
    outcome, log = sanitized_session(agent, workdir, tid, timeout, repair_context=diagnostic)
    git("sparse-checkout", "disable", cwd=workdir)
    if outcome.returncode:
        message = quota_message(outcome)
        if message:
            raise QuotaExceeded(message)
        raise RuntimeError("Repair CLI failed; code not merged")
    allowed_changed(changed_paths(workdir), paths)
    tests(workdir, task)
    return log


def state_path(tid):
    return LOCAL/("runner-state-"+tid+".json")

def read_state(tid):
    return read_json(state_path(tid),{})

def checkpoint(tid,agent,phase,details):
    """Per-task state, so parallel claude/codex runs never read each other's phase;
    runner-state.json only mirrors the latest event for humans."""
    LOCAL.mkdir(parents=True,exist_ok=True)
    body=json.dumps({"task":tid,"agent":agent,"phase":phase,"at":stamp(),
                     "details":details},indent=2)+"\n"
    for p in (state_path(tid),LOCAL/"runner-state.json"):
        p.write_text(body,encoding="utf-8",newline="\n")

QUOTA=re.compile(r"usage.?limit|rate.?limit|quota.?exceed|too many requests|purchase more credits",re.I)
COOLDOWN_MINUTES=60

class QuotaExceeded(RuntimeError):
    """The agent CLI refused to work (subscription usage/rate limit): not a task failure."""

def quota_message(proc):
    """The limit line from a failed agent CLI run, or None for ordinary failures."""
    if not proc.returncode:
        return None
    text=(proc.stderr or "")+"\n"+(proc.stdout or "")
    line=next((l for l in text.splitlines() if QUOTA.search(l)),None)
    return line.strip()[:240] if line else None

def cooldown_path(agent):
    return LOCAL/("cooldown-"+agent+".json")

def cooling_until(agent):
    info=read_json(cooldown_path(agent),{})
    try:
        until=datetime.fromisoformat(str(info.get("retry_after","")))
    except ValueError:
        return None
    return until if until>datetime.now(timezone.utc) else None

def reset_time(message,now=None):
    """When the CLI says the limit resets: Claude's "|<epoch>" or Codex's "try again at 3:53 PM"."""
    now=now or datetime.now(timezone.utc)
    when=None
    epoch=re.search(r"\|(\d{10})\b",message)
    clock=re.search(r"(?i)\bat\s+(\d{1,2}):(\d{2})\s*([AP]M)\b",message)
    if epoch:
        when=datetime.fromtimestamp(int(epoch.group(1)),timezone.utc)
    elif clock:
        local=now.astimezone()
        hour=int(clock.group(1))%12+(12 if clock.group(3).upper()=="PM" else 0)
        when=local.replace(hour=hour,minute=int(clock.group(2)),second=0,microsecond=0)
        if when<=local:
            when+=timedelta(days=1)
    # Ignore implausible values; a small margin avoids retrying a second too early.
    if when and now<when<=now+timedelta(hours=24):
        return when+timedelta(minutes=2)
    return None

def start_cooldown(agent,message,minutes=COOLDOWN_MINUTES):
    LOCAL.mkdir(parents=True,exist_ok=True)
    until=reset_time(message) or datetime.now(timezone.utc)+timedelta(minutes=minutes)
    cooldown_path(agent).write_text(json.dumps({"agent":agent,"retry_after":until.isoformat(),
        "reason":message},indent=2)+"\n",encoding="utf-8",newline="\n")
    return until

def release_for_quota(tid,agent,message):
    """Return a claimed task to todo (not blocked) after a usage limit and record why."""
    p=next((ROOT/".agents/tasks").glob(tid+"_*.md"))
    raw=p.read_text(encoding="utf-8")
    for key,value in (("status","todo"),("owner","unassigned"),("branch","none"),("started_at","unknown")):
        raw=re.sub(r"(?m)^"+key+r": [^\r\n]+$",key+": "+value,raw,count=1)
    raw+="\n## Runner evidence\n- Released to todo: "+agent+" CLI usage limit, no code merged ("+message[:200].replace("\n"," ")+").\n"
    p.write_text(raw,encoding="utf-8",newline="\n")
    main_commit("chore: release "+tid+" after "+agent+" usage limit",agent,tid)

def execution_gate(config):
    if not config.get("execution_enabled",False):
        raise RuntimeError("Execution disabled: supervised end-to-end verification required")
    problems=supervised_problems(config,ROOT)
    if problems:
        raise RuntimeError("Supervised E2E evidence invalid: "+"; ".join(problems))

def record_supervised(path,tid,agent,merge_sha):
    """Write the evidence supervised_problems() requires; execution_enabled stays owner-controlled."""
    config=read_json(path,{})
    config["supervised_e2e_passed"]=True
    config["supervised_e2e"]={"task":tid,"agent":agent,"merge_sha":merge_sha,"verified_at":stamp()}
    path.write_text(json.dumps(config,indent=2)+"\n",encoding="utf-8",newline="\n")
    return config

def task_agent(tid):
    agent=records().get(tid,{}).get("agent")
    return agent if agent in ("claude","codex") else None

def run(tid, supervised=False):
    """Run one task; on every exit (success, failure, revert) main must end clean."""
    finished=False
    try:
        _run(tid,supervised)
        finished=True
    finally:
        with exclusive("main-merge"):
            agent=task_agent(tid)
            problem=settle_main(tid,agent) if agent else (
                "Main left dirty: "+", ".join(dirty_paths()[:10]) if dirty_paths() else None)
        if problem:
            info=read_state(tid)
            details=(str(info.get("details",""))+" | " if not finished and info else "")+problem
            checkpoint(tid,agent or "unknown","blocked_dirty_main",details[:400])
            print("agent runner: "+problem,file=sys.stderr)
            if finished:
                raise RuntimeError(problem)

def _run(tid, supervised=False):
    config=read_json(CONFIG,{})
    if supervised:
        if not sys.stdin.isatty():
            raise RuntimeError("First supervised execution needs a real interactive terminal")
        print("SUPERVISED ONE-TIME TEST. This can commit and merge verified task code into main.")
        print("Check TASK touches, backup local changes, and confirm correct Godot CLI first.")
        typed=input("To continue type exactly SUPERVISE "+tid+": ").strip()
        if typed != "SUPERVISE "+tid:
            raise RuntimeError("Supervised consent not given")
    else:
        execution_gate(config)
    if os.name!="nt":
        raise RuntimeError("Run coding agents only on the owner's Windows host")
    with exclusive("task-claim"):
        if git("branch","--show-current")!="main":
            raise RuntimeError("Start from a clean main branch")
        if dirty_paths():
            # Heal regenerated-only drift (e.g. an index missed by an older runner) before claiming.
            agent=task_agent(tid)
            problem=settle_main(tid,agent) if agent else "unknown task agent"
            if problem:
                raise RuntimeError("Start from a clean main branch: "+problem)
        git("pull","--ff-only","origin","main")
        all_tasks=records()
        task=all_tasks.get(tid)
        if task is None:raise RuntimeError("Unknown "+tid)
        paths=verify_claim(task,all_tasks)
        agent=task["agent"]
        branch="work/"+tid.lower()+"-"+uuid.uuid4().hex[:8]
        amend_status(tid,"in_progress",branch=branch,reason="Claimed by local runner at "+stamp())
        p=next((ROOT/".agents/tasks").glob(tid+"_*.md"))
        raw=p.read_text(encoding="utf-8")
        raw=re.sub(r"(?m)^owner: [^\r\n]+$","owner: "+agent,raw,count=1)
        raw=re.sub(r"(?m)^started_at: [^\r\n]+$","started_at: "+stamp(),raw,count=1)
        p.write_text(raw,encoding="utf-8",newline="\n")
        main_commit("chore: claim "+tid,agent,tid)
    WORKTREES.mkdir(parents=True,exist_ok=True)
    workdir=WORKTREES/(tid+"-"+branch.split("-")[-1])
    git("worktree","add","-b",branch,str(workdir),"main")
    checkpoint(tid,agent,"claimed",branch)
    try:
        hide_images(workdir)
        execute([sys.executable,"tools/agent_costs.py","start",tid,"--agent",agent],workdir)
        outcome,log=sanitized_session(agent,workdir,tid,config.get("execution_timeout_seconds",1800))
        # restore original art only AFTER model session has fully exited
        git("sparse-checkout","disable",cwd=workdir)
        if outcome.returncode:
            message=quota_message(outcome)
            if message:
                raise QuotaExceeded(message)
            raise RuntimeError("Agent CLI failed; code not merged")
        changed=changed_paths(workdir)
        allowed_changed(changed,paths)
        if not changed:raise RuntimeError("Agent did not change any allowed code")
        repair_log=validate_with_repair(workdir,task,paths,agent,tid,config.get("execution_timeout_seconds",1800))
        if repair_log is not None:log=repair_log
        changed=changed_paths(workdir)
        allowed_changed(changed,paths)
        git("add","--",*changed,cwd=workdir)
        if log is not None:
            execute([sys.executable,"tools/agent_costs.py","import-codex",str(log)],workdir,check=False)
        execute([sys.executable,"tools/agent_costs.py","complete","--message",
                 "feat: implement "+tid,"--no-summary"],workdir)
        checkpoint(tid,agent,"ready_to_merge",git("rev-parse","HEAD",cwd=workdir))
        if requires_pr(changed):
            git("push", "-u", "origin", branch, cwd=workdir)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".md", delete=False) as body:
                body.write("Implements " + tid + ". Task tests and changed-path validation passed.\n\nInfrastructure requires review before merge.\n")
                body_path = body.name
            try:
                url=execute(["gh", "pr", "create", "--base", "main", "--head", branch,
                             "--title", "feat: implement " + tid, "--body-file", body_path], workdir).stdout.strip()
            finally:
                Path(body_path).unlink(missing_ok=True)
            with exclusive("main-merge"):
                amend_status(tid,"review",branch=branch,reason="Validated infrastructure PR: "+url)
                main_commit("chore: record review "+tid,agent,tid)
            checkpoint(tid,agent,"review",url)
            return
        with exclusive("main-merge"):
            if git("status","--porcelain"):
                raise RuntimeError("Main became dirty; refusing merge")
            git("pull","--ff-only","origin","main")
            git("rebase","main",cwd=workdir)
            allowed_changed(git("diff","--name-only","main...HEAD",cwd=workdir).splitlines(),
                            paths+[".agents/monitoring/receipts/"])
            tests(workdir,task)
            git("merge","--no-ff","--no-edit",branch)
            merge_sha=git("rev-parse","HEAD")
            git("push","origin","main")
            checkpoint(tid,agent,"merged_pending_main_tests",merge_sha)
            try:
                tests(ROOT,task,"--all")
            except Exception:
                git("revert","-m","1","--no-edit",merge_sha)
                git("push","origin","main")
                amend_status(tid,"blocked",reason="Post-merge regression; auto-reverted "+merge_sha)
                main_commit("chore: block reverted "+tid,agent,tid)
                checkpoint(tid,agent,"auto_reverted",merge_sha)
                return
            amend_status(tid,"done",reason="Merged "+merge_sha+"; post-merge validation passed")
            extra=None
            if supervised:
                # Only a real, fully validated supervised run may mark E2E as passed.
                record_supervised(CONFIG,tid,agent,merge_sha)
                extra=[CONFIG.relative_to(ROOT).as_posix()]
            main_commit("chore: record validated "+tid,agent,tid,extra)
            checkpoint(tid,agent,"done",merge_sha)
    except QuotaExceeded as exc:
        # Usage limits are not task failures: release to todo and pause this agent.
        checkpoint(tid,agent,"released_quota",str(exc)[:200])
        start_cooldown(agent,str(exc))
        try:
            with exclusive("main-merge"):
                release_for_quota(tid,agent,str(exc))
        except Exception as record_exc:
            print("agent runner: could not release task: "+str(record_exc),file=sys.stderr)
        raise
    except Exception as exc:
        # Fail closed; do not delete any evidence or guess that a merge succeeded.
        checkpoint(tid,agent,"blocked_pending_review",str(exc)[:200])
        if git("branch","--show-current")=="main":
            try:
                with exclusive("main-merge"):
                    amend_status(tid,"blocked",reason="Runner failed: "+str(exc)[:300])
                    main_commit("chore: block failed "+tid,agent,tid)
            except Exception as record_exc:
                # Keep the original failure; run() reports any leftover dirt on main.
                print("agent runner: could not record block: "+str(record_exc),file=sys.stderr)
        raise
    finally:
        # Preserve worktree on failure for human debugging; remove only successful
        # worktrees after runner confirms post-merge tests.
        info=read_state(tid)
        released=info.get("phase")=="released_quota" and not changed_paths(workdir)
        if info.get("phase")=="done" or released:
            git("worktree","remove","--force",str(workdir))
            git("branch","-d",branch)

def pick_next(agent):
    """Choose the highest priority eligible task without contacting AI."""
    if agent not in ("claude", "codex"):
        raise ValueError("Unsupported agent")
    active=records()
    rank={"critical":0,"high":1,"normal":2,"low":3}
    choices=[]
    for t in active.values():
        if t.get("agent") != agent or t.get("status") != "todo":
            continue
        try:
            verify_claim(t,active)
        except ValueError:
            continue
        m=re.search(r"(?m)^\*\*Priority:\*\* (critical|high|normal|low)",t["text"])
        priority=m.group(1) if m else "normal"
        choices.append((rank[priority],t["id"]))
    return min(choices)[1] if choices else None

PULSE_PATHS=[".agents/planner/goals.json",".agents/planner/daily/"]

def refresh_queue(agent):
    """Idle: run the deterministic milestone pulse (no AI) so new or unblocked steps can be claimed."""
    if git("branch","--show-current")!="main" or dirty_paths():
        return False
    with exclusive("task-claim"):
        git("pull","--ff-only","origin","main")
        result=json.loads(execute([sys.executable,"tools/goal_task_factory.py","pulse"]).stdout)
        fresh=result.get("created",[])+result.get("promoted",[])
        main_commit("chore: pulse "+(", ".join(fresh) if fresh else "(no new tasks)"),agent,"pulse",PULSE_PATHS)
    return bool(fresh)

def run_session(agent):
    """Work through eligible tasks until none is left, the usage limit is hit, or a task fails."""
    config=read_json(CONFIG,{})
    execution_gate(config)
    limit=int(config.get("max_tasks_per_runner_session",1))
    # Windows Task Scheduler kills the worker after 3 h: start a task only if it can still finish.
    budget=int(config.get("runner_session_minutes",150))*60
    per_task=int(config.get("execution_timeout_seconds",1800))+600
    started=time.monotonic()
    finished=[]
    pulsed=False
    while len(finished)<limit:
        if finished and time.monotonic()-started+per_task>budget:
            print(agent+" session time budget reached; remaining tasks wait for the next run")
            break
        until=cooling_until(agent)
        if until:
            print(agent+" usage cooldown until "+until.isoformat()+"; no task claimed, no AI call made")
            break
        selected=pick_next(agent)
        if selected is None and not pulsed:
            pulsed=True
            if refresh_queue(agent):
                selected=pick_next(agent)
        if selected is None:
            print("No eligible task for "+agent+"; no AI call made")
            break
        run(selected)  # failures raise and end the session; usage limits raise QuotaExceeded
        finished.append(selected)
        if read_state(selected).get("phase")!="done":
            break  # e.g. auto-reverted after post-merge tests: stop instead of chaining work
    if finished:
        print(agent+" session finished "+str(len(finished))+" task(s): "+", ".join(finished))
    return finished

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run",metavar="TASK-ID")
    mode.add_argument("--supervised",metavar="TASK-ID")
    mode.add_argument("--run-next",choices=("claude","codex"))
    mode.add_argument("--preflight",action="store_true")
    args=parser.parse_args()
    if args.preflight:
        cfg=read_json(CONFIG,{})
        print(json.dumps({"execution_enabled":cfg.get("execution_enabled",False),
          "supervised_e2e_passed":cfg.get("supervised_e2e_passed",False),
          "supervised_e2e":cfg.get("supervised_e2e"),
          "problems":supervised_problems(cfg,ROOT),
          "mode":"Windows only; no API keys; default disabled"},indent=2))
        return
    if args.supervised:
        run(args.supervised,supervised=True)
    else:
        # All direct/scheduled/manual entrypoints share a cross-clone lease.
        from manual_agents import repository_lease
        with repository_lease(ROOT):
            if args.run_next:
                run_session(args.run_next)
            else:
                run(args.run)

if __name__=="__main__":
    try:main()
    except QuotaExceeded as exc:
        # Deferred, not failed: the task is back to todo and this agent cools down.
        print("agent runner: usage limit, task released for retry: "+str(exc))
    except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired) as exc:
        print("agent runner: "+str(exc),file=sys.stderr)
        sys.exit(1)
