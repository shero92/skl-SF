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
touches: tools/build_hero_room_blueprint.py,tools/map_factory_cli.py,tools/capture_map_previews.gd,tools/tests/test_hero_room_assembly.py,tools/test_map.json,map_factory/maps/hero_room_01
test: python -m unittest discover -s tools/tests -p test_hero_room_assembly.py
done_when: Map Factory rebuilds hero_room_01 from the registered new assets as a new version, validates, and a real Godot screenshot is captured.
estimate_minutes: 90
---
# Hero Room Assembly and Verification

## Goal
Map Factory rebuilds hero_room_01 from the registered new assets as a new version, validates, and a real Godot screenshot is captured.

## Implementation
Rebuild hero_room_01 as the next version via map_factory_cli using only registered assets, validate it, and make the capture script write the Godot render. Test checks version validity, layers present and that every placed asset id exists in the registry. The real Godot capture is run by the operator after merge.

Scope: only the files listed in touches. Aider must not generate, edit, move or delete any image (PNG) and must not change assets_generated/ or assets/. Do not touch battle files (scenes/battle/, tools/verify_battle_*).

Router registration: add ONE entry for test_hero_room_assembly.py to tools/test_map.json (id, kind python, covers, command, paths) so test_router passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] hero_room_01 next version validates; test passes; capture command documented in the task result
- [ ] No PNG changed
- [ ] python tools/run_tests.py --changed passes

## Test
`python -m unittest discover -s tools/tests -p test_hero_room_assembly.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 for Map Factory automation. Record the real execution tool and model when run.
