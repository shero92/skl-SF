#!/usr/bin/env python3
"""Bounded manual coordinator. No AI on idle/dry-run; existing runner owns code execution."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from contextlib import contextmanager
import ctypes
import hashlib
import json
import math
import struct
import zlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import uuid

import agent_runner as ar
from runner_safety import overlaps
from task_evidence import check_task


class CoordinatorError(RuntimeError):pass
class Busy(CoordinatorError):pass


def git(root,*args):
    return subprocess.run(["git",*args],cwd=root,check=True,capture_output=True,text=True).stdout.strip()


def repository_key(root):
    remote=git(root,"remote","get-url","origin").strip().rstrip("/")
    remote=re.sub(r"^git@([^:]+):",r"https://\1/",remote)
    return hashlib.sha256(remote.removesuffix(".git").lower().encode()).hexdigest()[:24]


@contextmanager
def repository_lease(root):
    """Same lease across independent clones and scheduled/manual worker entrypoints."""
    key=repository_key(root)
    if os.name=="nt":
        from ctypes import wintypes
        kernel=ctypes.WinDLL("kernel32",use_last_error=True)
        kernel.CreateMutexW.argtypes=[ctypes.c_void_p,wintypes.BOOL,wintypes.LPCWSTR]
        kernel.CreateMutexW.restype=wintypes.HANDLE
        kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD]
        kernel.ReleaseMutex.argtypes=[wintypes.HANDLE]
        kernel.CloseHandle.argtypes=[wintypes.HANDLE]
        handle=kernel.CreateMutexW(None,False,"Local\\skl-SF-manual-"+key)
        if not handle:raise CoordinatorError("Cannot create repository worker mutex")
        result=kernel.WaitForSingleObject(handle,0)
        if result not in (0,128):
            kernel.CloseHandle(handle)
            raise Busy("Another manual or scheduled worker owns this repository session")
        try:yield
        finally:
            kernel.ReleaseMutex(handle);kernel.CloseHandle(handle)
    else:
        import fcntl
        folder=Path(tempfile.gettempdir())/"skl-SF-worker-locks";folder.mkdir(exist_ok=True)
        with (folder/(key+".lock")).open("a",encoding="utf-8",newline="\n") as handle:
            try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as exc:raise Busy("Repository worker already active") from exc
            try:yield
            finally:fcntl.flock(handle,fcntl.LOCK_UN)


def records(root):
    result=ar.records(root)
    ids=[]
    for file in (root/".agents/tasks").glob("TASK-*.md"):
        match=re.search(r"(?m)^id: (TASK-\d{4})$",file.read_text(encoding="utf-8"))
        if match:ids.append(match.group(1))
    if len(ids)!=len(set(ids)):raise CoordinatorError("Duplicate canonical task IDs; reconcile before execution")
    return result


def is_art(task):
    return task.get("art_request","none")!="none" or task.get("agent") in ("graphics","specialist")


def art_adapter(root,agent):
    """Only an explicitly approved/hash-pinned local adapter can expose an image tool.

    No such capability is inferred from a CLI login, model name or installed Blender.
    """
    manifest=root/".agents/planner/manual_art_adapters.json"
    if not manifest.is_file():return None
    config=json.loads(manifest.read_text(encoding="utf-8")).get("agents",{}).get(agent,{})
    if (config.get("status")!="approved" or not config.get("approved_by")
            or not config.get("approved_at") or config.get("image_tool_verified") is not True):return None
    relative=config.get("path","")
    if not isinstance(relative,str) or not re.fullmatch(r"tools/[A-Za-z0-9_/.-]+\.py",relative) or ".." in relative.split("/"):
        return None
    path=(root/relative).resolve()
    if not path.is_relative_to((root/"tools").resolve()) or not path.is_file():return None
    if hashlib.sha256(path.read_bytes()).hexdigest()!=config.get("sha256"):return None
    return path


def task_blockers(task,all_tasks,root,agents,include_art=False):
    reasons=[]
    if task.get("status")!="todo":return ["status: "+task.get("status","missing")]
    deps=[x.strip() for x in task.get("depends_on","none").split(",") if x.strip() and x.strip()!="none"]
    pending=[tid for tid in deps if all_tasks.get(tid,{}).get("status")!="done"]
    if pending:reasons.append("unfinished dependencies: "+", ".join(pending))
    for other in all_tasks.values():
        if other.get("status")!="in_progress":continue
        if other.get("agent")==task.get("agent"):reasons.append("agent already has an active task")
        if any(overlaps(p.strip(),q.strip()) for p in task.get("touches", "").split(",")
               for q in other.get("touches", "").split(",") if p.strip() and q.strip()):
            reasons.append("touch conflict with active "+other["id"])
    if is_art(task):
        if not include_art:reasons.append("art excluded; use -IncludeArt")
        if task.get("agent") not in agents:reasons.append("ART task must be assigned to codex or claude")
        elif art_adapter(root,task["agent"]) is None:reasons.append("approved image-tool adapter unavailable")
        aid=task.get("art_request","none")
        files=list((root/".agents/graphics/requests").glob(aid+"_*.md"))
        if len(files)!=1:reasons.append("ART request missing or ambiguous")
        elif not re.search(r"(?m)^status: (requested|in_progress)$",files[0].read_text(encoding="utf-8")):
            reasons.append("ART request is not ready for production")
        if not task.get("evidence_manifest"):reasons.append("ART reference evidence manifest required")
    elif task.get("agent") not in agents:reasons.append("assigned agent not selected")
    else:
        try:ar.verify_claim(task,all_tasks)
        except ValueError as exc:reasons.append(str(exc))
    try:reasons.extend(check_task(task,root))
    except (ValueError,OSError,KeyError,TypeError) as exc:reasons.append("evidence invalid: "+str(exc))
    return list(dict.fromkeys(reasons))


def queue_snapshot(root,agents,include_art=False):
    tasks=records(root)
    return {tid:{"agent":t.get("agent"),"status":t.get("status"),
                 "blockers":task_blockers(t,tasks,root,agents,include_art)} for tid,t in sorted(tasks.items())}


def choose(tasks,agents,reserved,attempted,root,include_art=False,cooling=None):
    rank={"critical":0,"high":1,"normal":2,"low":3}
    occupied=[tasks[tid] for tid in reserved if tid in tasks]
    selected=[]
    for agent in agents:
        if any(t.get("agent")==agent for t in occupied) or (cooling and cooling(agent)):continue
        options=[]
        for tid,task in tasks.items():
            if task.get("agent")!=agent or tid in attempted or tid in reserved:continue
            if task_blockers(task,tasks,root,agents,include_art):continue
            paths=[p.strip() for p in task.get("touches","").split(",") if p.strip()]
            if any(overlaps(p,q.strip()) for other in occupied+selected
                   for p in paths for q in other.get("touches","").split(",") if q.strip()):continue
            match=re.search(r"(?m)^\*\*Priority:\*\* (critical|high|normal|low)",task.get("text",""))
            options.append((rank[match.group(1) if match else "normal"],tid,task))
        if options:selected.append(min(options,key=lambda v:v[:2])[2])
    return selected


def coordinator(source,deadline):
    """Reuse a dedicated clean clone; never stash/reset/clean the user's checkout."""
    remote=git(source,"remote","get-url","origin")
    base=Path(os.environ.get("LOCALAPPDATA",tempfile.gettempdir()))/"rtk/skl-SF/manual"
    path=base/repository_key(source)
    def command(*args,cwd=None):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise CoordinatorError("Session deadline before coordinator preparation")
        return subprocess.run(["git",*args],cwd=cwd,check=True,capture_output=True,text=True,timeout=remaining)
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        command("clone","--no-checkout","--single-branch","--branch","main",remote,str(path))
        command("checkout","main",cwd=path)
    if git(path,"remote","get-url","origin")!=remote:raise CoordinatorError("Coordinator origin mismatch")
    if git(path,"branch","--show-current")!="main" or git(path,"status","--porcelain"):
        raise CoordinatorError("Dedicated coordinator is not clean main; preserve it for review")
    command("pull","--ff-only","origin","main",cwd=path)
    for key in ("user.name","user.email"):
        value=subprocess.run(["git","config","--get",key],cwd=source,capture_output=True,text=True).stdout.strip()
        if value:command("config",key,value,cwd=path)
    return path


