"""Register the Codex B3 / ART-0023 hero-room candidate masters (doors, window wall, side banners, wall lantern) as runtime parts (TASK-0145).

Usage: python tools/register_b3_art.py [--dry-run]

Same method as register_environment_art.py: the master in assets_hd stays untouched; the runtime part is the visible
(alpha >= 128) bounding box, BOX-downscaled to fit the intended native canvas (uniform scale) from the delivery manifest.
Origin is the bottom centre. Re-running skips IDs that already exist. Registered status is "ready" because the owner
said to agree all new Codex graphics and use them after reviewing the native captures; the room's own visual approval stays false.

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
    "date": "2026-11-11",
    "evidence": "Owner chat 2026-11-10: reviewed B3/ART-0023 native captures, then 'agree them all and use them' (integrate the delivered candidates)",
    "method": "independent image_gen masters kept unchanged in assets_hd; runtime part is a trimmed BOX downscale",
}
# item id: (part id, category, subtype, y_sort, tags)
PARTS = {
    "hero_compass_wood_door_north": ("A21", "architecture", "door", True, ["door", "wood", "compass", "north"]),
    "hero_compass_wood_door_east": ("A22", "architecture", "door", True, ["door", "wood", "compass", "east"]),
    "hero_compass_wood_door_south": ("A23", "architecture", "door", True, ["door", "wood", "compass", "south"]),
    "hero_compass_wood_door_west": ("A24", "architecture", "door", True, ["door", "wood", "compass", "west"]),
    "wall_straight_window_opening": ("W036", "architecture", "wall", True, ["wall", "window", "ivy"]),
    "hero_side_banner_east_facing_long": ("D24", "decor", "banner", True, ["banner", "side", "east"]),
    "hero_side_banner_east_facing_short": ("D25", "decor", "banner", True, ["banner", "side", "east", "short"]),
    "hero_side_banner_west_facing_long": ("D26", "decor", "banner", True, ["banner", "side", "west"]),
    "hero_wall_lantern_west": ("L06", "lighting", "lantern", True, ["lantern", "wall", "west"]),
}


def manifest_request(item: dict) -> str:
    return "ART-0023" if "side_banner" in item["id"] or "lantern" in item["id"] else "ART-0038" if "window" in item["id"] else "ART-0005"


def items() -> dict[str, dict]:
    found = {}
    for manifest in sorted((ROOT / ".agents/graphics/deliveries").glob("ART-*/manifest.json")):
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("batch") == "B3" or manifest.parent.name == "ART-0023":
            for item in data["items"]:
                found[item["id"]] = item
    return found


def build(name: str, spec: tuple, item: dict) -> tuple[dict, Image.Image]:
    identifier, category, subtype, y_sort, tags = spec
    master = ROOT / item["master_path"]
    image = Image.open(master).convert("RGBA")
    box = image.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
    image = image.crop(box)
    native = ROOT / item["native_review_path"]  # the owner-reviewed native render defines the runtime canvas
    canvas_w, canvas_h = (int(v) for v in item.get("intended_native_canvas") or Image.open(native).size)
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
                   "request_id": item.get("request_id") or manifest_request(item)},
        "qa_notes": "Codex image_gen master (B3 / ART-0023 hero-room batch); runtime part is a trimmed BOX downscale. Footprint and collision need scene calibration.",
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
