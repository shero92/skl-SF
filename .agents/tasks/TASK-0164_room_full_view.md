---
id: TASK-0164
status: review
owner: claude
agent: claude
priority: high
branch: claude/room-full-view
depends_on: TASK-0163
issue: none
art_request: none
touches: .agents/tasks/TASK-0164_room_full_view.md,tools/build_v0029_patch.py,tools/capture_game_window.gd,tools/room_design.py,scenes/main.gd,map_factory/scripts/room_factory.gd,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/blocks/latest.json,map_factory/maps/hero_room_01/layers/latest.json,map_factory/maps/index.json,docs/previews/map_factory_renders/t0164_v0029/game_window.png
test: python tools/run_tests.py --changed
done_when: Pressing F5 shows the whole hero room (sky and clouds at the top, stairs and cliff foam at the bottom) in the game window, proven by a capture of the real window, with green tests.
estimate_minutes: 30
---
# The whole room is visible in the game window

Owner (2026-11-11): the window cut about 80 px off the top and the bottom of the 1536x1024 room (window is 1536x864).

- hero_room_01 v0029: camera zoom 0.84375 (864 / 1024); the front-left chest moved clear of the parapet.
- `scenes/main.gd` clears the window with the map backdrop colour, so the margin beside the canvas is sea blue.
- `tools/room_design.py`: `Design.set_property(key, value)`.
- `tools/capture_game_window.gd`: saves what the real game window shows.

## Evidence / handoff
- Real window capture: docs/previews/map_factory_renders/t0164_v0029/game_window.png (1280x720 window).
- The side margins (about 110 px each at 1280 wide) are flat blue: the ocean tiles and waves stop at the canvas edge. Extending the sea past the canvas is not done.
