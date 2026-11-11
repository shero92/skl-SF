"""hero_room_01 v0029: the camera shows the whole 1536x1024 room in the 1536x864 window (TASK-0164).

Usage: python tools/build_v0029_patch.py   (then map_factory_cli.py apply --manifest <patch>)
Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from room_design import Design

d = Design("hero_room_01")
# 864 / 1024: the full canvas height fits the window, so sky, clouds, stairs and cliff foam are all on screen.
d.set_property("camera", {"x": 768, "y": 512, "zoom": 0.84375})
# The front-left chest sat half behind the parapet; move it up onto the open floor.
d.transform("FrontLeftChest", x=470, y=742)
print(d.write_patch("hero_room_01 v0029: camera zoom 0.84375 so the whole room height is visible in the game window; "
                    "front-left chest moved clear of the parapet. Visual approval is still pending."))
