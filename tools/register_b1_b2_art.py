"""Register the Codex B1/B2 hero-room candidate masters as runtime parts (TASK-0144).

Usage: python tools/register_b1_b2_art.py [--dry-run]

Same method as register_environment_art.py: the master in assets_hd stays untouched; the runtime part is the visible
(alpha >= 128) bounding box, BOX-downscaled to fit the intended native canvas (uniform scale) from the delivery manifest.
Origin is the bottom centre. Re-running skips IDs that already exist. Registered status is "ready" because the owner
said to merge and integrate after the visual review of the native captures; the room's own visual approval stays false.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "map_factory/metadata/asset_index.json"
APPROVAL = {
    "approved_by": "owner",
    "date": "2026-11-10",
    "evidence": "Owner chat 2026-11-10: reviewed B1/B2 native captures, then 'merge and build' (integrate the delivered candidates)",
    "method": "independent image_gen masters kept unchanged in assets_hd; runtime part is a trimmed BOX downscale",
}
# item id: (part id, category, subtype, y_sort, tags)
PARTS = {
    "hero_entrance_stairs_south": ("A19", "architecture", "stairs", True, ["stairs", "entrance", "ivy"]),
    "hero_stone_sphere_finial": ("A20", "architecture", "post", True, ["post", "sphere", "finial"]),
    "hero_compass_floor_inlay": ("D20", "decor", "inlay", False, ["compass", "inlay", "floor"]),
    "hero_rope_post": ("D21", "decor", "fence", True, ["rope", "post", "fence"]),
    "hero_rope_swag_west_rail": ("D22", "decor", "fence", True, ["rope", "rail", "west"]),
    "hero_rope_swag_east_rail": ("D23", "decor", "fence", True, ["rope", "rail", "east"]),
    "hero_study_table_south": ("P27", "furniture", "table", True, ["table", "study", "south"]),
    "hero_study_table_north": ("P28", "furniture", "table", True, ["table", "study", "north"]),
    "hero_study_table_east": ("P29", "furniture", "table", True, ["table", "study", "east"]),
    "hero_study_table_west": ("P30", "furniture", "table", True, ["table", "study", "west"]),
    "study_wooden_stool": ("P31", "furniture", "stool", True, ["stool", "study"]),
    "hero_study_bookshelf_south": ("P32", "furniture", "bookshelf", True, ["bookshelf", "armillary", "south"]),
    "hero_study_bookshelf_north": ("P33", "furniture", "bookshelf", True, ["bookshelf", "armillary", "north"]),
    "hero_headboard_shelf_south": ("P34", "furniture", "shelf", True, ["shelf", "headboard", "south"]),
    "hero_blue_white_planter": ("V034", "vegetation", "planter", True, ["planter", "blue_white", "flowers"]),
}


def items() -> dict[str, dict]:
    found = {}
    for manifest in sorted((ROOT / ".agents/graphics/deliveries").glob("ART-*/manifest.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("batch") in ("B1", "B2"):
            for item in data["items"]:
                found[item["id"]] = item
    return found


def build(name: str, spec: tuple, item: dict) -> tuple[dict, Image.Image]:
    identifier, category, subtype, y_sort, tags = spec
    master = ROOT / item["master_path"]
    image = Image.open(master).convert("RGBA")
    box = image.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
    image = image.crop(box)
    canvas_w, canvas_h = (int(v) for v in item["intended_native_canvas"])
    scale = min(canvas_w / image.width, canvas_h / image.height)  # uniform fit inside the intended native canvas
    width = max(1, round(image.width * scale))
    height = max(1, round(image.height * scale))
    image = image.resize((width, height), Image.Resampling.BOX)
    label = " ".join(p.capitalize() for p in name.removeprefix("hero_").split("_"))
    rel = f"map_factory/parts/{category}/{identifier}_{label.replace(' ', '_')}.png"
    record = {
        "id": identifier, "name": label, "category": category, "subtype": subtype,
        "texture_path": "res://" + rel, "status": "ready", "pixel_size": [width, height],
        "origin": [width // 2, height],
        "collision": {"enabled": False, "size": [32, 16], "offset": [0, 0]},
        "y_sort": y_sort,
        "shadow": {"type": "none", "opacity": 0.25, "offset_x": 4, "offset_y": 2},
        "tags": sorted(set(tags + [category])), "reusable": True,
        "source": {"kind": "image_gen_master", "master": item["master_path"],
                   "master_sha256": hashlib.sha256(master.read_bytes()).hexdigest(),
                   "request_id": item["request_id"]},
        "qa_notes": "Codex image_gen master (B1/B2 hero-room target batch); runtime part is a trimmed BOX downscale. Footprint and collision need scene calibration.",
        "qa_approval": dict(APPROVAL),
    }
    return record, image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(INDEX.read_text(encoding="utf-8"))
    known = {a["id"] for a in catalog["assets"]}
    delivered = items()
    added = 0
    for name, spec in PARTS.items():
        if spec[0] in known:
            continue
        record, image = build(name, spec, delivered[name])
        print(record["id"], name, record["pixel_size"])
        if args.dry_run:
            continue
        target = ROOT / record["texture_path"].removeprefix("res://")
        target.parent.mkdir(parents=True, exist_ok=True)
        image.save(target)
        catalog["assets"].append(record)
        added += 1
    if added:
        catalog["asset_count"] = len(catalog["assets"])
        INDEX.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"registered {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
