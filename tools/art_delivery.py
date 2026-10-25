#!/usr/bin/env python3
"""Validate owner-delivered art by PNG headers/hashes/metadata WITHOUT image viewing.

Integration is OFF by default and only runs on clean local main when explicitly enabled.
Never synthesizes, repaints or changes delivered PNG pixels.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REQUESTS=ROOT/".agents/graphics/requests"
DELIVERIES=ROOT/".agents/graphics/deliveries"
CATALOG=ROOT/"map_factory/metadata/asset_index.json"
CONFIG=ROOT/".agents/planner/config.json"
VALID_CATEGORIES={"architecture","environment","floors","walls","objects","furniture","decor","shadows"}
PNG_SIG=b"\x89PNG\r\n\x1a\n"

def png_properties(p):
    with p.open("rb") as fp:
        data=fp.read(33)
    if len(data)<33 or data[:8]!=PNG_SIG or data[12:16]!=b"IHDR":
        raise ValueError("Not a valid PNG header: "+str(p))
    width,height,depth,color=struct.unpack(">IIBB",data[16:26])
    if not (1<=width<=4096 and 1<=height<=4096 and depth==8 and color in (4,6)):
        raise ValueError("RGBA/gray-alpha PNG with valid native size required: "+str(p))
    return [width,height]

def request_fields(path):
    data=path.read_text(encoding="utf-8")
    if not data.startswith("---\n"):raise ValueError("Missing ART frontmatter")
    fields={}
    for line in data.split("---",2)[1].splitlines():
        if ":" in line:
            key,val=line.split(":",1)
            fields[key.strip()]=val.strip()
    return fields,data

def collect(root=ROOT):
    catalog=json.loads((root/"map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))
    current={a["id"] for a in catalog["assets"]}
    outputs=[]
    for req in sorted((root/".agents/graphics/requests").glob("ART-*.md")):
        fields,raw=request_fields(req)
        if fields.get("status")!="delivered":
            continue
        ident=fields["id"]
        folder=root/".agents/graphics/deliveries"/ident
        manifest_file=folder/"manifest.json"
        if not manifest_file.is_file():raise ValueError(ident+": missing delivery manifest")
        m=json.loads(manifest_file.read_text(encoding="utf-8"))
        if m.get("request_id")!=ident:raise ValueError(ident+": invalid manifest request ID")
        expected=[x.strip() for x in fields["output_paths"].split(",")]
        assets=m.get("assets")
        files=m.get("files")
        if not isinstance(files,list) or not isinstance(assets,list) or len(assets)!=len(expected):
            raise ValueError(ident+": require 1 metadata asset per expected PNG")
        if sorted(x.get("path","") for x in files)!=sorted(expected):
            raise ValueError(ident+": expected directional image filenames do not match")
        bypath={x["path"]:x for x in files}
        group=[]
        for asset in assets:
            for key in ("id","name","category","subtype","texture_path","pixel_size","origin","collision","shadow","tags","reusable","source"):
                if key not in asset:raise ValueError(ident+": metadata missing "+key)
            rid=asset["id"]
            if not isinstance(rid,str) or not re.fullmatch(r"[A-Z][0-9]{3,4}",rid) or rid in current:
                raise ValueError(ident+": duplicate/malformed catalog ID")
            current.add(rid)
            category=asset["category"]
            if category not in VALID_CATEGORIES:raise ValueError(ident+": forbidden art category")
            dest=asset["texture_path"]
            if not isinstance(dest,str) or not dest.startswith("res://map_factory/parts/"+category+"/"):
                raise ValueError(ident+": bad production asset path")
            production=root/dest.removeprefix("res://")
            if production.exists() or production.suffix.lower()!=".png" or ".." in production.parts:
                raise ValueError(ident+": refusing production art overwrite")
            source=asset["source"]
            if not isinstance(source,dict) or source.get("kind")!="owner_delivery":
                raise ValueError(ident+": provenance must be owner_delivery")
            source_path=source.get("file")
            if source_path not in expected:raise ValueError(ident+": source must match delivered filename")
            png=root/source_path
            if not png.is_file():raise ValueError(ident+": missing delivered file")
            if hashlib.sha256(png.read_bytes()).hexdigest()!=bypath[source_path].get("sha256"):
                raise ValueError(ident+": SHA-256 mismatch")
            if png_properties(png)!=asset["pixel_size"]:
                raise ValueError(ident+": PNG dimensions differ from metadata")
            origin=asset["origin"]
            if not isinstance(origin,list) or len(origin)!=2 or any(not isinstance(x,int) for x in origin):
                raise ValueError(ident+": invalid origin")
            group.append((source_path,dest,asset))
        outputs.append((req,fields,m,group))
    return catalog,outputs

def integrate():
    cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
    if not cfg.get("art_integration_enabled",False):
        raise RuntimeError("Art integration disabled until supervised validation")
    def call(*args):
        r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True)
        if r.returncode:raise RuntimeError("Command failed: "+str(args[:2]))
        return r.stdout.strip()
    if call("git","branch","--show-current")!="main" or call("git","status","--porcelain"):
        raise RuntimeError("Clean main required; integration cannot run inside agent branch")
    catalog,batches=collect()
    if not batches:
        print("No delivered art to integrate")
        return
    import tempfile
    from contextlib import contextmanager
    lock=ROOT/".agents/monitoring/.local/merge.lock"
    lock.parent.mkdir(parents=True,exist_ok=True)
    try:
        with lock.open("x",encoding="utf8") as h:h.write("art delivery")
    except FileExistsError:
        raise RuntimeError("Merge lock held; abort integration")
    try:
        call("git","pull","--ff-only","origin","main")
        catalog,batches=collect()
        for req,fields,manifest,group in batches:
            for source,dest,meta in group:
                destination=ROOT/dest.removeprefix("res://")
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/source,destination)
                catalog["assets"].append(meta)
                call("git","add","--",str(destination.relative_to(ROOT)).replace("\\","/"))
            fields_before=req.read_text(encoding="utf8")
            req.write_text(fields_before.replace("status: delivered","status: integrated",1),encoding="utf8")
            call("git","add","--",str(req.relative_to(ROOT)).replace("\\","/"))
            issue=fields.get("issue")
            if issue and issue.isdigit():
                # Closing issue after commit and successful post-registration validation only.
                pass
        catalog["asset_count"]=len(catalog["assets"])
        CATALOG.write_text(json.dumps(catalog,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        call("git","add","--","map_factory/metadata/asset_index.json")
        call(sys.executable,"tools/agent_workflow.py","--write")
        call(sys.executable,"tools/generate_project_indexes.py","--write")
        call("git","add","-A","--",".agents/project",".agents/graphics/QUEUE.md")
        call("git","commit","-m","chore: register owner-delivered assets without image analysis",
             "-m","Agent: chatgpt\nCost-USD: unknown")
        call("git","push","origin","main")
        for req,fields,manifest,group in batches:
            if fields.get("issue","").isdigit():
                call("gh","issue","close",fields["issue"],"--reason","completed")
        print("Registered",sum(len(g) for _,_,_,g in batches),"owner-delivered assets")
    finally:
        lock.unlink(missing_ok=True)

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check",action="store_true")
    g.add_argument("--integrate",action="store_true")
    opts=p.parse_args()
    if opts.check:
        _,items=collect()
        print(json.dumps({"deliveries_verified":[x[1]["id"] for x in items]}))
    else:
        integrate()

if __name__=="__main__":
    try:main()
    except (ValueError,RuntimeError,KeyError,OSError,json.JSONDecodeError) as e:
        print("art delivery:",e,file=sys.stderr)
        sys.exit(1)
