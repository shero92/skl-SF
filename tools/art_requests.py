#!/usr/bin/env python3
"""Owner GitHub Issue handoff for metadata-defined ART requests. No image access."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
REQUESTS=ROOT/".agents/graphics/requests"

def fields(text):
    if not text.startswith("---\n"):raise ValueError("Invalid ART frontmatter")
    result={}
    for row in text.split("---",2)[1].splitlines():
        if ":" in row:
            k,v=row.split(":",1)
            result[k.strip()]=v.strip()
    return result

def git(*args):
    p=subprocess.run(["git",*args],cwd=ROOT,capture_output=True,text=True)
    if p.returncode:raise RuntimeError("Git command failed: "+str(args[0]))
    return p.stdout.strip()

def create(args):
    if git("branch","--show-current")!="main" or git("status","--porcelain"):
        raise RuntimeError("Clean main required")
    task=next((ROOT/".agents/tasks").glob(args.task+"_*.md"),None)
    if task is None:raise ValueError("Unknown TASK ID")
    if not re.fullmatch(r"[a-z][a-z0-9_]{4,80}",args.dedupe_key):
        raise ValueError("Invalid dedupe_key")
    if any(fields(p.read_text(encoding="utf8")).get("dedupe_key")==args.dedupe_key for p in REQUESTS.glob("ART-*.md")):
        raise ValueError("Duplicate art request")
    names=[x.strip() for x in args.filenames.split(",")]
    if len(names)!=4 or len(set(names))!=4 or any(not re.fullmatch(r"[A-Za-z0-9_-]+\.png",n) for n in names):
        raise ValueError("Four uniquely named PNG views required")
    if not re.fullmatch(r"\d{1,4}x\d{1,4}",args.size):
        raise ValueError("Provide native WxH size")
    ids=[int(m.group(1)) for p in REQUESTS.glob("ART-*.md") if (m:=re.match(r"ART-(\d{4})_",p.name))]
    num=next(i for i in range(1,10000) if i not in ids)
    aid="ART-"+f"{num:04d}"
    paths=[".agents/graphics/deliveries/"+aid+"/"+n for n in names]
    payload="\n".join([
        "---","id: "+aid,"status: requested","owner: graphics-specialist",
        "task: "+args.task,"dedupe_key: "+args.dedupe_key,
        "existing_asset_ids: "+args.existing_ids,"output_paths: "+", ".join(paths),
        "issue: none","---","# "+args.title,"",
        "## Reference / native specification",
        "- Reference goal image: "+args.reference,
        "- Pixel size: "+args.size,
        "- Palette: "+args.palette,
        "- Orientations: north, east, south, west (four distinct upright views)",
        "- Shadows: "+args.shadows,
        "- Layers: "+args.layers,"",
        "## Exact delivery filenames",*("- "+p for p in paths),"",
        "## Required metadata",
        "- manifest.json: request_id, files(path, sha256), assets(catalog entries)",
        "- One complete asset_index-compatible record per PNG: id, name, category, subtype, texture_path, pixel_size, origin, collision, shadow, tags, reusable, source",
        "- Each source must declare kind=owner_delivery and the exact delivery filename",
        "- Preserve native pixel detail; no scripted generation or automated visual approval","",
        "## Quality criteria",args.criteria,
        "- Transparent RGBA pixels, four correct perspectives, palette matched to authentic source",
        "- No neighbor sprites, character/gameplay/UI changes or unknown baked shadows",""
    ]) 
    (REQUESTS/(aid+"_"+args.dedupe_key+".md")).write_text(payload,encoding="utf8")
    text=task.read_text(encoding="utf8")
    text=re.sub(r"(?m)^status: .+$","status: blocked_on_art",text,count=1)
    text=re.sub(r"(?m)^art_request: .+$","art_request: "+aid,text,count=1)
    task.write_text(text,encoding="utf8")
    print("Created "+aid+"; commit planning changes before issuing owner notification")

def notify():
    cfg=json.loads((ROOT/".agents/planner/config.json").read_text(encoding="utf8"))
    if not cfg.get("graphics_issue_enabled",False):
        print("Issue notifications disabled until supervised setup")
        return
    if git("branch","--show-current")!="main" or git("status","--porcelain"):
        raise RuntimeError("Clean main required")
    def gh(*args):
        p=subprocess.run(["gh",*args],cwd=ROOT,capture_output=True,text=True)
        if p.returncode:raise RuntimeError("gh "+args[0]+" failed")
        return p.stdout.strip()
    gh("label","create","art-needed","--color","D93F0B","--force")
    updates=[]
    for req in sorted(REQUESTS.glob("ART-*.md")):
        content=req.read_text(encoding="utf8")
        data=fields(content)
        if data.get("status") not in ("requested","blocked_reference") or data.get("issue","none")!="none":
            continue
        rid=data["id"]
        url=gh("issue","create","--title","Art needed: "+rid,
               "--assignee","shero92","--label","art-needed",
               "--body","Owner must deliver four PNGs and metadata; request: "+req.relative_to(ROOT).as_posix())
        m=re.search(r"/issues/(\d+)",url)
        if not m:raise RuntimeError("Issue URL missing")
        marker="issue: none"
        if marker in content:content=content.replace(marker,"issue: "+m.group(1),1)
        else:content=content.replace("output_paths: "+data["output_paths"],
                      "output_paths: "+data["output_paths"]+"\nissue: "+m.group(1),1)
        req.write_text(content,encoding="utf8")
        updates.append(req.relative_to(ROOT).as_posix())
    if updates:
        git("add","--",*updates)
        git("commit","-m","chore: link ART requests to owner issues","-m","Agent: chatgpt\nCost-USD: unknown")
        git("push","origin","main")
    print("Owner issues created:",len(updates))

def main():
    ap=argparse.ArgumentParser()
    commands=ap.add_subparsers(dest="command",required=True)
    new=commands.add_parser("request")
    for key in ["task","dedupe-key","title","reference","size","palette","shadows","layers","filenames","criteria"]:
        new.add_argument("--"+key,required=True)
    new.add_argument("--existing-ids",default="none")
    commands.add_parser("notify")
    a=ap.parse_args()
    create(a) if a.command=="request" else notify()

if __name__=="__main__":
    try:main()
    except (ValueError,RuntimeError,OSError) as e:
        print("art requests:",e,file=sys.stderr)
        sys.exit(1)
