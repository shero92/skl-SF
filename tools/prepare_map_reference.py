#!/usr/bin/env python3
"""Register a new AI room reference image and create a safe, editable draft job.

This step does NOT pretend to segment a room image. The AI/artist must identify
blocks and create missing independent PNGs, review composition, then move the
completed manifest into intake/pending with analysis_status=reviewed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from map_factory_cli import ROOT, check_id, digest_json, get_latest, registry, PRESET_NAMES

REFERENCES=Path("map_factory/references")
DRAFTS=Path("map_factory/intake/drafts")


def prepare(root: Path, source: Path, map_id: str, mode: str,
            preset: str | None = None, from_map: str | None = None):
    check_id(map_id)
    if mode not in ("create", "patch", "clone"):
        raise ValueError("Invalid map job mode")
    root=root.resolve()
    source=source.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() not in (".png",".jpeg",".jpg",".webp"):
        raise ValueError("Unsupported reference image")
    with Image.open(source) as im:
        im.load()
        width,height=im.size
        if not(128<=width<=8192 and 128<=height<=8192):
            raise ValueError("Image dimensions out of bounds")
    image_sha=hashlib.sha256(source.read_bytes()).hexdigest()
    reg=registry(root)
    manifest={"mode":mode,"map_id":map_id,"analysis_status":"pending_review",
              "note":"Reference preserved; AI segmentation/asset QA not completed.",
              "source_image":{
                  "path":None,
                  "sha256":image_sha,
                  "pixel_size":[width,height],
                  "status":"awaiting_ai_block_analysis"
              },
              "assets":[], "changes":[]}
    if mode=="create":
        if map_id in reg["maps"]:
            raise ValueError("Map exists; use patch mode")
        if preset not in PRESET_NAMES:
            raise ValueError("Choose a valid preset: " + ", ".join(PRESET_NAMES))
        manifest["preset"]=preset
    elif mode=="patch":
        snapshot=get_latest(root,map_id)
        manifest["base_version"]=snapshot["version"]
        manifest["base_sha256"]=digest_json(snapshot)
    else:
        if map_id in reg["maps"]:
            raise ValueError("New cloned map ID already exists")
        if from_map is None:
            raise ValueError("Clone mode needs --from-map")
        latest=get_latest(root,from_map)
        manifest["from_map"]=from_map
        manifest["source_parent_version"]=latest["version"]
        manifest["source_parent_sha256"]=digest_json(latest)
    image_dest=root/REFERENCES/(map_id+"_"+image_sha[:12]+source.suffix.lower())
    draft=root/DRAFTS/(map_id+"_"+image_sha[:12]+".json")
    if draft.exists():
        raise ValueError("Draft already prepared; avoid silently overwriting its analysis")
    image_dest.parent.mkdir(parents=True,exist_ok=True)
    draft.parent.mkdir(parents=True,exist_ok=True)
    if image_dest.exists():
        if hashlib.sha256(image_dest.read_bytes()).hexdigest()!=image_sha:
            raise ValueError("Reference filename hash conflict")
    else:
        shutil.copyfile(source,image_dest)
    manifest["source_image"]["path"]=image_dest.relative_to(root).as_posix()
    draft.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8",newline="\n")
    return draft.relative_to(root).as_posix(),manifest


def main():
    parser=argparse.ArgumentParser(description="Prepare map reference and AI block analysis draft")
    parser.add_argument("--image",type=Path,required=True)
    parser.add_argument("--map-id",required=True)
    parser.add_argument("--mode",choices=["create","clone","patch"],required=True)
    parser.add_argument("--preset",choices=PRESET_NAMES)
    parser.add_argument("--from-map")
    args=parser.parse_args()
    draft,manifest=prepare(ROOT,args.image,args.map_id,args.mode,args.preset,args.from_map)
    print(json.dumps({
        "draft":draft,"reference":manifest["source_image"],
        "analysis_status":"pending_review",
        "next":"Analyze parts, reuse IDs, attach missing PNGs, add changes, set analysis_status=reviewed and move draft to pending."
    },ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
