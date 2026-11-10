"""Write the hero_room_01 v0021 patch: unified world Y-sort so characters pass behind/in front of walls and furniture (TASK-0128).

Usage: python tools/build_v0021_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Only the allowed map property `occlusion_mode` changes; no block, asset or position is touched.

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


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0021: occlusion_mode world_y_sort. Walls, decor and characters share one Y-sort so the hero is drawn in front of or behind furniture and walls by ground contact. No block, asset or position changed.",
             "source_image": previous["source_image"],
             "changes": [{"op": "set_property", "key": "occlusion_mode", "value": "world_y_sort"}]}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
