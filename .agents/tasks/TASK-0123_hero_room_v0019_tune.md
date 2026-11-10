---
id: TASK-0123
status: review
owner: claude
agent: claude
priority: medium
branch: claude/room-v0019
depends_on: TASK-0122
issue: none
art_request: none
touches: tools/build_v0019_patch.py,map_factory/maps/hero_room_01/,map_factory/maps/index.json,docs/previews/map_factory_renders/t0123_v0019/
test: python tools/run_tests.py --changed
done_when: hero_room_01 v0019 is published with the side walls moved off the floor, terrace edge strips on the front edge and the horizon haze strip, with a real Godot capture; visual_approval stays false.
estimate_minutes: 30
---
# Hero Room v0019: tune the new art

## Result (Claude, 2026-11-10)
v0019 (tools/build_v0019_patch.py): side wall runs 19px outward, four E032 terrace edge strips on the front edge, E035 haze strip at the horizon. Capture: docs/previews/map_factory_renders/t0123_v0019/. Still unused: straight/corner walls, parapet cap, sea stacks beyond those placed. Not owner-reviewed.
Next: owner review; replace the thin rear wall with the connected straight pieces.
