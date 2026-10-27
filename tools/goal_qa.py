#!/usr/bin/env python3
"""One-shot owner goal visual QA. Outside ordinary coding/planning agent sessions.

Real images are accessed ONLY during final comparison (Codex -i documented by owner).
Never mark a long goal final_verified automatically.
"""
import argparse
import hashlib
import struct
import uuid
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from task_evidence import check_task

ROOT=Path(__file__).resolve().parents[1]
GOALS=ROOT/".agents/planner/goals"
OUTPUT=ROOT/".agents/qa/renders"
RESULTS=ROOT/".agents/qa/results"
CONFIG=ROOT/".agents/planner/config.json"

def command(args,cwd=ROOT,env=None,timeout=900):
    p=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout,
                     encoding="utf-8",errors="replace")
    if p.returncode:
        raise RuntimeError("Command failed: "+str(args[0])+" ("+str(p.returncode)+")")
    return p

def goal_state(gid):
    if not re.fullmatch(r"GOAL-\d{4}",gid):
        raise ValueError("Expected GOAL-####")
    d=GOALS/gid
    state=json.loads((d/"state.json").read_text(encoding="utf-8"))
    if state.get("status")!="active" or not state.get("milestones_approved",False):
        raise ValueError("Goal milestones are not approved")
    return d,state


def eligible(gid):
    d,state=goal_state(gid)
    relevant=[]
    required=state.get("qa_required_tasks")
    if required is not None:
        if (state.get("qa_required_tasks_approved") is not True or not isinstance(required,list)
                or not required or len(set(required))!=len(required)
                or any(not isinstance(t,str) or not re.fullmatch(r"TASK-\d{4}",t) for t in required)):
            raise ValueError("Final QA requires an approved nonempty task prerequisite list")
        for tid in required:
            matches=list((ROOT/".agents/tasks").glob(tid+"_*.md"))
            if len(matches)!=1:
                raise ValueError("Final QA prerequisite task missing: "+tid)
            relevant.append(matches[0].read_text(encoding="utf-8"))
    for f in [] if required is not None else (ROOT/".agents/tasks").glob("TASK-*.md"):
        text=f.read_text(encoding="utf-8")
        if "**Goal:** "+gid in text or "**Source:** goal:"+gid+":" in text:
            relevant.append(text)
    if not relevant or any(not re.search(r"(?m)^status: done$",t) for t in relevant):
        raise ValueError("Cannot verify an unfinished goal")
    return d,state


def capture_spec(map_id="hero_room_01", *, root=None):
    root=ROOT if root is None else Path(root)
    if not re.fullmatch(r"[a-z][a-z0-9_]{2,63}",map_id):
        raise ValueError("Invalid map ID")
    registry=json.loads((root/"map_factory/maps/index.json").read_text(encoding="utf-8"))
    record=registry["maps"][map_id]
    version=record["version"]
    if type(version) is not int or version < 1:
        raise ValueError("Invalid registered version")
    snapshot=f"map_factory/maps/{map_id}/versions/v{version:04d}.json"
    data=json.loads((root/snapshot).read_text(encoding="utf-8"))
    digest=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
    if data.get("map_id")!=map_id or data.get("version")!=version or digest!=record.get("snapshot_sha256"):
        raise ValueError("Registered snapshot identity/hash mismatch")
    return {"id":map_id,"version":version,"snapshot":snapshot,"snapshot_sha256":digest,
            "file":f"{map_id}_v{version:04d}.png","canvas_size":data["canvas_size"]}


def verify_capture(source, receipt, spec, nonce):
    if not isinstance(nonce,str) or not nonce:raise ValueError("Capture run identity required")
    if not source.is_file() or not receipt.is_file():
        raise RuntimeError("Real Godot screenshot or receipt missing")
    proof=json.loads(receipt.read_text(encoding="utf-8"))
    expected={"capture_id":nonce,"map_id":spec["id"],"version":spec["version"],
              "snapshot_sha256":spec["snapshot_sha256"],"canvas_size":spec["canvas_size"],
              "camera_position":[spec["canvas_size"][0]/2,spec["canvas_size"][1]/2],"camera_zoom":[1,1]}
    if any(proof.get(k)!=v for k,v in expected.items()):
        raise ValueError("Stale/mismatched Godot capture receipt")
    with source.open("rb") as handle:
        header=handle.read(24)
    if len(header)!=24 or header[:8]!=b"\x89PNG\r\n\x1a\n" or header[12:16]!=b"IHDR":
        raise ValueError("Godot capture is not a PNG")
    if list(struct.unpack(">II",header[16:24]))!=spec["canvas_size"]:
        raise ValueError("Capture dimensions do not match viewport")
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    if proof.get("render_sha256")!=digest:
        raise ValueError("Capture hash does not match receipt")
    return proof


