#!/usr/bin/env python3
"""Corrected environment asset registry (v2).

Derived from the approved v1 registry + the *measured* alpha bounds of every PNG.
PNGs, filenames, asset ids and SHA256 are never modified. Footprints, anchors and
collision are authored from what the art actually shows (visual bounds), not from
image dimensions, because the generated canvases carry large transparent padding
(e.g. F06/F07 East/West bookcases are 128x256 canvases with a 120x50 drawing).

Run: python tools/build_environment_registry_v2.py
"""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
T = 64
V1 = json.loads((ROOT / "map_factory/metadata/environment_assets_approved.json").read_text(encoding="utf-8"))

ROLE = {
    "A01": "column_slender", "A02": "column_capital", "A03": "column_main", "A04": "arch_half_left",
    "A05": "arch_complete_main", "A06": "arch_half_right", "A07": "keystone", "A08": "arch_plain_frame",
    "A09": "doorway_ornate", "A10": "stair_step", "A11": "stair_support_left", "A12": "stair_support_right",
    "A13": "entrance_post",
    "W01": "wall_block", "W02": "wall_block", "W03": "wall_block_broken", "W04": "wall_block_cracked",
    "W05": "wall_block_ivy", "W06": "wall_block_flowers", "W07": "wall_cap", "W08": "wall_corner_inner",
    "W09": "wall_corner_outer", "W10": "wall_low_broken", "W11": "wall_end_left", "W12": "wall_end_right",
    "W13": "wall_arch_adjacent_left", "W14": "wall_arch_adjacent_right", "W15": "wall_banner_mount",
    "F01": "bed", "F02": "bed", "F03": "bed", "F04": "bed", "F05": "bedside_table", "F06": "bookcase",
    "F07": "bookcase", "F08": "work_table", "F09": "bench_horizontal", "F10": "bench_vertical",
    "F11": "crate_small", "F12": "crate_medium",
    "D01": "rug_bed", "D02": "rug_table", "D03": "floor_emblem", "D04": "banner_long", "D05": "banner_short",
    "D06": "banner_support", "D07": "cloth_fold", "D08": "gold_trim",
    "L01": "lantern_wall", "L02": "lantern_wall_unlit_base", "L03": "candles", "L04": "lantern_table",
    "L05": "flame_overlay",
}
HANG = {"D04", "D05", "D06", "L01", "L02", "P01", "P02", "P03", "P12", "P13"}
WALL_MOUNTED_OK = ["wall_block", "wall_block_broken", "wall_block_cracked", "wall_block_ivy", "wall_block_flowers",
                   "wall_cap", "wall_corner_outer", "wall_corner_inner", "wall_low_broken", "wall_end_left",
                   "wall_end_right", "wall_arch_adjacent_left", "wall_arch_adjacent_right", "wall_banner_mount"]

# logical ground footprint [w, d] in 64px cells, authored from the visible drawing.
ARCH_FP = {"A04": [2, 1], "A05": [2, 1], "A06": [2, 1], "A08": [2, 1], "A09": [2, 1], "A10": [2, 1],
           "A11": [2, 1], "A12": [2, 1]}
# solid cells (relative to footprint top-left) when different from "all footprint cells"
SOLID_CELLS = {"A11": [[0, 0]], "A12": [[1, 0]]}
NO_COLLISION = {"A07", "A10"}
# art whose canvas/drawing disagree with the declared facing/footprint; usable only with care
ART_MISMATCH = {
    "F06@east": "128x256 canvas but the bookcase is drawn horizontally (122x50) in the middle",
    "F06@west": "128x256 canvas but the bookcase is drawn horizontally (118x54) in the middle",
    "F07@east": "128x256 canvas but the bookcase is drawn horizontally (124x51) in the middle",
    "F07@west": "128x256 canvas but the bookcase is drawn horizontally (112x56) at the bottom",
    "F08@east": "192x256 canvas but the table is drawn horizontally (173x94) - not a true side view",
    "F08@west": "192x256 canvas but the table is drawn horizontally (186x93) - not a true side view",
    "F09@east": "64x128 canvas but the bench is drawn horizontally (60x30)",
    "F09@west": "64x128 canvas but the bench is drawn horizontally (62x29)",
    "F10@north": "128x64 canvas with a tiny 26x53 drawing",
}
BED_ORIENT = {
    "south": "headboard top, footboard bottom (faces player)",
    "north": "headboard bottom, footboard top (faces away)",
    "west": "headboard right, footboard left",
    "east": "headboard left, footboard right",
}


