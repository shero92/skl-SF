"""Write the hero_room_01 v0019 patch: tune the v0018 terrace with unused ART-0032..0035 parts (TASK-0123).

Usage: python tools/build_v0019_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Moves the side wall runs outward off the floor, hides the hard front floor edge with the terrace edge
strips and adds the horizon haze strip. No historical file is edited.

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
SIDE_X = {"PerimeterWall_00_02": 243, "PerimeterWall_00_06": 243,
          "PerimeterWall_16_02": 1300, "PerimeterWall_16_06": 1300}
ADD = [  # layer, part, instance, x, y
    ("front_objects", "E032", "FrontEdgeStripLeftA", 450, 814),
    ("front_objects", "E032", "FrontEdgeStripLeftB", 740, 806),
    ("front_objects", "E032", "FrontEdgeStripRightA", 1050, 814),
    ("front_objects", "E032", "FrontEdgeStripRightB", 1290, 806),
    ("background_objects", "E035", "HorizonHaze", 768, 88),
]


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    changes = [{"op": "update_block", "instance_id": name, "set": {"x": x}} for name, x in SIDE_X.items()]
    changes += [{"op": "add_block", "layer": layer,
                 "block": {"id": part, "instance_id": name, "x": x, "y": y, "scale": 1.0}}
                for layer, part, name, x, y in ADD]
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0019: side wall runs moved outward, terrace edge strips on the front edge and the horizon haze strip (ART-0033/0034 parts). Visual approval pending.",
             "source_image": previous["source_image"], "changes": changes}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out, len(changes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
