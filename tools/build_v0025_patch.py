"""Write the hero_room_01 v0025 patch: move the rope fences onto the visible floor corners (TASK-0146).

Usage: python tools/build_v0025_patch.py   (then map_factory_cli.py apply --manifest <patch>)
The same change set gives the B1-B3 furniture parts provisional base colliders in the catalog (asset_index.json).
Nothing is generated; history is never edited.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
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
    # Rope fences: the v0023 positions were behind the side walls under Y-sorting; move them onto the visible floor corners.
    update("RopePostWestFar", x=352.0, y=668.0), update("RopePostWestNear", x=420.0, y=748.0), update("RopeWest", x=386.0, y=712.0),
    update("RopePostEastFar", x=1218.0, y=668.0), update("RopePostEastNear", x=1140.0, y=752.0), update("RopeEast", x=1179.0, y=714.0),
]


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0025: rope fences moved onto the visible floor corners; the B1-B3 furniture parts now carry provisional base colliders from the catalog. Visual approval is still pending.",
             "source_image": previous["source_image"],
             "changes": CHANGES}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