@contextmanager
def bind_runner(root):
    old={name:getattr(ar,name) for name in ("ROOT","CONFIG","LOCAL","WORKTREES")}
    ar.ROOT=root;ar.CONFIG=root/".agents/planner/config.json";ar.LOCAL=root/".agents/monitoring/.local"
    ar.WORKTREES=root.parent/(root.name+"-worktrees")
    try:yield
    finally:
        for name,value in old.items():setattr(ar,name,value)


def reject_producer_approval(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if (key in {"reviewer","reviewer_session","approved_by","owner_approved","owner_final_signoff","integrated"} and item
                    or key in {"status","review_status","qa_status"} and item in ("ready","reviewed","approved","integrated")):
                raise ValueError("Producer cannot author independent approval/integration")
            reject_producer_approval(item)
    elif isinstance(value,list):
        for item in value:reject_producer_approval(item)


def png_structure(data):
    offset=8;image_data=False;ended=False
    while offset+12<=len(data):
        length=struct.unpack(">I",data[offset:offset+4])[0]
        kind=data[offset+4:offset+8];stop=offset+12+length
        if stop>len(data):raise ValueError("Truncated PNG chunk")
        if zlib.crc32(data[offset+4:offset+8+length]) & 0xffffffff != struct.unpack(">I",data[offset+8+length:stop])[0]:
            raise ValueError("Invalid PNG chunk CRC")
        if kind==b"IDAT" and length:image_data=True
        if kind==b"IEND":
            ended=True
            if length or stop!=len(data):raise ValueError("Invalid PNG end")
            break
        offset=stop
    if not image_data or not ended:raise ValueError("PNG image data/end missing")


def validate_art_output(workdir,aid,expected,reference_sha):
    """Validate bytes/manifests only; no artistic approval or image decoding."""
    import art_delivery
    workdir=workdir.resolve()
    folder=workdir/".agents/graphics/deliveries"/aid
    manifest_path=folder/"manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("request_id")!=aid or not manifest.get("files"):
        raise ValueError("ART manifest request/files mismatch")
    reject_producer_approval(manifest)
    if manifest.get("status","delivered")!="delivered":raise ValueError("Producer may deliver only")
    if (not all(manifest.get(k) for k in ("producer","tool","model"))
            or manifest.get("reference_sha256")!=reference_sha):
        raise ValueError("ART provenance and authenticated reference hash required")
    paths=[entry.get("path") for entry in manifest["files"]]
    if len(paths)!=len(set(paths)) or set(paths)!=set(expected):
        raise ValueError("ART manifest must match every requested output exactly")
    allowed={manifest_path.relative_to(workdir).as_posix()}
    for entry in manifest["files"]:
        relative=entry.get("path","")
        path=(workdir/relative).resolve()
        if (not path.is_relative_to(folder.resolve()) or path.suffix.lower()!=".png"
                or ".." in relative.split("/") or "\\" in relative):
            raise ValueError("ART output escaped its delivery directory")
        data=path.read_bytes()
        if hashlib.sha256(data).hexdigest()!=entry.get("sha256"):
            raise ValueError("ART output hash mismatch")
        dimensions=art_delivery.png_properties(path)
        png_structure(data)
        origin=entry.get("origin")
        if (entry.get("pixel_size")!=dimensions or not isinstance(origin,list) or len(origin)!=2
                or any(type(n)not in (int,float) or not math.isfinite(n) for n in origin)):
            raise ValueError("Measured output dimensions/origin required")
        if not all(k in entry for k in ("footprint","collision","shadow")):
            raise ValueError("Ground footprint/collision/shadow metadata required")
        allowed.add(path.relative_to(workdir).as_posix())
    changed=set(ar.changed_paths(workdir))
    if not changed or not changed.issubset(allowed):
        raise ValueError("ART producer changed files outside its delivery manifest")
    return sorted(changed)


def run_art(task,deadline,cancel_event=None):
    """Produce in a separate assigned ART worktree; push a review PR, never merge art."""
    adapter=art_adapter(ar.ROOT,task["agent"])
    if adapter is None:raise CoordinatorError("Approved image adapter disappeared")
    tid=task["id"];aid=task["art_request"];agent=task["agent"]
    if not re.fullmatch(r"ART-\d{4}",aid):raise CoordinatorError("Invalid ART ID")
    branch="art/"+aid.lower()+"-"+uuid.uuid4().hex[:8]
    workdir=ar.WORKTREES/(tid+"-"+branch.split("-")[-1])
    with ar.execution_budget(deadline,repair_attempts=0,cancel_event=cancel_event):
        with ar.coordination_lock():
            current=records(ar.ROOT).get(tid,{})
            if current.get("status")!="todo":raise CoordinatorError("ART task already claimed")
            if ar.dirty_paths():raise CoordinatorError("Coordinator dirty before ART claim")
            ar.amend_status(tid,"in_progress",branch=branch,reason="Manual ART producer; review required")
            ar.main_commit("chore: claim "+tid,agent,tid)
            ar.WORKTREES.mkdir(parents=True,exist_ok=True)
            ar.git("worktree","add","--no-checkout","-b",branch,str(workdir),"main")
        try:
            # Expose only this request's registered environment reference IDs to the artist.
            request=next((ar.ROOT/".agents/graphics/requests").glob(aid+"_*.md"))
            text=request.read_text(encoding="utf-8")
            match=re.search(r"(?m)^existing_asset_ids: (.*)$",text)
            ids={v.strip()for v in (match.group(1) if match else "").split(",")}
            catalog=json.loads((ar.ROOT/"map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))
            exposed=[a["texture_path"].removeprefix("res://")for a in catalog["assets"]
                     if a["id"]in ids and a["category"]not in ("characters","ui")]
            proof=json.loads((ar.ROOT/task["evidence_manifest"]).read_text(encoding="utf-8"))
            exposed.extend(item["path"]for item in proof["requirements"]if item.get("kind")=="reference")
            patterns=["/*","!/map_factory/parts/","!/.agents/graphics/deliveries/","!/docs/previews/","!/.agents/qa/renders/"]
            patterns.extend("!/**/"+pattern for pattern in ar.IMAGE_GLOBS)
            patterns.extend("/"+name for name in exposed)
            ar.execute(["git","sparse-checkout","set","--no-cone","--stdin"],workdir,input="\n".join(patterns)+"\n")
            ar.git("read-tree","-mu","HEAD",cwd=workdir)
            base=ar.git("rev-parse","HEAD",cwd=workdir)
            inventory=re.search(r"(?m)^output_paths: (.*)$",text)
            expected=[v.strip() for v in (inventory.group(1) if inventory else "").split(",") if v.strip()]
            if not expected or any(ar.git("ls-tree","--name-only",base,"--",name,cwd=workdir) for name in expected):
                raise CoordinatorError("Existing delivery must be preserved; allocate reviewed revision paths first")
            reference_sha=next(item["sha256"] for item in proof["requirements"]if item.get("kind")=="reference")
            ar.execute([sys.executable,"tools/agent_costs.py","start",tid,"--agent",agent],workdir)
            local_adapter=workdir/adapter.relative_to(ar.ROOT)
            result=ar.execute([sys.executable,str(local_adapter),"--task",tid,"--art-request",aid,
                               "--review-only","--deadline",str(deadline)],workdir,check=False)
            if result.returncode:raise RuntimeError("ART adapter failed; staged work preserved")
            if ar.git("rev-parse","HEAD",cwd=workdir)!=base:
                raise CoordinatorError("ART adapter created unauthorized commits")
            changed=validate_art_output(workdir,aid,expected,reference_sha)
            staged_request=workdir/request.relative_to(ar.ROOT)
            staged_request.write_text(re.sub(r"(?m)^status: .+$","status: delivered",text,count=1),encoding="utf-8",newline="\n")
            ar.git("add","--",*changed,request.relative_to(ar.ROOT).as_posix(),cwd=workdir)
            ar.execute([sys.executable,"tools/agent_costs.py","complete","--message","art: deliver "+aid,"--no-summary"],workdir)
            ar.git("push","origin","HEAD:"+branch,cwd=workdir)
            body=workdir/".agents/monitoring/.local/art-pr.md"
            body.write_text("Unapproved ART delivery "+aid+" for "+tid+". Independent visual review and owner approval required. No production integration.",encoding="utf-8",newline="\n")
            pr=ar.execute(["gh","pr","create","--base","main","--head",branch,"--title","art: review "+aid,"--body-file",str(body)],workdir).stdout.strip()
            with ar.coordination_lock():
                ar.amend_status(tid,"review",branch=branch,reason="Unapproved delivery PR: "+pr)
                ar.main_commit("chore: record ART review "+tid,agent,tid)
            ar.checkpoint(tid,agent,"review",pr)
        except Exception as exc:
            ar.checkpoint(tid,agent,"blocked_pending_review",str(exc)[:300])
            with ar.coordination_lock():
                if not ar.dirty_paths():
                    ar.amend_status(tid,"blocked",reason="ART producer: "+str(exc)[:300])
                    ar.main_commit("chore: block ART production "+tid,agent,tid)
            raise


def block_missing_evidence(root,agents,include_art):
    """Record only hard prerequisites/tool blockers, never transient dependency conflicts."""
    blocked=[]
    with ar.coordination_lock():
        tasks=records(root)
        for tid,task in tasks.items():
            if task.get("status")!="todo" or task.get("agent") not in agents:continue
            reasons=check_task(task,root)
            if include_art and is_art(task):
                if art_adapter(root,task["agent"]) is None:reasons.append("approved image-tool adapter unavailable")
                if not task.get("evidence_manifest"):reasons.append("ART reference evidence manifest required")
            if reasons:
                ar.amend_status(tid,"blocked",reason="Manual prerequisites: "+"; ".join(reasons))
                blocked.append(tid)
        if blocked:ar.main_commit("chore: record task-specific prerequisite blockers","codex",blocked[0])
    return blocked


def execute_task(task,deadline,cancel_event=None):
    if is_art(task):run_art(task,deadline,cancel_event)
    else:
        with ar.execution_budget(deadline,repair_attempts=1,cancel_event=cancel_event):ar.run(task["id"])
    return ar.read_state(task["id"])


def run_batch(root,agents,max_tasks=10,max_minutes=150,include_art=False,*,executor=None,clock=time.monotonic):
    if max_tasks<1 or not math.isfinite(max_minutes) or max_minutes<=0:raise ValueError("Finite positive count and time limits required")
    deadline=clock()+max_minutes*60
    config=ar.read_json(ar.CONFIG,{})
    ar.execution_gate(config)
    per_task=int(config.get("execution_timeout_seconds",1800))
    attempted=set();results=[];running={};pulsed=False
    cancelled=threading.Event()
    executor=executor or (lambda task,limit:execute_task(task,limit,cancelled))
    with ar.execution_budget(deadline,repair_attempts=0,cancel_event=cancelled):
        prerequisite_blocks=block_missing_evidence(root,agents,include_art)
    with ThreadPoolExecutor(max_workers=len(agents)) as pool:
        while True:
            if clock()>=deadline:
                cancelled.set()
                ar.cancel_budget(cancelled)
                break
            with ar.coordination_lock():
                tasks=records(root)
                available=choose(tasks,agents,{t["id"] for t in running.values()},attempted,root,include_art,ar.cooling_until)
                for task in available:
                    if len(attempted)>=max_tasks:break
                    if deadline-clock()<per_task:break
                    attempted.add(task["id"])
                    running[pool.submit(executor,task,deadline)]=task
            if not running:
                if not pulsed and len(attempted)<max_tasks and deadline-clock()>=per_task:
                    pulsed=True
                    with ar.execution_budget(deadline,repair_attempts=0,cancel_event=cancelled):
                        if ar.refresh_queue(agents[0]):continue
                break
            done,_=wait(running,timeout=min(0.25,max(0,deadline-clock())),return_when=FIRST_COMPLETED)
            for future in done:
                task=running.pop(future);tid=task["id"];pulsed=False
                try:
                    state=future.result();phase=state.get("phase")
                    if phase not in ("done","review","auto_reverted","blocked_pending_review","released_quota"):
                        raise CoordinatorError("Unverified task outcome: "+str(phase))
                    results.append({"task":tid,"agent":task["agent"],"phase":phase})
                except ar.QuotaExceeded:
                    results.append({"task":tid,"agent":task["agent"],"phase":"released_quota"})
                except Exception as exc:
                    with ar.coordination_lock():
                        current=records(root).get(tid,{})
                        if (current.get("status")!="blocked" or ar.dirty_paths()
                                or git(root,"branch","--show-current")!="main"):
                            cancelled.set()
                            ar.cancel_budget(cancelled)
                            raise CoordinatorError("Unsafe runner failure; session stopped: "+str(exc)) from exc
                    results.append({"task":tid,"agent":task["agent"],"phase":"blocked","reason":str(exc)[:300]})
        # Include every worker result even when the deadline was reached while waiting.
        for future,task in list(running.items()):
            try:state=future.result();phase=state.get("phase","blocked")
            except Exception as exc:phase="interrupted";state={"details":str(exc)[:300]}
            results.append({"task":task["id"],"agent":task["agent"],"phase":phase,"canonical_status":records(root).get(task["id"],{}).get("status"),"details":state.get("details","")})
    return {"attempted":len(attempted),"prerequisite_blocks":prerequisite_blocks,"results":results,"remaining":queue_snapshot(root,agents,include_art),
            "limit_reached":len(attempted)>=max_tasks,"deadline_reached":clock()>=deadline}


def preflight(root,agents):
    missing=[name for name in ["git","gh",*agents] if shutil.which(name) is None]
    if missing:raise CoordinatorError("Missing required CLI: "+", ".join(missing))
    with bind_runner(root):ar.execution_gate(ar.read_json(ar.CONFIG,{}))


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument("--agents",nargs="+",choices=["codex","claude"],default=["codex","claude"])
    parser.add_argument("--max-tasks",type=int,default=10)
    parser.add_argument("--max-minutes",type=float,default=150)
    parser.add_argument("--include-art",action="store_true")
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args(argv)
    if len(set(args.agents))!=len(args.agents) or args.max_tasks<1 or not math.isfinite(args.max_minutes) or args.max_minutes<=0:
        parser.error("Unique agents and positive session limits required")
    source=args.source.resolve()
    if args.dry_run:
        print(json.dumps({"dry_run":True,"tasks":queue_snapshot(source,args.agents,args.include_art)},indent=2))
        return 0
    started=time.monotonic();deadline=started+args.max_minutes*60
    preflight(source,args.agents)
    with repository_lease(source):
        root=coordinator(source,deadline)
        remaining=(deadline-time.monotonic())/60
        if remaining<=0:raise CoordinatorError("Session expired preparing coordinator")
        with bind_runner(root):
            local=ar.LOCAL;local.mkdir(parents=True,exist_ok=True)
            dest=local/("manual-session-"+str(time.time_ns())+".json")
            try:
                summary=run_batch(root,args.agents,args.max_tasks,remaining,args.include_art)
            except BaseException as exc:
                summary={"session_status":"interrupted","error":str(exc)[:500],
                         "remaining":queue_snapshot(root,args.agents,args.include_art)}
                dest.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n")
                print("Interrupted session evidence: "+str(dest),file=sys.stderr)
                raise
            dest.write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8",newline="\n")
            print(json.dumps({"summary":str(dest),"attempted":summary["attempted"],"results":summary["results"]},indent=2))
    return 0


if __name__=="__main__":
    try:sys.exit(main())
    except Busy as exc:print(str(exc));sys.exit(0)
    except (CoordinatorError,OSError,ValueError,subprocess.SubprocessError) as exc:
        print("Manual runner: "+str(exc),file=sys.stderr);sys.exit(1)
