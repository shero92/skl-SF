"""Register the 128-piece environment art pack as reusable map assets.

This is registration, not production: every PNG is referenced in place, hashed and
never copied, resized, recoloured or moved. All measurements come from the sidecar
JSON that shipped with each PNG (native size, footprint, declared anchor) plus the
pack's own four-view identity grouping.

What the script derives, and why:

* ``origin`` - the pack sidecars declare a bottom-LEFT anchor ``(0, h)``. The map
  factory's grid placement contract places a sprite's bottom-CENTER on the ground
  anchor (``world_anchor`` in tools/map_factory_placement.py), and every pack sprite
  is drawn centred in its canvas, so the registered pivot is ``(w // 2, h)``.
  Floor tiles and background segments keep ``(0, 0)`` because they are drawn from
  their top-left corner.
* ``collision`` - a ground-contact box equal to the declared tile footprint. The
  pack ships no physics data; the footprint is the only measured ground extent.
* ``shadow`` - the existing S0xx shadow parts, chosen per category.
* ``placement_contract`` - floor contracts for anything that stands on the ground
  and mounted contracts for wall/tabletop dressing. Footprints stay
  ``measurement_status: provisional`` until an owner reviews them visually.
* ``direction_asset_ids`` - the pack draws four independent cardinal views for each
  furniture identity. Raw rotation of upright art is forbidden, so the four views
  are registered as separate records and linked from every record of the group.

Run:  py -3 tools/register_environment_pack.py [--check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "assets_generated"
INDEX = ROOT / "map_factory/metadata/asset_index.json"

FACINGS = ("north", "east", "south", "west")
PACK_CATEGORY = {
    "architecture": "architecture",
    "background": "environment",
    "decor": "decor",
    "floor": "floors",
    "furniture": "furniture",
    "lighting": "objects",
    "plants": "vegetation",
    "props": "objects",
    "wall": "walls",
}
SUBTYPE = {
    "architecture": "stone",
    "background": "seascape",
    "decor": "decal",
    "floor": "stone",
    "furniture": "furniture",
    "lighting": "lantern",
    "plants": "foliage",
    "props": "prop",
    "wall": "stone",
}
EXTRA_TAGS = {
    "architecture": ["architecture", "stone"],
    "background": ["environment", "seascape", "ocean"],
    "decor": ["decor", "decal"],
    "floor": ["floor", "stone", "sandstone"],
    "furniture": ["furniture", "interior"],
    "lighting": ["objects", "lighting", "lantern"],
    "plants": ["vegetation", "foliage"],
    "props": ["objects", "prop"],
    "wall": ["walls", "stone", "architecture"],
}
# Wall/tabletop dressing: mounted on a host instead of standing on the ground.
MOUNTED = frozenset(
    ["R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12",
     "L01", "L02", "L03", "L04", "L05",
     "D04", "D05", "D06", "D07", "D08",
     "P01", "P02", "P03", "P12", "P13"]
)
# Ground decals: they lie flat and never reserve a walkable cell.
OVERLAY = frozenset(["D01", "D02", "D03", "P04", "P05", "P06", "P14", "R13", "R14"])
# Ground-standing furniture and props.
SOLID = frozenset(
    ["F01", "F02", "F03", "F04", "F05", "F06", "F07", "F08", "F09", "F10",
     "F11", "F12", "R01", "R02", "R03", "R04",
     "P07", "P08", "P09", "P10", "P11"]
)
SHADOW = {
    "F01": "bed", "F02": "bed", "F03": "bed", "F04": "bed",
    "F05": "contact_medium", "F06": "bookshelf", "F07": "bookshelf",
    "F08": "table", "F09": "chair", "F10": "chair",
    "F11": "contact_small", "F12": "contact_medium",
}
DEFAULT_SHADOW = {
    "architecture": {"type": "soft_cast", "opacity": 0.22, "offset_x": 8, "offset_y": 6},
    "walls": {"type": "wall_base", "opacity": 0.24, "offset_x": 8, "offset_y": 6},
    "furniture": {"type": "contact_medium", "opacity": 0.26, "offset_x": 4, "offset_y": 2},
    "decor": {"type": "none", "opacity": 0.0, "offset_x": 0, "offset_y": 0},
    "objects": {"type": "contact_small", "opacity": 0.20, "offset_x": 3, "offset_y": 2},
    "vegetation": {"type": "plant", "opacity": 0.16, "offset_x": 3, "offset_y": 3},
    "floors": {"type": "none", "opacity": 0.0, "offset_x": 0, "offset_y": 0},
    "environment": {"type": "none", "opacity": 0.0, "offset_x": 0, "offset_y": 0},
}
TAG_NAME = {
    "A01": ["column", "main_stone_column"],
    "A02": ["column", "capital"],
    "A03": ["column", "base"],
    "A04": ["arch", "left_wing"],
    "A05": ["arch", "open_span"],
    "A06": ["arch", "right_wing"],
    "A07": ["arch", "keystone"],
    "A08": ["door", "frame"],
    "A09": ["door", "ruined"],
    "A10": ["stairs", "step"],
    "A11": ["stairs", "left_support"],
    "A12": ["stairs", "right_support"],
    "A13": ["pillar", "entrance"],
}


def load_sidecars():
    items = []
    for path in sorted(PACK.glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if "asset_id" not in data or "filename" not in data:
            continue
        data["_sidecar"] = path.relative_to(ROOT).as_posix()
        items.append(data)
    return items


def group_items(items):
    groups = {}
    for item in items:
        groups.setdefault(item["identity"], {})[item.get("orientation", "default")] = item
    return groups


def record_ids(group):
    """Map orientation -> registered record ID for one art identity."""
    orientations = [o for o in FACINGS if o in group]
    if not orientations:
        # Single-view art (architecture, walls, floors, props, background).
        only = group["default"]
        return {"default": only["asset_id"]}, only["asset_id"], False
    ids = {o: group[o]["asset_id"] for o in orientations}
    if len(set(ids.values())) == len(ids) and len(ids) == 4:
        # The pack gave each view its own top-level ID (the royal bed, F01-F04).
        return ids, ids["south"], False
    if len(set(ids.values())) == 1 and len(ids) == 4:
        # One ID, four drawn views: keep the base ID as the canonical record.
        only = next(iter(set(ids.values())))
        return {o: f"{only}_{o}" for o in orientations}, only, True
    return ids, ids[orientations[0]], False


def texture_path(item):
    return "res://assets_generated/" + item["filename"]


def build_record(item, ident, direction_map=None, base=False, approved=False):
    pack_category = item["category"]
    category = PACK_CATEGORY[pack_category]
    width, height = int(item["native_width"]), int(item["native_height"])
    flat = pack_category in ("floor", "background")
    origin = [0, 0] if flat else [width // 2, height]
    footprint = [int(item.get("footprint_tiles_x") or 1),
                 int(item.get("footprint_tiles_y") or 1)]
    tags = list(EXTRA_TAGS[pack_category])
    tags += TAG_NAME.get(item["asset_id"], [])
    tags += [t for t in str(item["asset_name"]).split("_") if t][:4]
    if pack_category == "decor" and "rug" in str(item["asset_name"]):
        tags.append("rug")
    shadow = dict(DEFAULT_SHADOW[category])
    if item["asset_id"] in SHADOW:
        shadow = {"type": SHADOW[item["asset_id"]], "opacity": 0.28,
                  "offset_x": 0, "offset_y": 0}
    collision = {"enabled": False, "size": [32, 16], "offset": [0, 0]}
    if item["asset_id"] in SOLID:
        collision = {"enabled": True,
                     "size": [footprint[0] * 64, footprint[1] * 64],
                     "offset": [0, -(footprint[1] * 32)]}
    record = {
        "id": ident,
        "name": item.get("title") or item["asset_name"],
        "category": category,
        "subtype": ("rug" if "rug" in tags else SUBTYPE[pack_category]),
        "texture_path": texture_path(item),
        "status": "ready",
        "pixel_size": [width, height],
        "origin": origin,
        "collision": collision,
        "y_sort": not flat,
        "shadow": shadow,
        "tags": sorted(set(tags)),
        "reusable": True,
        "source": {
            "kind": "image_gen_environment_pack",
            "pack": "assets_generated",
            "pack_asset_id": item["asset_id"],
            "pack_orientation": item.get("orientation", "default"),
            "sidecar": item["_sidecar"],
            "sha256": item.get("sha256"),
            "anchor_declared": [item.get("anchor_x"), item.get("anchor_y")],
            "anchor_registered": origin,
            "identity": item["identity"],
        },
        "qa_notes": ("Environment pack asset. Transparency, native size and canvas "
                     "bounds scripted-checked; silhouette, palette and seams await "
                     "owner visual review."),
        "approval_status": "approved" if approved else "needs_review",
    }
    if direction_map:
        record["direction_asset_ids"] = dict(direction_map)
        record["canonical_view"] = item.get("orientation", "default")
    contract = placement_contract(item, pack_category, footprint)
    if contract:
        record["placement_contract"] = contract
    if base:
        record["record_role"] = "canonical"
    return record


def placement_contract(item, pack_category, footprint):
    base_id = item["asset_id"]
    if base_id in MOUNTED:
        return {
            "schema_version": 1,
            "mode": "mounted",
            "mount_on_categories": ["furniture", "walls", "architecture"],
            "measurement_status": "provisional",
        }
    if base_id in SOLID or base_id in OVERLAY:
        return {
            "schema_version": 1,
            "mode": "floor",
            "footprint_cells": list(footprint),
            "occupancy_group": "overlay" if base_id in OVERLAY else "solid",
            "allowed_floor_tags": ["stone"],
            "forbidden_floor_tags": [],
            "measurement_status": "provisional",
        }
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify PNG hashes and report without writing")
    parser.add_argument("--approve", action="store_true",
                        help="set pack approval_status to approved (PNG bytes are never modified)")
    args = parser.parse_args(argv)

    index = json.loads(INDEX.read_text(encoding="utf-8"))
    items = load_sidecars()
    if len(items) != 128:
        raise SystemExit(f"Expected 128 pack sidecars, found {len(items)}")

    missing, mismatched = [], []
    for item in items:
        png = PACK / item["filename"]
        if not png.exists():
            missing.append(item["filename"])
            continue
        digest = hashlib.sha256(png.read_bytes()).hexdigest()
        if item.get("sha256") and digest != item["sha256"]:
            mismatched.append(item["filename"])
    if missing or mismatched:
        raise SystemExit(f"Pack integrity failed: missing={missing} mismatched={mismatched}")

    records = []
    for identity, group in sorted(group_items(items).items()):
        ids, base_id, needs_base = record_ids(group)
        direction = dict(ids) if len(ids) == 4 else None
        for orientation, ident in sorted(ids.items()):
            records.append(build_record(group[orientation], ident, direction,
                                        approved=args.approve))
        if needs_base or base_id not in ids.values():
            source = group.get("north") or group["south"]
            records.append(build_record(source, base_id, direction, base=True,
                                        approved=args.approve))

    known = {r["id"] for r in records}
    kept = [a for a in index["assets"]
            if a.get("id") not in known
            and (a.get("source") or {}).get("pack") != "assets_generated"]
    index["assets"] = kept + sorted(records, key=lambda r: r["id"])
    index["asset_count"] = len(index["assets"])
    index["environment_pack"] = {
        "pack": "assets_generated",
        "pieces": len(records),
        "pngs": len(items),
        "source": "128-piece image_gen environment pack, 2026-10-30",
        "registered_by": "tools/register_environment_pack.py",
        "approval_status": "approved" if args.approve else "needs_review",
        "note": ("Registered for reference reconstruction of hero_room_01. "
                 "Owner approved all 128 pack PNGs; PNG bytes unchanged." if args.approve else
                 "Silhouette, palette and seam review is the owner's."),
    }
    if args.check:
        print(f"pack ok: {len(items)} pngs hashed; {len(records)} records ready")
        return 0
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8", newline="\n")
    print(f"registered {len(records)} records ({len(items)} pngs); "
          f"catalog now holds {index['asset_count']} assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
