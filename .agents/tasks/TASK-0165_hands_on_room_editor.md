---
id: TASK-0165
status: review
owner: claude
agent: claude
priority: high
branch: claude/room-editor
depends_on: TASK-0164
issue: none
art_request: none
touches: .agents/tasks/TASK-0165_hands_on_room_editor.md,scenes/map_factory_editor.gd,scenes/map_factory_editor.tscn,scenes/main.gd,tools/room_editor_save.py,tools/verify_room_editor.gd,tools/tests/test_room_editor.py,tools/capture_game_window.gd,tools/test_map.json,docs/previews/map_factory_renders/t0165_editor/editor_window.png
test: python tools/run_tests.py --changed
done_when: The owner can open an editor from the room (F2), pick any catalog part, place it on a chosen level, move, resize, turn, flip and delete pieces, undo, and save; saving publishes a new immutable room version through the factory rules so F5 shows it. A headless test covers every operation and a dry-run save.
estimate_minutes: 180
---
# Hands-on room editor (first stage)

Owner (2026-11-11): "there is no real factory which I could run and build the room by myself". This is that tool, stage one.

- `scenes/map_factory_editor.tscn`: F2 in the room opens it (or run the scene directly); Esc returns.
  - Left panel: target level (background, ground, walls and back, furniture/plants/decor, front), part category, part list with pictures, Grid snap, Undo, Save, Back.
  - Mouse: click selects or places, drag moves, wheel resizes the selection (or zooms the view when nothing is selected), right/middle drag pans.
  - Keys: Q/E turn 15 degrees, F flip, Delete removes, arrows nudge one pixel, G grid snap, 1-5 target level, Ctrl+Z undo, Ctrl+S save.
- `tools/room_editor_save.py`: turns the editor's change list into one patch, validates it with the factory rules and applies it as the next version. A rejected edit leaves nothing behind.
- Walking still follows the grid: grid-placed parts keep their cells; the editor changes what is drawn (free_transform).

## Evidence / handoff
- `tools/verify_room_editor.gd` (registry id `room_editor`): every operation, undo back to the loaded room, and a dry-run save accepted by the factory.
- Real window capture: docs/previews/map_factory_renders/t0165_editor/editor_window.png. Nobody has edited and saved a room by hand yet.
- Not in this stage: painting ground tiles, editing the sea/sky settings, changing a piece's level after placing it, walkable-cell editing, multi-select, copy/paste, redo. Moved pieces keep their old shadow until the room is saved and reloaded. Saving needs `python` on PATH.
