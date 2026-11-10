"""Register the owner-approved ART-0032..ART-0035 masters as runtime parts (TASK-0122).

Usage: python tools/register_environment_art.py [--dry-run]

Each master (assets_hd/<...>/v001/<name>.png, never modified) is trimmed to its alpha bounding box and
resized (BOX filter, one subject per file) to a fixed on-screen width, written to
map_factory/parts/<category>/<ID>_<Name>.png and added to asset_index.json with the next free ID.
Origin is the bottom centre of the visible pixels. Re-running skips IDs that already exist.

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
    "evidence": "Owner chat 2026-11-10: all new graphics (ART-0032, ART-0033, ART-0034, ART-0035) agreed, start using them",
    "method": "independent image_gen masters kept unchanged in assets_hd; runtime part is a trimmed BOX downscale",
}

W, E, V = "walls", "environment", "vegetation"
# name: (id, category, subtype, master folder, on-screen width px, y_sort, tags)
ART = {
    "wall_straight_long_a": ("W027", W, "stone", "architecture/connected_ruin_walls", 320, True, ["wall", "straight", "ivy"]),
    "wall_straight_long_b": ("W028", W, "stone", "architecture/connected_ruin_walls", 320, True, ["wall", "straight", "ivy"]),
    "wall_corner_outer_left": ("W029", W, "stone", "architecture/connected_ruin_walls", 256, True, ["wall", "corner", "outer", "left"]),
    "wall_corner_outer_right": ("W030", W, "stone", "architecture/connected_ruin_walls", 256, True, ["wall", "corner", "outer", "right"]),
    "wall_corner_inner_left": ("W031", W, "stone", "architecture/connected_ruin_walls", 256, True, ["wall", "corner", "inner", "left"]),
    "wall_corner_inner_right": ("W032", W, "stone", "architecture/connected_ruin_walls", 256, True, ["wall", "corner", "inner", "right"]),
    "wall_side_left_run": ("W033", W, "stone", "architecture/connected_ruin_walls", 160, True, ["wall", "side", "left"]),
    "wall_side_right_run": ("W034", W, "stone", "architecture/connected_ruin_walls", 160, True, ["wall", "side", "right"]),
    "parapet_cap_run": ("W035", W, "stone", "architecture/connected_ruin_walls", 320, True, ["wall", "parapet", "cap"]),
    "cliff_face_front_a": ("E025", E, "cliff", "background/terrace_cliff", 320, False, ["cliff", "front", "rock"]),
    "cliff_face_front_b": ("E026", E, "cliff", "background/terrace_cliff", 320, False, ["cliff", "front", "rock"]),
    "cliff_face_front_c": ("E027", E, "cliff", "background/terrace_cliff", 320, False, ["cliff", "front", "rock"]),
    "cliff_rubble_cluster": ("E028", E, "cliff", "background/terrace_cliff", 128, True, ["cliff", "rubble", "rock"]),
    "foam_at_cliff_base": ("E029", E, "water", "background/terrace_cliff", 320, False, ["foam", "water", "cliff"]),
    "terrace_edge_corner_left": ("E030", E, "cliff", "background/terrace_cliff", 256, False, ["terrace", "edge", "corner", "left"]),
    "terrace_edge_corner_right": ("E031", E, "cliff", "background/terrace_cliff", 256, False, ["terrace", "edge", "corner", "right"]),
    "terrace_edge_straight": ("E032", E, "cliff", "background/terrace_cliff", 320, False, ["terrace", "edge", "straight"]),
    "foam_patch_a": ("E033", E, "water", "background/sea_coast", 192, False, ["foam", "water"]),
    "foam_patch_b": ("E034", E, "water", "background/sea_coast", 192, False, ["foam", "water"]),
    "horizon_haze_strip": ("E035", E, "sky", "background/sea_coast", 768, False, ["haze", "horizon", "sky"]),
    "rock_arch_far_left": ("E036", E, "rock", "background/sea_coast", 160, False, ["rock", "arch", "far", "left"]),
    "rock_arch_far_right": ("E037", E, "rock", "background/sea_coast", 160, False, ["rock", "arch", "far", "right"]),
    "sea_stack_tall_a": ("E038", E, "rock", "background/sea_coast", 128, False, ["rock", "sea_stack", "tall"]),
    "sea_stack_tall_b": ("E039", E, "rock", "background/sea_coast", 128, False, ["rock", "sea_stack", "tall"]),
    "sea_stack_tall_c": ("E040", E, "rock", "background/sea_coast", 128, False, ["rock", "sea_stack", "tall"]),
    "flower_mound_blue": ("V025", V, "foliage", "plants/coastal_garden", 96, True, ["flower", "mound", "blue"]),
    "flower_mound_white": ("V026", V, "foliage", "plants/coastal_garden", 96, True, ["flower", "mound", "white"]),
    "hanging_vine_long": ("V027", V, "foliage", "plants/coastal_garden", 40, False, ["vine", "hanging"]),
    "ivy_tuft_wall_a": ("V028", V, "foliage", "plants/coastal_garden", 96, False, ["ivy", "wall"]),
    "ivy_tuft_wall_b": ("V029", V, "foliage", "plants/coastal_garden", 96, False, ["ivy", "wall"]),
    "palm_clump_front_left": ("V030", V, "foliage", "plants/coastal_garden", 128, True, ["palm", "front", "left"]),
    "palm_clump_front_right": ("V031", V, "foliage", "plants/coastal_garden", 128, True, ["palm", "front", "right"]),
    "planter_stone_flowers_large": ("V032", V, "planter", "plants/coastal_garden", 128, True, ["planter", "stone", "flowers"]),
    "planter_stone_flowers_medium": ("V033", V, "planter", "plants/coastal_garden", 96, True, ["planter", "stone", "flowers"]),
}


def title(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("_"))


def build(name: str, spec: tuple) -> tuple[dict, Image.Image]:
    identifier, category, subtype, folder, width, y_sort, tags = spec
    master = ROOT / "assets_hd" / folder / "v001" / f"{name}.png"
    image = Image.open(master).convert("RGBA")
    box = image.getchannel("A").point(lambda v: 255 if v >= 128 else 0).getbbox()
    image = image.crop(box)
    height = max(1, round(image.height * width / image.width))
    image = image.resize((width, height), Image.Resampling.BOX)
    label = title(name)
    rel = f"map_factory/parts/{category}/{identifier}_{label.replace(' ', '_')}.png"
    record = {
        "id": identifier, "name": label, "category": category, "subtype": subtype,
        "texture_path": "res://" + rel, "status": "ready", "pixel_size": [width, height],
        "origin": [width // 2, height],
        "collision": {"enabled": False, "size": [32, 16], "offset": [0, 0]},
        "y_sort": y_sort,
        "shadow": {"type": "none", "opacity": 0.25, "offset_x": 4, "offset_y": 2},
        "tags": sorted(set(tags + [category])), "reusable": True,
        "source": {"kind": "image_gen_master", "master": master.relative_to(ROOT).as_posix(),
                   "master_sha256": hashlib.sha256(master.read_bytes()).hexdigest()},
        "qa_notes": "Codex image_gen master (ART-0032..0035), runtime part is a trimmed BOX downscale; owner agreed 2026-11-10.",
        "qa_approval": dict(APPROVAL),
    }
    return record, image


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    catalog = json.loads(INDEX.read_text(encoding="utf-8"))
    known = {a["id"] for a in catalog["assets"]}
    added = 0
    for name, spec in ART.items():
        if spec[0] in known:
            continue
        record, image = build(name, spec)
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
