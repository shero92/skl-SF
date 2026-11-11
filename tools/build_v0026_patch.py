"""hero_room_01 v0026: first use of free_transform and tools/room_design.py (TASK-0148).

Usage: python tools/build_v0026_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from room_design import Design

d = Design("hero_room_01")
# Target: the bed stands on a wide blue rug. The rug keeps its grid cell; only the drawn sprite grows and moves.
d.transform("BedRug", x=450, y=660, scale=1.8)
# Target: flowers at both arch bases. Independent decor placed off-grid, turned and resized.
d.place("V025", "ArchBaseFlowersLeft", 640, 305, scale=0.7, rotation=-8)
d.place("P05", "ArchBaseFlowersRight", 850, 305, scale=0.8, rotation=14, flip=True)
print(d.write_patch("hero_room_01 v0026: bed rug enlarged and re-centred under the bed with free_transform; "
                    "two independent flower pieces placed off-grid at the arch bases, turned and resized. "
                    "Visual approval is still pending."))
