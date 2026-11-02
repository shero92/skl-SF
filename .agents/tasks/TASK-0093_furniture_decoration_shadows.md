---
id: TASK-0093
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0092
issue: none
art_request: none
touches: map_factory/scripts/modular_room_builder.gd,tools/room_assembly.py,tools/map_factory_layers.py,tools/tests/test_furniture_shadows.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_furniture_shadows.py
done_when: Bed, tables, rugs, decorations, lighting and shadows land in the correct layers with correct ordering.
estimate_minutes: 90
---
# Furniture, Decoration and Shadows

## Goal
Bed, tables, rugs, decorations, lighting and shadows land in the correct layers with correct ordering.

## Implementation
Fix placement and layer assignment for furniture, rugs, decorations, lights and shadows (layers: background, ground, walls, furniture_decor, shadows_overlays). Add checks for ordering and that shadows/overlays are above their source objects and below UI.

Scope: only the files listed in touches. Aider must not generate, edit, move or delete any image (PNG) and must not change assets_generated/ or assets/. Do not touch battle files (scenes/battle/, tools/verify_battle_*).

Router registration: add ONE entry for test_furniture_shadows.py to tools/test_map.json (id, kind python, covers, command, paths) so test_router passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Layer assignment test passes for the reference layout objects
- [ ] No PNG changed
- [ ] python tools/run_tests.py --changed passes

## Test
`python -m unittest discover -s tools/tests -p test_furniture_shadows.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 for Map Factory automation. Record the real execution tool and model when run.
