"""Write the hero_room_01 v0024 patch: integrate the Codex B1/B2 candidates registered by register_b3_art.py (TASK-0145).

Usage: python tools/register_b3_art.py && python tools/build_v0024_patch.py   (then map_factory_cli.py apply --manifest <patch>)
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
    # Rear-left wall run with the small window opening (spec 4.3); same instance, so the mounted banner stays.
    update("PerimeterWall_03_00", id="W036"),
    # Closed arched wooden door with compass emblem replaces the ruined stone door in the right wall.
    update("RearRightDoor", id="A23", scale=1.5),
    # Side banners and wall lanterns: dedicated side views (east-facing on the west wall, west-facing on the east wall).
    update("LeftSideWallBanner", id="D24", scale=1.0),
    update("RightSideWallBanner", id="D26", scale=1.0),
    update("RightWallLantern2", id="L06", scale=1.0),
    update("RightWallLantern6", id="L06", scale=1.0),
]


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0024: integrate the owner-accepted Codex B3/ART-0023 graphics (compass wooden door, window wall piece, side banners, wall lantern) in place of the old instances. Visual approval is still pending.",
             "source_image": previous["source_image"],
             "changes": CHANGES}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
