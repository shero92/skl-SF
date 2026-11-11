"""hero_room_01 v0027: Codex chest views, oblique rugs and clouds placed with tools/room_design.py (TASK-0149).

Usage: python tools/build_v0027_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from room_design import Design

d = Design("hero_room_01")
# Oblique rugs drawn for this camera replace the flat ones. Rugs never block walking, so they are free decals.
d.remove("BedRug").remove("TableRug")
d.place("D27", "BedRugOblique", 450, 600, layer="ground_overlays")
d.place("D28", "TableRugOblique", 1122, 668, layer="ground_overlays")
# Plain-oak chest views replace the two front crates (off-grid; their colliders block the hero).
d.remove("CrateF12").remove("CrateF10")
d.place("F029", "FrontLeftChest", 470, 760)
d.place("F030", "FrontRightChest", 1236, 742)
# Independent cloud silhouettes in the sky.
d.place("B12", "SkyCloudA", 330, 62, layer="background_objects")
d.place("B13", "SkyCloudB", 900, 58, layer="background_objects")
d.place("B14", "SkyCloudC", 1290, 66, layer="background_objects")
print(d.write_patch("hero_room_01 v0027: oblique bedroom and study rugs (ART-0015), plain-oak chest views instead of the "
                    "front crates (ART-0021) and three independent clouds (ART-0002). Visual approval is still pending."))
