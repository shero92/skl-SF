"""Write the hero_room_01 v0020 patch: connected straight wall runs (ART-0032) replace the thin rear wall (TASK-0124).

Usage: python tools/build_v0020_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Two host instances keep their mounted banners; the other rear wall pieces are removed. No historical file is edited.

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
REMOVE = ["PerimeterWall_01_00", "PerimeterWall_02_00", "PerimeterWall_04_00",
          "PerimeterWall_11_00", "PerimeterWall_12_00", "PerimeterWall_14_00", "PerimeterWall_15_00"]
HOSTS = {  # host instance (keeps its mounted banner) -> connected straight run
    "PerimeterWall_03_00": {"id": "W027", "x": 402, "y": 289, "scale": 1.05},
    "PerimeterWall_13_00": {"id": "W028", "x": 1122, "y": 289, "scale": 1.2},
}


def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    changes = [{"op": "remove_block", "instance_id": name} for name in REMOVE]
    changes += [{"op": "update_block", "instance_id": name, "set": values} for name, values in HOSTS.items()]
    patch = {"manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
             "base_sha256": digest_json(latest),
             "note": "hero_room_01 v0020: the thin rear wall pieces are replaced by the connected straight wall runs W027 and W028 (ART-0032); banners stay mounted on host instances. Visual approval pending.",
             "source_image": previous["source_image"], "changes": changes}
    out = MAP / "patches" / f"v{latest['version'] + 1:04d}.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out, len(changes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