def render(gid, *, intermediate=False):
    _,state=goal_state(gid) if intermediate else eligible(gid)
    if not intermediate and state.get("final_comparison_run_at"):
        raise ValueError("Final comparison already recorded for this goal")
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    if os.name!="nt":raise RuntimeError("Run Godot capture on owner Windows desktop")
    if not intermediate and command(["git","branch","--show-current"]).stdout.strip()!="main":
        raise RuntimeError("Use main for final verification")
    spec=capture_spec()
    revision=command(["git","rev-parse","HEAD"]).stdout.strip()
    nonce=uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix="skl-qa-") as tmp:
        workdir=Path(tmp)/"project"
        # Only the deterministic rendering process sees production resources;
        # model sessions stay in their separate image-free coding worktrees.
        command(["git","worktree","add","--detach",str(workdir),revision])
        try:
            if capture_spec(spec["id"],root=workdir)!=spec:
                raise ValueError("Committed render snapshot differs from requested revision")
            request=workdir/".agents/monitoring/.local/capture-request.json"
            request.parent.mkdir(parents=True,exist_ok=True)
            request.write_text(json.dumps({"capture_id":nonce,"cases":[spec]})+"\n",encoding="utf-8",newline="\n")
            executable=cfg.get("godot_executable","godot")
            # Import classes/resources first. Capture requires a real renderer;
            # --headless uses the dummy display and cannot produce valid pixels.
            command([executable,"--headless","--path",str(workdir),"--editor","--quit"],workdir,timeout=1200)
            cmd=[executable,"--path",str(workdir),"--rendering-method","gl_compatibility",
                 "--rendering-driver","opengl3","--script","res://tools/capture_map_previews.gd",
                 "--","--capture-manifest","res://.agents/monitoring/.local/capture-request.json"]
            command(cmd,workdir,timeout=1200)
            source=workdir/"docs/previews/map_factory_renders"/spec["file"]
            proof=verify_capture(source,source.with_suffix(".json"),spec,nonce)
            folder=OUTPUT/gid
            folder.mkdir(parents=True,exist_ok=True)
            dest=folder/(spec["file"] if intermediate else "hero_room_final.png")
            shutil.copyfile(source,dest)
            proof.update({"commit":revision,"intermediate":intermediate,"owner_final_signoff":False})
            dest.with_suffix(".json").write_text(json.dumps(proof,indent=2)+"\n",encoding="utf-8",newline="\n")
            print(dest.relative_to(ROOT).as_posix())
            return proof
        finally:
            command(["git","worktree","remove","--force",str(workdir)])


def authenticated_reference(gid):
    _,state=goal_state(gid)
    manifest=state.get("reference_manifest")
    if not manifest:
        raise ValueError("Authenticated reference manifest required before image comparison")
    errors=check_task({"evidence_manifest":manifest},ROOT)
    if errors:raise ValueError("Reference identity check failed: "+"; ".join(errors))
    proof=json.loads((ROOT/manifest).read_text(encoding="utf-8"))
    references=[item for item in proof["requirements"]if item.get("kind")=="reference"]
    if len(references)!=1:raise ValueError("Exactly one authenticated source reference required")
    return ROOT/references[0]["path"]


