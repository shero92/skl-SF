---
id: TASK-0168
status: review
owner: claude
agent: claude
priority: high
branch: claude/photo-backdrop-test
depends_on: TASK-0167
issue: none
art_request: ART-0050
touches: .agents/tasks/TASK-0168_hero_room_from_painting.md,.agents/graphics/requests/ART-0050_hero_room_painting_clean_plate.md,.agents/graphics/requests/reference_crops/ART-0050_painted_characters_target.png,scenes/main.gd,map_factory/photo_rooms/hero_room_01.json,tools/verify_main_equipment.gd,tools/capture_game_window.gd,docs/previews/map_factory_renders/photo_backdrop_test/photo_mode.png
test: python tools/run_tests.py --changed
done_when: F5 shows the hero room as the owner's target painting with the hero walking only on the painted floor and stairs; F3 switches to the Map Factory pieces and back; a headless test proves the painted bed, table and parapet are closed and the stairs are open.
estimate_minutes: 150
---
# Hero room built from the painting instead of tiles

Owner (2026-11-12): "lets try to create the room from the photo and do what we need to do instead of tiles".

- `map_factory/photo_rooms/hero_room_01.json`: the painting (reference file, unchanged), walk squares of 32 px measured on the painting, and moves for NPCs and interaction spots that the tile room had on painted furniture or plants.
- `scenes/main.gd`: the room starts as the painting. The Map Factory pieces are hidden and their furniture collisions rest; the hero's walk grid comes from the photo room. F3 switches to the pieces (map walk grid and collisions return) and back; the choice survives a visit to the editor or a battle.
- The Map Factory, the editor (F2) and battles are unchanged and still work on the tile map.

Not done here:
- The painting still has its painted hero and companion: ART-0050 asks Codex for the same painting without them.
- Characters never pass behind painted furniture; the walk squares are cut so that this is not needed.
- The side margins of the window are still flat blue.
- Editor and battle setup still use the tile map, not the painting's squares.
- No visual approval: nobody walked the room by hand.
