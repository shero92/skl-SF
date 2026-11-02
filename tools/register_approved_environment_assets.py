#!/usr/bin/env python3
"""Register the 128 owner-approved environment PNGs (assets_generated/).

Marks library_manifest.json + sidecar JSON as approved (status fields only; PNGs,
hashes, IDs, filenames, sizes, anchors are never touched) and writes the
Godot-facing registry map_factory/metadata/environment_assets_approved.json.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "assets_generated"
APPROVAL = {
    "approved_by": "owner",
    "approved_on": "2026-10-31",
    "scope": "visual approval of all 128 environment PNGs; use in Map Factory rooms",
}
NO_COLLISION = {"A04", "A05", "A06", "A07", "A10"}


def classify(aid: str) -> str:
    c = aid[0]
    if c == "B":
        return "background"
    if c == "G":
        return "ground"
    if aid in ("D01", "D02", "D03"):
        return "ground_overlay"
    if c in "WAF":
        return "structure"
    return "decoration"


def pivot(aid: str, w: int, h: int) -> list:
    # Attachment pivot inside the sprite: hanging things hang from the top.
    if aid in ("D04", "D05", "D06", "L01", "L02", "P01", "P02", "P03", "P12", "P13"):
        return [w // 2, 0]
    return [w // 2, h]  # standing things rest on their bottom centre


def main() -> None:
    manifest_path = LIB / "library_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    registry = {}
    for rec in manifest["assets"]:
        png = LIB / rec["filename"]
        side = png.with_suffix(".json")
        meta = json.loads(side.read_text(encoding="utf-8"))
        digest = hashlib.sha256(png.read_bytes()).hexdigest()
        assert digest == rec["sha256"] == meta["sha256"], f"hash drift {png.name}"
        aid, facing = meta["asset_id"], meta["orientation"]
        w, h = meta["native_width"], meta["native_height"]
        fx, fy = meta["footprint_tiles_x"], meta["footprint_tiles_y"]
        level = classify(aid)
        key = aid if facing == "default" else f"{aid}@{facing}"
        registry[key] = {
            "asset_id": aid,
            "name": meta["asset_name"],
            "facing": facing,
            "level": level,
            "texture": "res://assets_generated/" + rec["filename"],
            "sha256": digest,
            "sprite_size": [w, h],
            "footprint_cells": [fx, fy],
            "anchor": [meta["anchor_x"], meta["anchor_y"]],
            "anchor_note": "sprite bottom-left sits on the footprint's bottom-left ground corner",
            "attach_pivot": pivot(aid, w, h),
            "collision": level == "structure" and aid not in NO_COLLISION,
            "approval_status": "approved",
        }
        rec["approval_status"] = "approved"
        rec["approval"] = APPROVAL
        meta["approval_status"] = "approved"
        meta["approval"] = APPROVAL
        side.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    manifest["new_asset_status"] = "approved_by_owner_2026-10-31"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = ROOT / "map_factory" / "metadata" / "environment_assets_approved.json"
    out.write_text(json.dumps({
        "schema": "skl.environment_assets.v1",
        "tile_size": 64,
        "count": len(registry),
        "approval": APPROVAL,
        "assets": registry,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered {len(registry)} assets -> {out}")


if __name__ == "__main__":
    main()
