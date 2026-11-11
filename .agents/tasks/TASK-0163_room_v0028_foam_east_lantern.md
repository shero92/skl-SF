---
id: TASK-0163
status: review
owner: claude
agent: claude
priority: medium
branch: claude/room-v0028
depends_on: TASK-0149
issue: none
art_request: ART-0040
touches: .agents/tasks/TASK-0163_room_v0028_foam_east_lantern.md,tools/register_b5_art.py,tools/build_v0028_patch.py,tools/room_design.py,tools/tests/test_room_design.py,.agents/graphics/deliveries/ART-0040,.agents/graphics/requests/ART-0040_hero_room_wall_lantern_east.md,assets_hd/lighting/east_wall_lantern/v001,map_factory/metadata/asset_index.json,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/blocks/latest.json,map_factory/maps/hero_room_01/layers/latest.json,map_factory/maps/index.json,docs/previews/map_factory_renders/t0163_v0028/hero_room_01_v0028.png
test: python tools/run_tests.py --changed
done_when: Codex's finished east wall lantern master is delivered as ART-0040 unchanged, the lantern and the four ART-0003 foam phases are registered, and hero_room_01 v0028 shows the lanterns on the west wall and animated foam at the cliff base in a real Godot capture with green tests; visual approval stays false.
estimate_minutes: 60
---
# hero_room_01 v0028: east wall lantern and animated cliff foam

Owner (2026-11-11): Codex is paused for three hours; Claude takes over what is needed.

- ART-0040: Codex had drawn `assets_hd/lighting/east_wall_lantern/v001/hero_wall_lantern_east.png` and left it uncommitted in the main checkout (kept in branch `backup/local-changes-20261111c`). `tools/register_b5_art.py` copies it byte for byte to the delivery path, writes the manifest and marks the request delivered. Nothing was redrawn.
- Parts: L07 (east-pointing lantern, 29x47), B15-B18 (foam phases, fixed 96x48 frames so they stay registered).
- `tools/room_design.py`: `place(..., animation={"frames": [...], "fps": n})`.
- v0028: LeftWallLantern2/6 use L07; four foam strips cycle at 4 fps at the cliff base.

## Evidence / handoff
- Real Godot capture: docs/previews/map_factory_renders/t0163_v0028/ (visual_approval stays false). The capture is one still frame; the foam cycle itself was not watched in a window.
- Lantern wall-mount offset and foam contact height are provisional.
- This covers the lantern half of TASK-0153 and TASK-0160; the ART-0037 sea light regeneration is still open for Codex.
