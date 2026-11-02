---
id: TASK-0094
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0093
issue: none
art_request: none
touches: tools/build_hero_room_blueprint.py,tools/tests/test_hero_room_lighting_decor.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_lighting_decor.py
done_when: Lanterns along walls and beside bed and table, candles on shelves and table, blue banners on wall blocks, ivy and flowers on wall tops, vases and books, all on the correct layer.
estimate_minutes: 90
---
# Lanterns, candles, banners, ivy and decoration placement

## Problem (evidence)
AUDIT: v0012 has only 2 L01 hanging lanterns and 3 glow effects. The registry has L01-L05 (wall lantern, glowless base, candle cluster, table lantern, flame glow), D banners and trims, P ivy/flower/bush and R vases/books/maps/fruit. 83 of the 128 v2 assets are not referenced by the room.

## Goal
Lanterns along walls and beside bed and table, candles on shelves and table, blue banners on wall blocks, ivy and flowers on wall tops, vases and books, all on the correct layer.

## Implementation
In tools/build_hero_room_blueprint.py add placements: wall lanterns (L01/L02) spaced along side walls, candle cluster L03 on the bookcase and table, table lantern L04, glow overlay L05 over each lit lantern (front/overlay layer, never behind the wall), banners D04/D05 on wall mount blocks, ivy P01-P03 hanging from wall tops, flower and bush clusters at wall bases, vases and R-series props near furniture. Mount only on wall cells created by TASK-0093. Test asserts layer assignment (glow overlays in front layer, banners in back layer), that every decor item sits on a wall cell or on its parent furniture, and ids exist in v2.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files (scenes/battle/, tools/verify_battle_*). Do NOT call main() of tools/build_hero_room_blueprint.py from tests or code you add: it rewrites committed v0012 patch files; import and call only layout_entries()/resolve_entries()/helper functions. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Router registration: add ONE entry for test_hero_room_lighting_decor.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Lighting, banners and decor placed on valid mounts and layers
- [ ] No PNG or generated asset changed
- [ ] `python tools/run_tests.py --changed` passes

## Expected result in Godot
Visible lanterns with glow, banners, ivy and flowers like the reference. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_hero_room_lighting_decor.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
