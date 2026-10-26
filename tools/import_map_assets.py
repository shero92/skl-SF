#!/usr/bin/env python3
"""Import individual map artwork referenced by an AI-authored manifest.

The AI (or artist) must generate separate transparent PNGs first.
This importer NEVER segments a whole-room screenshot by guessing.
Character, UI and shadow categories are disallowed.
Existing IDs are never overwritten: changed images go to candidates for QA.
"""
import csv
import hashlib
import json
from pathlib import Path
import re
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
INDEX=Path("map_factory/metadata/asset_index.json")
QUEUE=Path("map_factory/metadata/production_queue.csv")
SOURCE=Path("map_factory/intake/assets")
PREF={"floors":"F","walls":"W","architecture":"A","stairs":"ST",
      "environment":"E","furniture":"P","objects":"O","vegetation":"V","decor":"D"}

def valid_repo_path(root, path, prefix):
    if not isinstance(path,str) or "\\" in path:
        raise ValueError("Bad PNG path")
    absolute=(root/path).resolve()
    if not absolute.is_relative_to((root/prefix).resolve()):
        raise ValueError("PNG source must be inside "+str(prefix))
    if not absolute.is_file() or absolute.suffix.lower()!=".png":
        raise ValueError("Missing separate PNG "+str(path))
    return absolute

def import_assets(root: Path, assets: list):
    if not assets:
        return {"installed":[],"candidates":[],"unchanged":[]}
    source_index=root/INDEX
    index=json.loads(source_index.read_text(encoding="utf-8"))
    by={a["id"]:a for a in index["assets"]}
    installed=[];candidates=[];unchanged=[]
    seen=set()
    for item in assets:
        ident=str(item["id"])
        category=str(item["category"])
        if category not in PREF:
            raise ValueError("Map-only factory cannot import "+category)
        if not re.fullmatch(re.escape(PREF[category])+r"[0-9]{3,5}",ident):
            raise ValueError("ID prefix does not match category: "+ident)
        if ident in seen:
            raise ValueError("Repeated asset ID in bundle: "+ident)
        seen.add(ident)
        src=valid_repo_path(root,item["file"],SOURCE)
        if src.stat().st_size>18_000_000:
            raise ValueError("PNG exceeds 18 MB: "+ident)
        with Image.open(src) as im:
            im.load()
            w,h=im.size
            if im.format!="PNG" or not(24<=w<=4096 and 24<=h<=4096):
                raise ValueError("Bad resolution for "+ident)
            a=im.convert("RGBA").getchannel("A")
            amin,amax=a.getextrema()
            if amax<8:
                raise ValueError("Empty alpha image: "+ident)
            if category not in ("floors","environment") and amin==255:
                raise ValueError("Object sprite must have transparent RGBA: "+ident)
        blob=src.read_bytes()
        digest=hashlib.sha256(blob).hexdigest()
        if ident in by:
            existing=by[ident]
            current=root/existing["texture_path"].removeprefix("res://")
            if current.is_file() and hashlib.sha256(current.read_bytes()).hexdigest()==digest:
                unchanged.append(ident)
                continue
            candidate=root/"map_factory/candidates"/category/(ident+"_"+src.name)
            candidate.parent.mkdir(parents=True,exist_ok=True)
            candidate.write_bytes(blob)
            candidates.append({"id":ident,"candidate_path":candidate.relative_to(root).as_posix(),
                               "sha256":digest,"review_required":True})
            continue
        name=str(item["name"]).strip()
        slug=re.sub(r"[^A-Za-z0-9]+","_",name).strip("_")
        if not slug:
            raise ValueError("Invalid asset name")
        dest=root/"map_factory/parts"/category/(ident+"_"+slug+".png")
        if dest.exists():
            raise ValueError("Refusing path overwrite: "+str(dest))
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(blob)
        anchor=item.get("origin",[0,0] if category=="floors" else [w//2,h])
        if not isinstance(anchor,list) or len(anchor)!=2:
            raise ValueError("Invalid origin for "+ident)
        collision=item.get("collision",{"enabled":False,"size":[32,16],"offset":[0,0]})
        shadow=item.get("shadow",{"type":"none","opacity":.25,"offset_x":0,"offset_y":0})
        if not isinstance(collision,dict) or not isinstance(shadow,dict):
            raise ValueError("Invalid collision/shadow")
        record={"id":ident,"name":name,"category":category,
                "subtype":str(item.get("subtype","general")),
                "texture_path":"res://"+dest.relative_to(root).as_posix(),
                "status":"needs_cleanup","pixel_size":[w,h],
                "origin":anchor,"collision":collision,"shadow":shadow,
                "tags":item.get("tags",[category]),"y_sort":category!="floors",
                "reusable":True,
                "source":{"kind":"ai_map_intake","sha256":digest,
                          "original_file":item["file"],"reviewed":False},
                "qa_notes":"Generated independent PNG, pending visual QA; source map image not automatically segmented."}
        index["assets"].append(record)
        by[ident]=record
        installed.append(ident)
    index["asset_count"]=len(index["assets"])
    index["generated_png_count"]=sum(
      (root/a["texture_path"].removeprefix("res://")).is_file()
      for a in index["assets"])
    index["extracted_count"]=index["generated_png_count"]
    source_index.write_text(json.dumps(index,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    with (root/QUEUE).open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f,lineterminator="\n")
        writer.writerow(["id","category","name","status","texture_path"])
        writer.writerows((a["id"],a["category"],a.get("name",a["id"]),a.get("status","planned"),a["texture_path"])
                         for a in index["assets"])
    return {"installed":installed,"candidates":candidates,"unchanged":unchanged}
