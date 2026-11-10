"""Write the hero_room_01 v0018 patch: the approved ART-0032..0035 parts around the terrace (TASK-0122).

Usage: python tools/build_v0018_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Only add_block / remove_block operations on top of the latest snapshot; no historical file is edited.

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

# (layer, part id, instance id, x, y, scale). y is the bottom anchor of the sprite.
BLOCKS = [
    # distant sea: arches, stacks, foam (behind everything)
    ("background_objects", "E036", "CoastArchFarLeft", 170, 300, 1.0),
    ("background_objects", "E037", "CoastArchFarRight", 1380, 300, 1.0),
    ("background_objects", "E039", "CoastStackTallLeft", 70, 640, 1.0),
    ("background_objects", "E038", "CoastStackTallRight", 1470, 600, 1.0),
    ("background_objects", "E040", "CoastStackLow", 1400, 740, 1.0),
    ("background_objects", "E033", "SeaFoamLeft", 140, 760, 1.0),
    ("background_objects", "E034", "SeaFoamRight", 1380, 800, 1.0),
    # terrace cliff under the front edge (the floor hides the upper rim)
    ("background_objects", "E026", "CliffFrontLeftOuter", 300, 985, 1.0),
    ("background_objects", "E025", "CliffFrontLeftInner", 520, 930, 1.0),
    ("background_objects", "E027", "CliffFrontRightInner", 1060, 1010, 1.0),
    ("background_objects", "E026", "CliffFrontRightOuter", 1270, 985, 1.0),
    ("background_objects", "E029", "CliffFoamLeftOuter", 300, 1000, 1.0),
    ("background_objects", "E029", "CliffFoamLeftInner", 520, 960, 1.0),
    ("background_objects", "E029", "CliffFoamRightInner", 1060, 1015, 1.0),
    ("background_objects", "E029", "CliffFoamRightOuter", 1270, 1000, 1.0),
    ("background_objects", "E028", "CliffRubbleLeft", 200, 1005, 1.0),
    ("background_objects", "E028", "CliffRubbleRight", 1340, 1005, 1.0),
    # terrace corners
    ("front_objects", "E030", "TerraceCornerLeft", 262, 905, 1.0),
    ("front_objects", "E031", "TerraceCornerRight", 1280, 905, 1.0),
    # hanging vines and ivy on the back wall
    ("front_objects", "V027", "BackWallVineLeft", 322, 300, 1.0),
    ("front_objects", "V027", "BackWallVineRight", 1154, 300, 1.0),
    ("front_objects", "V028", "BackWallIvyLeft", 420, 210, 1.0),
    ("front_objects", "V029", "BackWallIvyRight", 1060, 210, 1.0),
    # front garden: planters, mounds and palms
    ("objects", "V032", "FrontPlanterLeft", 310, 800, 1.0),
    ("objects", "V032", "FrontPlanterRight", 1240, 800, 1.0),
    ("objects", "V033", "FrontPlanterLeftInner", 560, 830, 1.0),
    ("objects", "V033", "FrontPlanterRightInner", 980, 830, 1.0),
    ("objects", "V025", "FrontMoundBlue", 440, 815, 1.0),
    ("objects", "V026", "FrontMoundWhite", 1110, 815, 1.0),
    ("objects", "V030", "FrontPalmLeft", 258, 770, 1.0),
    ("objects", "V031", "FrontPalmRight", 1285, 770, 1.0),
]

# side cliffs under the left/right walls and connected side wall runs replacing the thin wall stacks
BLOCKS += [
    ("background_objects", "E027", "CliffSideLeftUpper", 215, 520, 1.0),
    ("background_objects", "E026", "CliffSideLeftLower", 215, 760, 1.0),
    ("background_objects", "E026", "CliffSideRightUpper", 1325, 520, 1.0),
    ("background_objects", "E027", "CliffSideRightLower", 1325, 760, 1.0),
]
# Side wall runs reuse two existing wall instances as hosts so every mounted lantern/banner/ivy keeps a target.
SIDE_HOSTS = {  # side -> (part, x, [(host instance, y)])
    "00": ("W033", 262, [("PerimeterWall_00_02", 480), ("PerimeterWall_00_06", 740)]),
    "16": ("W034", 1282, [("PerimeterWall_16_02", 480), ("PerimeterWall_16_06", 740)]),
}
REMOVE = [f"PerimeterWall_{col}_{row:02d}" for col in ("00", "16") for row in (1, 3, 4, 5, 7)]
REMOUNT = {  # decoration -> new host
    **{n: "PerimeterWall_00_02" for n in ("WallTopIvy0", "LeftSideWallBanner")},
    **{n: "PerimeterWall_00_06" for n in ("LeftWallLantern4", "LeftWallLantern4Glow", "WallTopIvy2")},
    **{n: "PerimeterWall_16_02" for n in ("WallTopIvy1", "RightSideWallBanner")},
    **{n: "PerimeterWall_16_06" for n in ("RightWallLantern4", "RightWallLantern4Glow", "WallTopIvy3")},
}

def main() -> int:
    latest = json.loads((MAP / "latest.json").read_text(encoding="utf-8"))
    previous = json.loads((MAP / "patches" / f"v{latest['version']:04d}.json").read_text(encoding="utf-8"))
    changes = [{"op": "update_block", "instance_id": name, "set": {"mount_on": host}} for name, host in REMOUNT.items()]
    changes += [{"op": "remove_block", "instance_id": name} for name in REMOVE]
    for part, x, hosts in SIDE_HOSTS.values():
        changes += [{"op": "update_block", "instance_id": host, "set": {"id": part, "x": x, "y": y, "scale": 1.0}} for host, y in hosts]
    changes += [{"op": "add_block", "layer": layer,
                "block": {"id": part, "instance_id": name, "x": x, "y": y, "scale": scale}}
               for layer, part, name, x, y, scale in BLOCKS]
    patch = {
        "manifest_version": 1, "map_id": "hero_room_01", "base_version": latest["version"],
        "base_sha256": digest_json(latest),
        "note": "hero_room_01 v0018: the owner-agreed ART-0032..0035 parts (cliff base, coast stacks and arches, foam, planters, palms, vines) added around the terrace; existing pieces untouched. Visual approval pending.",
        "source_image": previous["source_image"],
        "changes": changes,
    }
    out = ROOT / "map_factory/maps/hero_room_01/patches/v0018.json"
    out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(out, len(changes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