def compare(gid):
    folder,state=eligible(gid)
    if state.get("final_comparison_started_at"):
        raise ValueError("Comparison already attempted once; owner must explicitly approve any rerun")
    reference=authenticated_reference(gid)
    image=OUTPUT/gid/"hero_room_final.png"
    if not image.is_file():raise ValueError("Render the actual Godot room before final comparison")
    receipt=image.with_suffix(".json")
    if not receipt.is_file():raise ValueError("Actual capture identity receipt required")
    captured=json.loads(receipt.read_text(encoding="utf-8"))
    verify_capture(image,receipt,capture_spec(),captured.get("capture_id"))
    if captured.get("intermediate") is not False or captured.get("commit")!=command(["git","rev-parse","HEAD"]).stdout.strip():
        raise ValueError("Final comparison requires a fresh final capture of this commit")
    state["final_comparison_started_at"]=datetime.now(timezone.utc).isoformat()
    (folder/"state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8",newline="\n")
    with tempfile.TemporaryDirectory(prefix="skl-qa-text-") as tmp:
        output=Path(tmp)/"differences.json"
        instr=("Final goal visual verification ONLY. Compare the first attached authentic user "
               "reference with the second attached REAL Godot Map Factory render. "
               "Return ONLY JSON with keys differences (array of short specific visible mismatches) "
               "and summary (string). No code edits, no visual assets generated. "
               "Never claim an artistic match without evidence. This is not owner signoff.")
        env=os.environ.copy()
        env.pop("OPENAI_API_KEY",None);env.pop("ANTHROPIC_API_KEY",None)
        process=subprocess.run(["codex","exec","--sandbox","read-only",
            "--skip-git-repo-check","-i",str(reference),"-i",str(image),
            "--output-last-message",str(output),instr],
            cwd=tmp,env=env,timeout=240,capture_output=True,text=True)
        if process.returncode or not output.is_file():
            raise RuntimeError("Final visual comparison failed; no completion notification")
        obj=json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(obj,dict) or set(obj)!={"differences","summary"} or not isinstance(obj["differences"],list):
            raise ValueError("Malformed final comparison JSON")
        if len(obj["differences"])>12 or any(not isinstance(x,str) or len(x)>600 for x in obj["differences"]):
            raise ValueError("Comparison differences invalid")
        payload={"goal":gid,"reference":reference.relative_to(ROOT).as_posix(),
                 "render":image.relative_to(ROOT).as_posix(),"comparison":obj,
                 "owner_final_signoff":False,"at":datetime.now(timezone.utc).isoformat()}
        RESULTS.mkdir(parents=True,exist_ok=True)
        (RESULTS/(gid+".json")).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
        # Reviewable investigation requests: do not guess which code or sprite is at fault.
        requests=ROOT/".agents/planner/requests"
        requests.mkdir(parents=True,exist_ok=True)
        import hashlib
        for difference in obj["differences"]:
            request={"status":"draft","title":"Investigate visible Hero Room mismatch",
                     "problem":difference,"file":"map_factory/maps/hero_room_01/latest.json",
                     "done_when":"Locate actual cause and document a safe evidence-backed correction",
                     "test":"python tools/map_factory_cli.py validate",
                     "priority":"normal","kind":"investigation","agent":"auto",
                     "origin":gid+" final QA"}
            digest=hashlib.sha256((gid+"|"+difference).encode()).hexdigest()[:12]
            dest=requests/("REQ-"+digest+".json")
            if not dest.exists():
                dest.write_text(json.dumps(request,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")

        state["final_comparison_run_at"]=payload["at"]
        (folder/"state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8",newline="\n")
        print("Wrote final comparison evidence; owner must review: "+gid)
        print("Visible differences (investigation candidates): "+str(len(obj["differences"])))
        # Owner may turn differences into specific tasks via the canonical request command.
        # Do not invent causal files/lines from image differences alone.
        return payload

def notify(gid):
    record=RESULTS/(gid+".json")
    if not record.is_file():raise RuntimeError("Run final compare first")
    data=json.loads(record.read_text(encoding="utf-8"))
    body="Owner final visual review required.\nReference: "+data["reference"]+"\nReal Godot render: "+data["render"]+"\nJSON comparison: "+record.relative_to(ROOT).as_posix()+"\nReview visual differences and approve or enter investigation TASKs. No automatic signoff."
    command(["gh","issue","create","--title","Goal final visual signoff: "+gid,
             "--assignee","shero92","--body",body])
    print("Owner notified on GitHub")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["capture","render","compare","notify"])
    p.add_argument("goal")
    a=p.parse_args()
    if a.action=="capture":render(a.goal,intermediate=True)
    elif a.action=="render":render(a.goal)
    elif a.action=="compare":compare(a.goal)
    else:notify(a.goal)

if __name__=="__main__":
    try:main()
    except (ValueError,RuntimeError,OSError,FileNotFoundError,subprocess.TimeoutExpired) as e:
        print("goal visual QA:",e,file=sys.stderr)
        sys.exit(1)
