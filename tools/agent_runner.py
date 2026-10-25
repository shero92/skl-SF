#!/usr/bin/env python3
"""Windows-only local coding executor. DISABLED until supervised end-to-end signoff.

No API keys, no Cloud AI, no arbitrary shell commands from task text.
The local owner's authenticated Claude/Codex CLI is used only when enabled.
"""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from runner_safety import allowed_changed, is_art, is_generated, normalize, safe_test, touches, verify_claim

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/".agents/planner/config.json"
LOCAL=ROOT/".agents/monitoring/.local"
WORKTREES=ROOT.parent/".skl-sf-worktrees"
IMAGE_GLOBS=["*.[pP][nN][gG]","*.[jJ][pP][gG]","*.[jJ][pP][eE][gG]",
 "*.[wW][eE][bB][pP]","*.[sS][vV][gG]","*.[gG][iI][fF]",
 "*.[bB][mM][pP]","*.[pP][sS][dD]","*.[aA][sS][eE][pP][rR][iI][tT][eE]"]
NO_KEYS=("OPENAI_API_KEY","ANTHROPIC_API_KEY")

def execute(argv,cwd=ROOT,*,input=None,timeout=600,check=True):
    clean=os.environ.copy()
    for key in NO_KEYS:clean.pop(key,None)
    proc=subprocess.run([str(x) for x in argv],cwd=str(cwd),input=input,
        capture_output=True,text=True,encoding="utf-8",errors="replace",
        env=clean,timeout=timeout,shell=False)
    if check and proc.returncode:
        raise RuntimeError("command failed: "+str(argv[0])+" ("+str(proc.returncode)+")")
    return proc

def git(*args,cwd=ROOT):
    return execute(["git",*args],cwd).stdout.strip()

def stamp():
    return datetime.now(timezone.utc).isoformat()

