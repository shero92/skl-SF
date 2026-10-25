#!/usr/bin/env python3
"""One-shot owner goal visual QA. Outside ordinary coding/planning agent sessions.

Real images are accessed ONLY during final comparison (Codex -i documented by owner).
Never mark a long goal final_verified automatically.
"""
import argparse
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

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

def eligible(gid):
    if not re.fullmatch(r"GOAL-\d{4}",gid):
        raise ValueError("Expected GOAL-####")
    d=GOALS/gid
    state=json.loads((d/"state.json").read_text(encoding="utf-8"))
    if state.get("status")!="active" or not state.get("milestones_approved",False):
        raise ValueError("Goal milestones are not approved")
    records=list((ROOT/".agents/tasks").glob("TASK-*.md"))
    relevant=[]
    for f in records:
        text=f.read_text(encoding="utf-8")
        if "**Goal:** "+gid in text or "**Source:** goal:"+gid+":" in text:
            relevant.append(text)
    if not relevant or any(not re.search(r"(?m)^status: done$",t) for t in relevant):
        raise ValueError("Cannot verify an unfinished goal")
    return d,state

def render(gid):
    d,state=eligible(gid)
    if state.get("final_comparison_run_at"):
        raise ValueError("Final comparison already recorded for this goal")
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    if os.name!="nt":raise RuntimeError("Run Godot capture on owner Windows desktop")
    if command(["git","branch","--show-current"]).stdout.strip()!="main":
        raise RuntimeError("Use main for final verification")
    version=json.loads((ROOT/"map_factory/maps/index.json").read_text(encoding="utf-8"))["maps"]["hero_room_01"]["version"]
    if version != 10:
        # The historical capture script currently lists v0001-v0010 explicitly.
        # Refuse stale images until the capture script is updated to current map version.
        raise ValueError("Current Hero Room version is "+str(version)+" but factory capture script ends at v0010")
    with tempfile.TemporaryDirectory(prefix="skl-qa-") as tmp:
        tmp=Path(tmp)
        # Godot needs image assets to render, so its isolated process sees them,
        # but NO CODING AGENT executes in this worktree.
        workdir=tmp/"project"
        command(["git","worktree","add","--detach",str(workdir),"HEAD"])
        try:
            cmd=[cfg.get("godot_executable","godot")]
            if cfg.get("godot_qa_headless",True):cmd.append("--headless")
            cmd+=["--path",str(workdir),"--rendering-driver","opengl3",
                  "--script","res://tools/capture_map_previews.gd"]
            command(cmd,workdir,timeout=1200)
            source=workdir/"docs/previews/map_factory_renders/hero_room_01_v0010.png"
            if not source.is_file() or source.stat().st_size<10000:
                raise RuntimeError("Real Godot screenshot missing; do NOT substitute generated art")
            dest=OUTPUT/gid/"hero_room_final.png"
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(source,dest)
            print(dest.relative_to(ROOT).as_posix())
        finally:
            command(["git","worktree","remove","--force",str(workdir)])

def compare(gid):
    folder,state=eligible(gid)
    if state.get("final_comparison_started_at"):
        raise ValueError("Comparison already attempted once; owner must explicitly approve any rerun")
    reference=[p for p in (folder/"references").iterdir()
               if p.suffix.lower() in {".png",".jpg",".jpeg",".webp"} and p.is_file()]
    if len(reference)!=1:
        raise ValueError("Final comparison requires exactly one authentic goal reference image")
    image=OUTPUT/gid/"hero_room_final.png"
    if not image.is_file():raise ValueError("Render the actual Godot room before final comparison")
    state["final_comparison_started_at"]=datetime.now(timezone.utc).isoformat()
    (folder/"state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
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
            "--skip-git-repo-check","-i",str(reference[0]),"-i",str(image),
            "--output-last-message",str(output),instr],
            cwd=tmp,env=env,timeout=240,capture_output=True,text=True)
        if process.returncode or not output.is_file():
            raise RuntimeError("Final visual comparison failed; no completion notification")
        obj=json.loads(output.read_text(encoding="utf-8"))
        if not isinstance(obj,dict) or set(obj)!={"differences","summary"} or not isinstance(obj["differences"],list):
            raise ValueError("Malformed final comparison JSON")
        if len(obj["differences"])>12 or any(not isinstance(x,str) or len(x)>600 for x in obj["differences"]):
            raise ValueError("Comparison differences invalid")
        payload={"goal":gid,"reference":reference[0].relative_to(ROOT).as_posix(),
                 "render":image.relative_to(ROOT).as_posix(),"comparison":obj,
                 "owner_final_signoff":False,"at":datetime.now(timezone.utc).isoformat()}
        RESULTS.mkdir(parents=True,exist_ok=True)
        (RESULTS/(gid+".json")).write_text(json.dumps(payload,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
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
                dest.write_text(json.dumps(request,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")

        state["final_comparison_run_at"]=payload["at"]
        (folder/"state.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
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
    p.add_argument("action",choices=["render","compare","notify"])
    p.add_argument("goal")
    a=p.parse_args()
    if a.action=="render":render(a.goal)
    elif a.action=="compare":compare(a.goal)
    else:notify(a.goal)

if __name__=="__main__":
    try:main()
    except (ValueError,RuntimeError,OSError,FileNotFoundError,subprocess.TimeoutExpired) as e:
        print("goal visual QA:",e,file=sys.stderr)
        sys.exit(1)
