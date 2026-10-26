#!/usr/bin/env python3
"""Audit independent PNG sprites without automatically approving low-quality art."""
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import json, csv, collections, hashlib

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"map_factory/metadata/asset_index.json"
REPORT=ROOT/"map_factory/metadata/asset_audit.json"
QUEUE=ROOT/"map_factory/metadata/production_queue.csv"
DOC=ROOT/"docs/ASSET_AUDIT.md"

def audit():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    rows=[]
    counts=collections.Counter()
    by_category={}
    for a in data["assets"]:
        item=dict(id=a["id"],category=a["category"],status=a["status"])
        path=ROOT/a["texture_path"].removeprefix("res://")
        if not path.exists():
            if a["status"] != "planned":
                item["warning"]="missing_png_but_marked_present"
                a["status"]="planned"
            counts["missing"]+=1
            rows.append(item)
            continue
        try:
            with Image.open(path) as img:
                if img.format!="PNG":
                    raise ValueError("Not PNG")
                img.load()
                w,h=img.size
                rgba=img.convert("RGBA")
                amin,amax=rgba.getchannel("A").getextrema()
                bbox=rgba.getchannel("A").getbbox()
        except (OSError,ValueError,UnidentifiedImageError) as ex:
            item["error"]="corrupt_png: "+str(ex)
            counts["invalid"]+=1
            rows.append(item)
            continue
        warnings=[]
        if a["status"] == "planned":
            a["status"]="needs_cleanup"
            a["source"]={"kind":"existing_unreviewed_png"}
            warnings.append("metadata_was_planned_but_png_exists")
        if a["status"] == "ready" and "inspect in godot" in str(a.get("qa_notes","")).lower():
            a["status"]="needs_cleanup"
            warnings.append("previously_ready_without_godot_review")
        if a.get("pixel_size") != [w,h]:
            warnings.append("metadata_dimensions_corrected")
            a["pixel_size"]=[w,h]
        if a["category"] not in ("floors","environment","ui") and amin==255:
            warnings.append("opaque_object_no_transparency")
        if a["category"]=="floors" and w!=h:
            warnings.append("non_square_floor_tile_or_decal")
        if w<32 or h<32:
            warnings.append("small_native_resolution")
        item.update(status=a["status"],pixel_size=[w,h],has_transparency=amin<255,
                    alpha_bbox=list(bbox) if bbox else None,bytes=path.stat().st_size,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest(),warnings=warnings)
        rows.append(item)
        counts["existing"]+=1
        counts["ready" if a["status"]=="ready" else "needs_cleanup"]+=1
        by_category.setdefault(a["category"],{"existing":0,"missing":0})["existing"]+=1
    for a in data["assets"]:
        if not (ROOT/a["texture_path"].removeprefix("res://")).exists():
            by_category.setdefault(a["category"],{"existing":0,"missing":0})["missing"]+=1
    data["extracted_count"]=counts["existing"]
    data["status_note"]="Asset presence verified automatically; no sprites are promoted to ready without visual QA."
    INDEX.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    with QUEUE.open("w",newline="",encoding="utf-8") as f:
        wr=csv.writer(f,lineterminator="\n"); wr.writerow(["id","category","name","status","texture_path"])
        wr.writerows((a["id"],a["category"],a["name"],a["status"],a["texture_path"]) for a in data["assets"])
    summary={"total":len(data["assets"]),**counts}
    report={"summary":summary,"by_category":by_category,"assets":rows,
            "notice":"An existing PNG is NOT a high-quality approval. Manual visual QA required."}
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    markdown=["# Automated asset inventory","",
       "File presence and metadata only. This does NOT certify visual quality.","",
       f"- Registered: {summary['total']}",
       f"- PNG files present: {counts['existing']}",
       f"- Missing: {counts['missing']}",
       f"- Drafts needing cleanup: {counts['needs_cleanup']}",
       f"- Reviewed ready: {counts['ready']}","",
       "| Category | Present | Missing |","|---|---:|---:|"]
    for cat,stat in sorted(by_category.items()):
        markdown.append(f"| {cat} | {stat['existing']} | {stat['missing']} |")
    markdown.extend(["","## Automatic issues",
                     "See asset_audit.json in map_factory/metadata for per-file details.",
                     "Review image transparency, edges, baked labels, anchors, tile seams and collision before approving.",""])
    DOC.write_text("\n".join(markdown),encoding="utf-8",newline="\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    audit()
