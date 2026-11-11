"""Write the hero_room_01 v0023 patch: integrate the Codex B1/B2 candidates registered by register_b1_b2_art.py (TASK-0144).

Usage: python tools/register_b1_b2_art.py && python tools/build_v0023_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Instance ids of replaced pieces are kept (lanterns, benches and the map stay mounted); old stair tiles and pillars are
removed and the new stair, finial posts, rope fence, compass, shelf, plant and stool are added at the owner-target
coordinates (docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md). Nothing is generated; history is never edited.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from map_factory_cli import digest_json  # noqa: E402

MAP = ROOT / "map_factory/maps/hero_room_01"


def update(name: str, **fields) -> dict:
    return {"op": "update_block", "instance_id": name, "set": fields}


def remove(name: str) -> dict:
    return {"op": "remove_block", "instance_id": name}


def add(layer: str, part: str, name: str, x: float, y: float, scale: float = 1.0, render_layer: str = "decorations") -> dict:
    return {"op": "add_block", "layer": layer,
            "block": {"id": part, "instance_id": name, "x": x, "y": y, "scale": scale, "render_layer": render_layer}}


CHANGES = [
    # Study table: the front view replaces the roof-like old one; other views are kept mapped for later rotation.
    # Items mounted on the table: the new table is 1.55x larger, so the vertical offsets are reduced to land on its top face.
    # The table faces south, which rotates mount offsets by 180 degrees, so both signs are flipped.
    *[update(n, mount_offset=[x, y]) for n, x, y in (
        ("DiningLantern", -65.0, 80), ("DiningCandles", 65.0, 80), ("TableScroll", 90.0, 80), ("TableMap", 30.0, 80),
        ("TableBook", 0.0, 80), ("TableFruitBowl", -30.0, 80), ("TableJug", -95.0, 80),
        ("DiningLanternGlow", -65.0, 92), ("DiningCandlesGlow", 65.0, 90))],
    remove("DiningTable"),  # re-added with the same id but without the old grid_placement (the new part has no floor contract yet)
    {"op": "add_block", "layer": "objects", "block": {
        "id": "P27", "instance_id": "DiningTable", "x": 1122.0, "y": 609, "scale": 1.55, "render_layer": "decorations",
        "facing": "south", "orientation_mode": "variants",
        "direction_asset_ids": {"north": "P28", "east": "P29", "south": "P27", "west": "P30"},
        "shadow": {"type": "table", "opacity": 0.3, "offset_x": 4, "offset_y": 0}}},
    update("StudyStool", id="P31", scale=1.2),
    # Right bookshelf with the armillary, candles and crates baked into the picture (removes the loose armillary prop).
    remove("RightShelfCandles"), remove("RightShelfCandlesGlow"),  # the candles are part of the new shelf picture
    remove("RightBookcase"),  # only north/south views exist, so the new shelf is a plain (non-rotating) block
    add("objects", "P32", "RightBookshelf", 1191, 437, render_layer="decorations"),
    remove("BookshelfArmillary"),
    add("objects", "P34", "HeadboardShelf", 315, 300),
    add("objects", "V034", "BluePlanter", 1335, 498),
    # Compass inlay: same instance, new oblique art, spec position.
    remove("CompassFloorEmblem"),
    add("ground_overlays", "D20", "CompassInlay", 761, 724, render_layer="ground"),
    # Entrance stair: the four stacked tiles, two supports and two plain pillars are replaced by one stair and two finial posts.
    *[remove(n) for n in ("StairStep1", "StairStep2", "StairStep3", "StairStep4", "StairSupportLeft", "StairSupportRight",
                          "EntrancePillarLeft", "EntrancePillarRight")],
    add("back_objects", "A19", "EntranceStair", 737, 1024, render_layer="walls"),
    add("objects", "A20", "FinialPostLeft", 622, 812),
    add("objects", "A20", "FinialPostRight", 852, 812),
    # Rope-and-post terrace fences on both edges.
    add("objects", "D21", "RopePostWestFar", 214, 660),
    add("objects", "D21", "RopePostWestNear", 286, 742),
    add("objects", "D22", "RopeWest", 250, 700),
    add("objects", "D21", "RopePostEastFar", 1214, 660),
    add("objects", "D21", "RopePostEastNear", 1286, 742),
    add("objects", "D23", "RopeEast", 1250, 700),
]


RENAMED_OBSTACLES = {"EntrancePillarLeft": "FinialPostLeft", "EntrancePillarRight": "FinialPostRight", "RightBookcase": "RightBookshelf"}


def navigation_with_new_obstacles(latest: dict) -> dict:
    navigation = json.loads(json.dumps(latest["navigation"]))
    for obstacle in navigation["obstacles"]:
        obstacle["instance_id"] = RENAMED_OBSTACLES.get(obstacle["instance_id"], obstacle["instance_id"])
    return navigation


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0023: integrate the Codex B1/B2 candidates (study table, stool, bookshelf with armillary, headboard shelf, blue-white plant, entrance stair with finial posts, rope fences, compass inlay). Positions follow the owner target; visual approval is still pending.",
             "source_image": previous["source_image"],
             "changes": CHANGES + [{"op": "set_property", "key": "navigation", "value": navigation_with_new_obstacles(latest)}]}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
