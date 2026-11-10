---
id: TASK-0124
status: review
owner: claude
agent: claude
priority: medium
branch: claude/room-v0020
depends_on: TASK-0123
issue: none
art_request: none
touches: tools/build_v0020_patch.py,map_factory/maps/hero_room_01/,map_factory/maps/index.json,docs/previews/map_factory_renders/t0124_v0020/
test: python tools/run_tests.py --changed
done_when: hero_room_01 v0020 is published with the connected straight wall runs W027/W028 (ART-0032) replacing the thin rear wall pieces, banners still mounted, with a real Godot capture; visual_approval stays false.
estimate_minutes: 30
---
# Hero Room v0020: connected rear wall

## Result (Claude, 2026-11-10)
tools/build_v0020_patch.py removes 7 thin rear wall pieces and turns PerimeterWall_03_00 / PerimeterWall_13_00 (banner hosts) into W027 / W028. The right rear wall is now one connected ruin behind the door; the left one is mostly behind the bookcase. Capture: docs/previews/map_factory_renders/t0124_v0020/. Not owner-reviewed. Still unused: corner pieces and parapet cap.
Next: owner review; use the corner/parapet pieces where the rear wall meets the side runs.