def footprint(aid, facing, bbox, w, h):
    if aid in ARCH_FP:
        return ARCH_FP[aid]
    if aid in ("A01", "A02", "A03", "A07", "A13") or aid[0] == "W":
        return [1, 1]
    if aid in ("F01", "F03"):
        return [3, 3]
    if aid in ("F02", "F04"):
        return [4, 3]
    if aid == "F05" or aid == "F11":
        return [1, 1]
    if aid in ("F06", "F07"):
        return [4, 1] if facing in ("north", "south") else [2, 1]
    if aid == "F08":
        return [4, 2] if facing in ("north", "south") else [3, 2]
    if aid == "F09":
        return [2, 1] if facing in ("north", "south") else [1, 1]
    if aid == "F10":
        return [1, 2] if facing in ("east", "west") else ([2, 1] if facing == "south" else [1, 1])
    if aid == "F12":
        return [2, 2]
    if aid == "D01":
        return [2, 2]
    if aid in ("D02", "D03"):
        return [3, 3]
    if aid[0] == "G":
        return [1, 1]
    if aid[0] in "LPR" or aid in ("D04", "D05", "D06", "D07", "D08"):
        return [1, 1]
    return [0, 0]  # background


def classify(aid):
    c = aid[0]
    if c == "B":
        return "background", 0, "background"
    if c == "G":
        return "ground", 1, "ground"
    if aid in ("D01", "D02", "D03"):
        return "ground_overlay", 1, "ground"
    if c in "WAF":
        return "structure", 2, "world_ysort"
    return "decoration", 3, "world_attached"


def attachment_points(aid, role, facing, b):
    x0, y0, x1, y1 = b
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    pts = {}
    if aid[0] == "W":
        pts = {"banner_hang": [cx, y0 + 26], "lantern_hang": [cx, y0 + 34], "wall_top_stand": [cx, y0 + 12],
               "ivy_hang": [cx, y0 + 14], "face_center": [cx, cy]}
    elif aid in ("A05", "A04", "A06", "A08"):
        pts = {"arch_drape_left": [x0 + 22, y0 + 14], "arch_drape_right": [x1 - 22, y0 + 14],
               "top_center": [cx, y0 + 6]}
    elif aid == "A09":
        pts = {"lantern_hang_left": [x0 + 4, y0 + 40], "lantern_hang_right": [x1 - 4, y0 + 40],
               "ivy_hang_right": [x1 - 6, y0 + 20]}
    elif aid in ("A01", "A02", "A03"):
        pts = {"capital": [cx, y0 + 6]}
    elif aid in ("L01", "L02"):
        pts = {"flame_base": [cx, y1 - 9]}
    elif aid == "F08" and facing in ("north", "south"):
        sy = int(y0 + 0.35 * (y1 - y0))
        pts = {"surface_left": [x0 + 52, sy], "surface_mid_left": [x0 + 98, sy - 2],
               "surface_mid_right": [x0 + 146, sy], "surface_right": [x1 - 40, sy - 4]}
    elif aid in ("F06", "F07") and facing in ("north", "south"):
        sy = y0 + 16
        pts = {"shelf_top_left": [x0 + 32, sy], "shelf_top_center": [cx, sy], "shelf_top_right": [x1 - 32, sy]}
    elif aid == "F05":
        pts = {"surface_center": [cx, int(y0 + 0.45 * (y1 - y0))]}
    elif aid in ("F09", "F10"):
        pts = {"seat_center": [cx, int(y0 + 0.4 * (y1 - y0))]}
    elif aid in ("F01", "F02", "F03", "F04"):
        pts = {"bed_center": [cx, cy]}
    return pts


