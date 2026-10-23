#!/usr/bin/env python3
"""Consume pending AI map manifests, import new map-only blocks, version layouts.

Each manifest is immutable: reusing a filename with changed bytes is forbidden.
The last version is the authoritative base; stale updates fail safely.
"""
from pathlib import Path
import hashlib,json,re,sys
from map_factory_cli import ROOT, clone_map, get_latest, apply, registry
from import_map_assets import import_assets

PENDING=Path("map_factory/intake/pending")
DONE=Path("map_factory/intake/processed")
REFERENCES=Path("map_factory/references")

def process(root=ROOT):
    imported=[]
    for file in sorted((root/PENDING).glob("*.json")):
        if not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}",file.stem):
            raise ValueError("Unsafe manifest name: "+file.name)
        content=file.read_bytes()
        digest=hashlib.sha256(content).hexdigest()
        receipt=root/DONE/file.name
        if receipt.exists():
            prior=json.loads(receipt.read_text())
            if prior.get("manifest_sha256")!=digest:
                raise ValueError("Previously processed manifest was edited: "+file.name)
            continue
        doc=json.loads(content)
        if not isinstance(doc,dict):
            raise ValueError("Manifest must be JSON object")
        source=doc.get("source_image")
        if source is not None:
            if not isinstance(source,dict) or not isinstance(source.get("path"),str):
                raise ValueError("source_image needs a repository path")
            src=(root/source["path"]).resolve()
            if not src.is_relative_to((root/REFERENCES).resolve()) or not src.is_file():
                raise ValueError("Room source_image must exist under map_factory/references")
            if src.suffix.lower() not in (".png",".jpg",".jpeg",".webp"):
                raise ValueError("Unsupported map source image")
            actual_sha=hashlib.sha256(src.read_bytes()).hexdigest()
            if source.get("sha256") and source["sha256"] != actual_sha:
                raise ValueError("Source image hash mismatch")
            doc["source_image"]={"path":source["path"],"sha256":actual_sha,
                                 "status":"image_supplied_for_ai_layout_review"}
        assets=import_assets(root,doc.get("assets",[]))
        mode=doc.get("mode","patch")
        map_id=doc.get("map_id")
        if mode=="clone":
            from_map=doc.get("from_map")
            if not from_map:
                raise ValueError("Clone mode requires from_map")
            clone_map(root,map_id,from_map)
            if doc.get("changes"):
                patch={"map_id":map_id,"base_version":1,"changes":doc["changes"],
                       "note":doc.get("note","Cloned room modified from latest parent")}
                if doc.get("source_image"):
                    patch["source_image"]=doc["source_image"]
                # The compiler reads a checked manifest path, not untrusted shell input.
                temporary=root/"map_factory/intake"/"_generated_patch.json"
                temporary.write_text(json.dumps(patch,ensure_ascii=False)+"\n")
                try:
                    result=apply(root,temporary.relative_to(root))
                finally:
                    temporary.unlink(missing_ok=True)
            else:
                result=get_latest(root,map_id)
        elif mode=="patch":
            # apply() reads the original JSON; the source hash, if supplied, is
            # validated above and recorded in the checked manifest.
            if source is not None:
                verified=root/"map_factory/intake"/"_verified_source_patch.json"
                verified.write_text(json.dumps(doc,ensure_ascii=False)+"\n")
                try:
                    result=apply(root,verified.relative_to(root))
                finally:
                    verified.unlink(missing_ok=True)
            else:
                result=apply(root,file.relative_to(root))
        else:
            raise ValueError("Unknown intake mode: "+str(mode))
        receipt.parent.mkdir(parents=True,exist_ok=True)
        receipt.write_text(json.dumps({
          "manifest":file.relative_to(root).as_posix(),
          "manifest_sha256":digest,"map_id":result["map_id"],
          "result_version":result["version"],"imported_assets":assets["installed"],
          "staged_candidates":assets["candidates"],
          "status":"processed","source_image":doc.get("source_image")
        },indent=2,ensure_ascii=False)+"\n")
        imported.append((file.name,result["map_id"],result["version"]))
    print(json.dumps({"processed":imported},indent=2))
    return imported

if __name__=="__main__":
    try:
        process()
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print("Intake rejected:",str(exc),file=sys.stderr)
        sys.exit(1)
