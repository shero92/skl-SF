"""Register the merged Codex deliveries ART-0021 (chest, four views), ART-0015 (two oblique rugs) and
ART-0002 (three clouds) as Map Factory runtime parts (TASK-0149).

Usage: python tools/register_b4_art.py [--dry-run]

Same method as register_b3_art.py: masters in assets_hd stay untouched; the runtime part is the visible
bounding box BOX-downscaled (uniform) into the native canvas named by the delivery manifest. The chest
manifest only names a provisional placement size, so a 76x76 canvas is used here. Re-running skips known IDs.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import register_b3_art as b3

ROOT = Path(__file__).resolve().parents[1]
APPROVAL = {
    "approved_by": "owner",
    "date": "2026-11-11",
    "evidence": "docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md (owner accepts Codex images automatically until one is named for regeneration)",
    "method": "independent image_gen masters kept unchanged in assets_hd; runtime part is a trimmed BOX downscale",
}
CHEST_CANVAS = [76, 76]
# item id: (part id, category, subtype, y_sort, tags)
PARTS = {
    "hero_study_chest_north": ("F027", "furniture", "chest", True, ["chest", "wood", "north"]),
    "hero_study_chest_east": ("F028", "furniture", "chest", True, ["chest", "wood", "east"]),
    "hero_study_chest_south": ("F029", "furniture", "chest", True, ["chest", "wood", "south"]),
    "hero_study_chest_west": ("F030", "furniture", "chest", True, ["chest", "wood", "west"]),
    "hero_bedroom_blue_rug": ("D27", "decor", "rug", False, ["rug", "decal", "bed", "oblique"]),
    "hero_study_blue_rug": ("D28", "decor", "rug", False, ["rug", "decal", "table", "oblique"]),
    "hero_cloud_01": ("B12", "environment", "seascape", False, ["cloud", "sky"]),
    "hero_cloud_02": ("B13", "environment", "seascape", False, ["cloud", "sky"]),
    "hero_cloud_03": ("B14", "environment", "seascape", False, ["cloud", "sky"]),
}
COLLIDER = {"F027": ([60, 20], [0, -10]), "F028": ([40, 30], [0, -15]), "F029": ([60, 20], [0, -10]), "F030": ([40, 30], [0, -15])}


def items() -> dict[str, dict]:
    found = {}
    for request in ("ART-0021", "ART-0015", "ART-0002"):
        data = json.loads((ROOT / f".agents/graphics/deliveries/{request}/manifest.json").read_text(encoding="utf-8"))
        for item in data["items"]:
            found[item["id"]] = dict(item, intended_native_canvas=item.get("native_canvas") or CHEST_CANVAS,
                                    native_review_path=item.get("native_review_path", item["master_path"]))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(b3.INDEX.read_text(encoding="utf-8"))
    known = {a["id"] for a in catalog["assets"]}
    delivered = items()
    added = 0
    for name, spec in PARTS.items():
        if spec[0] in known:
            continue
        record, image = b3.build(name, spec, delivered[name])
        record["qa_approval"] = dict(APPROVAL)
        record["qa_notes"] = ("Codex image_gen master (" + delivered[name]["request_id"] + "); runtime part is a trimmed BOX downscale. "
                              "Footprint and collision are provisional and need scene calibration.")
        if spec[0] in COLLIDER:
            size, offset = COLLIDER[spec[0]]
            record["collision"] = {"enabled": True, "size": size, "offset": offset}
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
        b3.INDEX.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"registered {added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
