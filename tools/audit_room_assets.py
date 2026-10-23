#!/usr/bin/env python3
"""Read-only physical PNG and five-pass completeness audit.

Existence, dimensions, alpha and ID integrity can be verified automatically.
Visual similarity / beauty of artwork cannot be certified algorithmically.
"""
from pathlib import Path
import hashlib,json,collections,sys
from PIL import Image
from map_factory_cli import ROOT,registry,asset_catalog,get_latest
from map_factory_layers import create_layer_stack

OUT=ROOT/"map_factory/metadata/room_block_quality.json"
DOC=ROOT/"docs/ROOM_BLOCK_QA.md"

def main():
    catalog=asset_catalog(ROOT)
    state=registry(ROOT)
    inspected={}
    summaries=[]
    errors=[]
    for map_id in sorted(state["maps"]):
        current=get_latest(ROOT,map_id,state)
        stack=create_layer_stack(current,catalog)
        used=stack["unique_asset_ids"]
        for asset_id in used:
            if asset_id in inspected:continue
            record=catalog.get(asset_id)
            if not record:
                errors.append("Unregistered asset "+asset_id)
                continue
            relative=record["texture_path"].removeprefix("res://")
            file=ROOT/relative
            if not file.is_file():
                errors.append("Missing PNG "+asset_id+" at "+relative)
                continue
            try:
                with Image.open(file) as img:
                    img.load()
                    if img.format!="PNG":
                        errors.append("Non PNG "+asset_id)
                    if list(img.size)!=record.get("pixel_size"):
                        errors.append("Wrong metadata dimensions "+asset_id)
                    alpha=img.convert("RGBA").getchannel("A")
                    bounds=alpha.getbbox()
                    if bounds is None:
                        errors.append("Transparent/empty "+asset_id)
                    inspected[asset_id]={
                      "id":asset_id,"category":record["category"],
                      "status":record.get("status","planned"),
                      "dimensions":list(img.size),
                      "alpha_bbox":list(bounds) if bounds else None,
                      "file_bytes":file.stat().st_size,
                      "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                      "texture_path":record["texture_path"]
                    }
            except Exception as exc:
                errors.append("Unreadable "+asset_id+": "+str(exc))
        attachments=[x for x in stack["passes"]["decorations"] if x["attachment"]]
        count=dict(stack["counts"])
        blocked=[x["instance_id"] for x in stack["passes"]["walls"]
                 if x["category"]=="characters"] if False else []
        summary={"map_id":map_id,"version":current["version"],"counts":count,
                 "placed_instances":sum(count[k] for k in ("background","ground","walls","decorations")),
                 "mounted_details":len(attachments),"owned_shadows":count["shadows"],
                 "unique_asset_ids":len(used),
                 "visual_qa_status":current.get("visual_qa",{}).get("status","needs_review"),
                 "reference_sha256":current.get("composition_reference",{}).get("reference_sha256")}
        summaries.append(summary)
        if count["shadows"] != sum(
              x["shadow"].get("type","none")!="none" for key in ("background","ground","walls","decorations") for x in stack["passes"][key]):
            errors.append("Shadow pass count mismatch "+map_id)
    # Inspect every environmental PNG, not only images used in current maps.
    # Characters and UI are strictly excluded.
    all_map_ids=[ident for ident,record in sorted(catalog.items())
                 if record.get("category") not in ("characters","ui")]
    for asset_id in all_map_ids:
        if asset_id in inspected:
            continue
        record=catalog[asset_id]
        relative=record["texture_path"].removeprefix("res://")
        file=ROOT/relative
        if not file.is_file():
            errors.append("Missing reusable map PNG "+asset_id)
            continue
        try:
            with Image.open(file) as img:
                img.load()
                if img.format!="PNG":
                    errors.append("Non-PNG reusable sprite "+asset_id)
                if list(img.size)!=record.get("pixel_size"):
                    errors.append("Metadata pixel size mismatch "+asset_id)
                bounds=img.convert("RGBA").getchannel("A").getbbox()
                if not bounds:
                    errors.append("Empty alpha for "+asset_id)
                inspected[asset_id]={
                    "id":asset_id,"category":record["category"],
                    "status":record.get("status","planned"),
                    "dimensions":list(img.size),
                    "alpha_bbox":list(bounds) if bounds else None,
                    "file_bytes":file.stat().st_size,
                    "sha256":hashlib.sha256(file.read_bytes()).hexdigest(),
                    "texture_path":record["texture_path"]}
        except Exception as exc:
            errors.append("Unreadable environmental sprite "+asset_id+": "+str(exc))
    if len(inspected)!=len(all_map_ids):
        errors.append("Map catalog incomplete: %d/%d PNGs verified"%(len(inspected),len(all_map_ids)))

    by_status=collections.Counter(x["status"] for x in inspected.values())
    response={"maps":summaries,"verified_environment_png_files":len(inspected),
              "environment_catalog_count":len(all_map_ids),
              "catalog_total":len(catalog),"catalog_status":dict(collections.Counter(x.get("status","planned") for x in catalog.values())),
              "referenced_status":dict(by_status),"errors":errors,
              "artistic_qa":"NOT APPROVED: image file presence and alpha cannot confirm full fidelity.",
              "assets":sorted(inspected.values(),key=lambda a:a["id"])}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(response,indent=2,ensure_ascii=False)+"\n")
    md=["# Room Map Factory — physical art and layer QA","",
        "This report only certifies file/metadata integrity. It **does not certify that artwork matches the user's reference**.","",
        "| Map | Revision | Background | Ground detail | Walls | Decorations | Independent shadows | Mounted |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s in summaries:
        c=s["counts"]
        md.append(f'| {s["map_id"]} | v{s["version"]:04d} | {c["background"]} | {c["ground"]} | {c["walls"]} | {c["decorations"]} | {c["shadows"]} | {s["mounted_details"]} |')
    md += ["",f"- Registered catalog images: **{len(catalog)}**.",
           f"- Verified environmental and shadow PNG files: **{len(inspected)} / {len(all_map_ids)}**.",
           f"- Integrity errors: **{len(errors)}**.",
           f"- Catalog QA statuses: **{dict(response['catalog_status'])}**.",
           "- Reference fidelity still needs artist comparison of exported Godot room render.",
           "- Only environment sprites and their independent shadow images are included; no characters/UI are added.",
           "", "Detailed per-ID PNG SHA-256, pixel bounds and paths: map_factory/metadata/room_block_quality.json.",""]
    if errors:md+=["## Errors",""]+["- "+x for x in errors]
    DOC.write_text("\n".join(md),encoding="utf-8")
    print(json.dumps({k:v for k,v in response.items() if k!="assets"},indent=2))
    return bool(errors)

if __name__=="__main__":
    sys.exit(main())
