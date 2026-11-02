---
id: TASK-0092
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0091
issue: none
art_request: none
touches: map_factory/scripts/modular_room_builder.gd,tools/room_assembly.py,tools/tests/test_ground_wall_builder.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_ground_wall_builder.py
done_when: Floors, walls, corners, arches and pillars are built without gaps or wrong overlaps and sit on their own layers.
estimate_minutes: 90
---
# Ground and Wall Builder

## Goal
Floors, walls, corners, arches and pillars are built without gaps or wrong overlaps and sit on their own layers.

## Implementation
Fix floor tiling, wall runs, corner and arch/pillar placement in the modular builder and room_assembly.py. Add a coverage check: no uncovered floor cell, no wall overlapping floor cells incorrectly, correct z/layer per piece.

Scope: only the files listed in touches. Aider must not generate, edit, move or delete any image (PNG) and must not change assets_generated/ or assets/. Do not touch battle files (scenes/battle/, tools/verify_battle_*).

Router registration: add ONE entry for test_ground_wall_builder.py to tools/test_map.json (id, kind python, covers, command, paths) so test_router passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Builder output has zero floor gaps and zero illegal overlaps for the reference layout
- [ ] No PNG changed
- [ ] python tools/run_tests.py --changed passes

## Test
`python -m unittest discover -s tools/tests -p test_ground_wall_builder.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 for Map Factory automation. Record the real execution tool and model when run.