def read_json(path,default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default

def records(root=ROOT):
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
    p.write_text(raw,encoding="utf-8")

def index_main():
    execute([sys.executable,"tools/agent_workflow.py","--write"])
    execute([sys.executable,"tools/generate_project_indexes.py","--write"])
    execute([sys.executable,"tools/agent_costs.py","report"])
    execute([sys.executable,"tools/goal_costs.py","--write"])

def main_commit(subject,agent,tid,extra=None):
    index_main()
    paths=[".agents/tasks",".agents/project/TASKS.md",".agents/project/ACTIVE.md",
           ".agents/monitoring/summary.json",".agents/monitoring/summary.md",
           ".agents/monitoring/goal_summary.json",".agents/monitoring/goal_summary.md"]
    if extra:paths+=extra
    git("add","-A","--",*paths)
    changed=git("diff","--cached","--name-only")
    if changed:
        git("commit","-m",subject,"-m","Task-ID: "+tid+"\nAgent: "+agent+"\nCost-USD: unknown")
        git("push","origin","main")

@contextmanager
def exclusive(label):
    LOCAL.mkdir(parents=True,exist_ok=True)
    target=LOCAL/(label+".lock")
    # Exclusive create: fail closed on stale lock; owner must examine and clear.
    try:
        fd=os.open(str(target),os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        raise RuntimeError("Another operation has lock "+str(target)+"; do not run concurrently")
    try:
        with os.fdopen(fd,"w") as handle:handle.write(str(os.getpid())+" "+stamp())
        yield
    finally:
        target.unlink(missing_ok=True)

def sanitized_session(agent,workdir,tid,timeout):
    prompt=(
        "Implement "+tid+". Read AGENTS.md and the canonical task. "
        "Modify ONLY its touches paths; no characters, UI, gameplay or art. "
        "Never read, view, inspect or generate PNG/JPG/SVG or other images; "
        "goal reference images are not accessible. "
        "No shell commands, no git commits, no index/dashboard generation. "
        "Leave code changes in the worktree and describe code changes briefly. "
        "Stop if a file outside touches is needed. The runner handles tests, "
        "tokens, merge and rollback.")
    if agent=="claude":
        args=["claude","-p","--permission-mode","acceptEdits","--tools",
              "Read,Edit,Write,Glob,Grep","--disallowedTools","Bash",
              "--strict-mcp-config","--no-chrome","--output-format","json",
              "--effort","low",prompt]
        proc=execute(args,workdir,timeout=timeout,check=False)
        return proc,None
    log=workdir/".agents/monitoring/.local/codex-exec.jsonl"
    log.parent.mkdir(parents=True,exist_ok=True)
    args=["codex","exec","--sandbox","workspace-write","--cd",str(workdir),
          "--json","-"]
    proc=execute(args,workdir,input=prompt,timeout=timeout,check=False)
    log.write_text(proc.stdout,encoding="utf-8")
    return proc,log

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
    requested=shlex.split(task["test"],posix=False)
    safe_test(requested)
    # Use current interpreter and trusted test modules regardless of task-controlled exe.
    step=requested[1:]
    if step[:1]==["-3"]:step=step[1:]
    # The router (tools/test_map.json) picks tests for changed paths, or all of them on main.
    commands=[
        [sys.executable,*step],
        [sys.executable,"tools/run_tests.py",scope]]
    failures=[]
    for command in commands:
        proc=execute(command,workdir,timeout=1800,check=False)
        if proc.returncode:failures.append(" ".join(str(x) for x in command[1:3])+" returned "+str(proc.returncode))
    if failures:raise RuntimeError("; ".join(failures))

def checkpoint(tid,agent,phase,details):
    p=LOCAL/"runner-state.json"
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps({"task":tid,"agent":agent,"phase":phase,"at":stamp(),
                             "details":details},indent=2)+"\n",encoding="utf-8")

def run(tid, supervised=False):
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
        if not config.get("execution_enabled",False):
            raise RuntimeError("Execution disabled: supervised end-to-end verification required")
        if not config.get("supervised_e2e_passed",False):
            raise RuntimeError("Must explicitly record supervised_e2e_passed before enabling")
    if os.name!="nt":
        raise RuntimeError("Run coding agents only on the owner's Windows host")
    if git("branch","--show-current")!="main" or git("status","--porcelain"):
        raise RuntimeError("Start from a clean main branch")
    with exclusive("task-claim"):
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
        p.write_text(raw,encoding="utf-8")
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
            raise RuntimeError("Agent CLI failed; code not merged")
        changed=changed_paths(workdir)
        allowed_changed(changed,paths)
        if not changed:raise RuntimeError("Agent did not change any allowed code")
        tests(workdir,task)
        git("add","--",*changed,cwd=workdir)
        if log is not None:
            execute([sys.executable,"tools/agent_costs.py","import-codex",str(log)],workdir,check=False)
        execute([sys.executable,"tools/agent_costs.py","complete","--message",
                 "feat: implement "+tid,"--no-summary"],workdir)
        checkpoint(tid,agent,"ready_to_merge",git("rev-parse","HEAD",cwd=workdir))
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
            main_commit("chore: record validated "+tid,agent,tid)
            checkpoint(tid,agent,"done",merge_sha)
    except Exception as exc:
        # Fail closed; do not delete any evidence or guess that a merge succeeded.
        checkpoint(tid,agent,"blocked_pending_review",str(exc)[:200])
        if git("branch","--show-current")=="main" and not git("status","--porcelain"):
            with exclusive("main-merge"):
                amend_status(tid,"blocked",reason="Runner failed; inspect local runner-state.json")
                main_commit("chore: block failed "+tid,agent,tid)
        raise
    finally:
        # Preserve worktree on failure for human debugging; remove only successful
        # worktrees after runner confirms post-merge tests.
        info=read_json(LOCAL/"runner-state.json",{})
        if info.get("phase")=="done":
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
          "mode":"Windows only; no API keys; default disabled"},indent=2))
        return
    if args.supervised:
        run(args.supervised,supervised=True)
    elif args.run_next:
        if not read_json(CONFIG,{}).get("execution_enabled",False) or not read_json(CONFIG,{}).get("supervised_e2e_passed",False):
            raise RuntimeError("Scheduled execution is disabled until supervised E2E owner signoff")
        selected=pick_next(args.run_next)
        if selected is None:
            print("No eligible task for "+args.run_next+"; no AI call made")
            return
        run(selected)
    else:
        run(args.run)

if __name__=="__main__":
    try:main()
    except (OSError,RuntimeError,ValueError,subprocess.TimeoutExpired) as exc:
        print("agent runner: "+str(exc),file=sys.stderr)
        sys.exit(1)
