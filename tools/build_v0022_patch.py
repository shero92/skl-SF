"""Write the hero_room_01 v0022 patch: registered props from the owner target placed in the room (TASK-0135).

Usage: python tools/build_v0022_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Only add_block operations with already registered, ready or needs_cleanup parts (O001/O003 blue vases, R12 armillary,
R13 conch, O022 shell, P012 stool). No art is generated, nothing existing moves, no historical file is edited.

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
# part, instance id, x, y (bottom anchor), scale. Positions follow the owner target (1125x750 reference x 1.3653).
PROPS = [
    ("O001", "ArchUrnLeft", 572, 350, 0.42),
    ("O001", "ArchUrnRight", 1057, 410, 0.42),
    ("R13", "BedsideConch", 262, 462, 0.42),
    ("R13", "FrontConch", 1113, 746, 0.42),
    ("O003", "FrontBlueVase", 1177, 746, 0.36),
    ("R12", "BookshelfArmillary", 1052, 262, 0.55),
    ("P012", "StudyStool", 1157, 655, 0.33),
]


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0022: occlusion_mode world_y_sort. Walls, decor and characters share one Y-sort so the hero is drawn in front of or behind furniture and walls by ground contact. No block, asset or position changed.",
             "source_image": previous["source_image"],
             "changes": [{"op": "add_block", "layer": "objects",
                          "block": {"id": part, "instance_id": name, "x": x, "y": y, "scale": scale, "render_layer": "decorations"}}
                         for part, name, x, y, scale in PROPS]}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
