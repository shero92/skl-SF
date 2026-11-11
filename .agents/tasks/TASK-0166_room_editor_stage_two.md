---
id: TASK-0166
status: review
owner: claude
agent: claude
priority: high
branch: claude/room-editor-2
depends_on: TASK-0165
issue: none
art_request: none
touches: .agents/tasks/TASK-0166_room_editor_stage_two.md,scenes/map_factory_editor.gd,tools/room_editor_save.py,tools/verify_room_editor.gd,tools/tests/test_room_editor.py,docs/previews/map_factory_renders/t0165_editor/editor_window_stage2.png
test: python tools/run_tests.py --changed
done_when: In the editor the owner can open any map of the registry, create a new empty map from a preset, paint floor squares and remove squares from the floor shape, copy a piece, move a piece to another level, hide or show a level, and redo; every edit saves as a new immutable version through the factory rules, and a headless test covers each operation.
estimate_minutes: 150
---
# Room editor, stage two: whole maps

Owner (2026-11-11): "improve the factory even more so I can build complete maps and fight maps and others by myself".

- Maps: a list of every map in the registry; "Create new map" makes an empty map from a factory preset (indoor_room, courtyard, dungeon, coast, sky_island) and opens it.
- Ground: pick a part from `floors` and click or drag over squares to paint them; "Erase floor squares" removes squares from the floor shape. A painted square outside the shape joins it.
- Pieces: Ctrl+D copies the selection, PageUp/PageDown moves it to another level, Shift+1-5 hides or shows a level, Ctrl+Y redoes.
- The map is fitted beside the panel when it loads.
- `tools/room_editor_save.py`: `tile` and `floor_footprint` changes, and `--new <map_id> --preset <name>`.

## Evidence / handoff
- `tools/verify_room_editor.gd`: ground paint and erase with a dry-run save, undo/redo, copy, level change with a dry-run save, hide/show, opening another map, new-map name and preset checks.
- Real window capture: docs/previews/map_factory_renders/t0165_editor/editor_window_stage2.png. Nobody has built a map by hand with it yet.
- Ground edits are previewed flat in the editor; joints and shading appear after saving. A piece moved to another level keeps its old draw order until saved.
- Not done: battle maps (blocked squares, unit start squares, playing a skirmish on an edited map), map size change, sea/sky/light settings, walkable-region editing, multi-select.