def main():
    out = {}
    for key, rec in V1["assets"].items():
        aid, facing = rec["asset_id"], rec["facing"]
        png = ROOT / rec["texture"].replace("res://", "")
        digest = hashlib.sha256(png.read_bytes()).hexdigest()
        assert digest == rec["sha256"], f"hash drift {key}"
        im = Image.open(png).convert("RGBA")
        alpha = im.getchannel("A").point(lambda v: 255 if v > 40 else 0)
        bbox = list(alpha.getbbox() or (0, 0, im.width, im.height))
        w, h = im.size
        category, level, render_pass = classify(aid)
        role = ROLE.get(aid)
        if role is None:
            role = {"G": "floor_tile", "B": "background_piece", "P": "plant", "R": "prop"}[aid[0]]
        x0, y0, x1, y1 = bbox
        cx = (x0 + x1) // 2
        fp = footprint(aid, facing, bbox, w, h)
        cells = [[dx, dy] for dy in range(fp[1]) for dx in range(fp[0])]
        flat = category in ("ground", "ground_overlay")
        if category == "background":
            pivot, anchor, placement = [0, 0], [0, 0], "background"
        elif flat:
            pivot, anchor, placement = [cx, (y0 + y1) // 2], [fp[0] * T // 2, fp[1] * T // 2], "ground_surface"
        elif aid in HANG:
            pivot, anchor, placement = [cx, y0], [fp[0] * T // 2, fp[1] * T // 2], "wall_face_hang"
        else:
            pivot, anchor = [cx, y1], [fp[0] * T // 2, fp[1] * T]
            placement = {"decoration": "floor_or_surface"}.get(category, "floor")
        if aid[0] == "P" and aid in ("P01", "P02", "P03", "P12", "P13"):
            placement = "wall_face_hang"
        parent_types = []
        if category == "decoration":
            if aid in ("D04", "D05", "D06", "L01", "L02", "P01", "P02", "P03", "P12", "P13"):
                parent_types = WALL_MOUNTED_OK + ["arch_complete_main", "arch_plain_frame", "doorway_ornate"]
            elif aid in ("L03", "L04", "R01", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12", "R13", "R14", "D07"):
                parent_types = ["work_table", "bookcase", "bedside_table", "bench_vertical", "bench_horizontal"]
            if aid[0] in "PR" and aid not in ("P01", "P02", "P03", "P12", "P13"):
                parent_types = parent_types + ["floor", "wall_top"] if parent_types else ["floor", "wall_top"]
            if aid == "L05":
                parent_types = ["lantern_wall", "lantern_wall_unlit_base", "lantern_table"]
        solid = category == "structure" and aid not in NO_COLLISION
        solid_cells = SOLID_CELLS.get(aid, cells) if solid else []
        mism = ART_MISMATCH.get(key)
        entry = {
            "asset_id": aid, "registry_key": key, "category": rec.get("name", ""),
            "asset_role": role,
            "source_texture_path": rec["texture"], "sha256": digest,
            "sprite_dimensions": [w, h],
            "visual_bounds": bbox,
            "logical_footprint": fp,
            "occupied_ground_cells": cells if category in ("structure", "ground", "ground_overlay") or (
                category == "decoration" and aid[0] in "PR" and aid not in ("P01", "P02", "P03", "P12", "P13")) else [],
            "ground_anchor_px": anchor,
            "ground_anchor_note": "point inside the footprint (footprint-local px) that render_pivot is pinned to",
            "render_pivot_px": pivot,
            "render_pivot_note": "sprite pixel that sits on the anchor: bottom-centre of the drawing for standing pieces, top-centre for hanging pieces, centre for flat overlays",
            "facing_direction": facing,
            "placement_surface": placement,
            "attachment_points": attachment_points(aid, role, facing, bbox),
            "allowed_parent_types": parent_types,
            "adjacency_rules": {},
            "collision_shape": {"type": "cells" if solid else "none", "cells": solid_cells},
            "depth_behavior": {"ground": "flat_below_world", "ground_overlay": "flat_below_world",
                               "background": "fixed_background", "structure": "y_sort_ground_contact",
                               "decoration": "above_parent_or_y_sort"}[category],
            "logical_level": level,
            "render_pass": render_pass,
            "shadow_receiver": category in ("ground", "ground_overlay"),
            "shadow_caster": solid and role not in ("stair_step",),
            "approval_status": "approved",
        }
        if aid in ("F01", "F02", "F03", "F04"):
            entry["verified_visual_orientation"] = BED_ORIENT[facing]
        if mism:
            entry["art_mismatch"] = mism
        out[key] = entry

    # per-asset adjacency rules
    for k, e in out.items():
        role = e["asset_role"]
        if role in ("bookcase",):
            e["adjacency_rules"] = {"wall_clearance_cells": 0, "must_touch_wall": "rear", "front_clearance_cells": 1}
        elif role == "work_table":
            e["adjacency_rules"] = {"wall_clearance_cells": 1, "front_clearance_cells": 1, "keep_clear_of": ["floor_emblem"]}
        elif role == "bed":
            e["adjacency_rules"] = {"wall_clearance_cells": 0, "head_to_wall": True, "needs_rug": "rug_bed"}
        elif role.startswith("wall") or role.startswith("arch") or role.startswith("column"):
            e["adjacency_rules"] = {"connects_to": ["wall", "column", "arch", "doorway", "corner"]}
        elif role.startswith("stair"):
            e["adjacency_rules"] = {"entrance_clearance_cells": 1}

    (ROOT / "map_factory/metadata/environment_assets_v2.json").write_text(json.dumps({
        "schema": "skl.environment_assets.v2",
        "tile_size": T,
        "count": len(out),
        "derived_from": "map_factory/metadata/environment_assets_approved.json",
        "approval": V1["approval"],
        "visual_bounds_note": "[x0,y0,x1,y1] alpha>40 bounding box in sprite pixels",
        "assets": out,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    flagged = [k for k, e in out.items() if "art_mismatch" in e]
    print(f"registry v2: {len(out)} assets; art mismatches: {flagged}")


if __name__ == "__main__":
    main()
