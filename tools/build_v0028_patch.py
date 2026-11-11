"""hero_room_01 v0028: east-pointing lanterns on the west wall and animated cliff foam (TASK-0163).

Usage: python tools/build_v0028_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from room_design import Design

FOAM = {"frames": ["B15", "B16", "B17", "B18"], "fps": 4}

d = Design("hero_room_01")
# West wall: the east-pointing lantern (ART-0040) mirrors the L06 pair on the east wall.
d.transform("LeftWallLantern2", part="L07", scale=1.0)
d.transform("LeftWallLantern6", part="L07", scale=1.0)
# Four-phase foam (ART-0003) where the cliff base meets the sea, left and right of the stairs.
for name, x, y in (("CliffFoamWestA", 250, 1040), ("CliffFoamWestB", 480, 1046),
                   ("CliffFoamEastA", 1030, 1046), ("CliffFoamEastB", 1280, 1040)):
    d.place("B15", name, x, y, scale=2.0, layer="background_objects", animation=FOAM)
print(d.write_patch("hero_room_01 v0028: east-pointing brass lanterns (ART-0040) on the west wall and four-phase animated "
                    "cliff foam (ART-0003) at the cliff base. Visual approval is still pending."))
