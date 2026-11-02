#!/usr/bin/env python3
"""Fail CI if room layouts reference unknown IDs or impossible structural values."""
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
assets=json.loads((ROOT/"map_factory/metadata/asset_index.json").read_text(encoding="utf-8"))["assets"]
by_id={a["id"]:a for a in assets}
v2=json.loads((ROOT/"map_factory/metadata/environment_assets_v2.json").read_text(encoding="utf-8"))["assets"]
errors=[]
warnings=[]
for path in sorted((ROOT/"map_factory/rooms").glob("*.json")):
    data=json.loads(path.read_text(encoding="utf-8"))
    if str(data.get("schema","")).startswith("skl.reference_room_layout"):
        # Explicit object layouts use the corrected registry v2 (asset_id, parent + attach_point).
        object_ids={o.get("object_id") for o in data.get("objects",[])}
        for o in data.get("objects",[]):
            rec=v2.get(str(o.get("asset_id","")))
            if rec is None:
                errors.append(f"{path.name}: unknown asset {o.get('asset_id')} in objects")
                continue
            if not (ROOT/rec["source_texture_path"].removeprefix("res://")).is_file():
                warnings.append(f"{path.name}: missing artwork for {o.get('asset_id')}")
            parent=o.get("parent")
            if parent is not None:
                host=next((h for h in data["objects"] if h.get("object_id")==parent),None)
                if parent not in object_ids or host is None:
                    errors.append(f"{path.name}: {o.get('object_id')} has missing parent {parent}")
                elif o.get("attach_point") not in v2[host["asset_id"]]["attachment_points"]:
                    errors.append(f"{path.name}: {parent} has no attachment point {o.get('attach_point')}")
        continue
    size=data.get("size",[18,11])
    if len(size)!=2 or any(int(s)<=0 for s in size):
        errors.append(f"{path.name}: invalid room size")
    if int(data.get("tile_size",48))<=0:
        errors.append(f"{path.name}: invalid tile_size")
    groups=["background_objects","ground_overlays","back_objects","objects","front_objects","decorations"]
    for group in groups:
        for item in data.get(group,[]):
            aid=str(item.get("id",""))
            if aid not in by_id:
                errors.append(f"{path.name}: unknown asset {aid} in {group}")
            else:
                tex=ROOT/by_id[aid]["texture_path"].removeprefix("res://")
                if not tex.is_file():
                    warnings.append(f"{path.name}: missing artwork for {aid} (placeholder shown)")
            if float(item.get("scale",1.0))<=0:
                errors.append(f"{path.name}: invalid scale for {aid}")
    for aid in data.get("floor_ids",[]):
        if aid not in by_id:
            errors.append(f"{path.name}: unknown floor asset {aid}")
        elif by_id[aid]["category"]!="floors":
            errors.append(f"{path.name}: non-floor ID used for ground {aid}")
    for npc in data.get("npcs",[]):
        if "x" not in npc or "y" not in npc:
            errors.append(f"{path.name}: NPC missing position")
print("Validated",len(list((ROOT/"map_factory/rooms").glob("*.json"))),"room layouts")
for v in warnings: print("WARNING:",v)
for v in errors: print("ERROR:",v)
sys.exit(1 if errors else 0)
