---
id: TASK-0091
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0090
issue: none
art_request: none
touches: tools/map_factory_orientation.py,tools/map_factory_placement.py,tools/tests/test_block_rotation.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_block_rotation.py
done_when: Blocks place correctly at 0, 90, 180 and 270 degrees using the matching directional image when one exists, never rotating a drawing whose perspective would break.
estimate_minutes: 90
---
# Block Rotation and Placement

## Goal
Blocks place correctly at 0, 90, 180 and 270 degrees using the matching directional image when one exists, never rotating a drawing whose perspective would break.

## Implementation
Fix orientation resolution in map_factory_orientation.py/map_factory_placement.py: choose the directional asset id for each rotation, fall back to a transform only for assets flagged rotation_safe, and reject others with a clear error. Add footprint and anchor handling for rotated blocks.

Scope: only the files listed in touches. Aider must not generate, edit, move or delete any image (PNG) and must not change assets_generated/ or assets/. Do not touch battle files (scenes/battle/, tools/verify_battle_*).

Router registration: add ONE entry for test_block_rotation.py to tools/test_map.json (id, kind python, covers, command, paths) so test_router passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] All four rotations resolve to the correct asset and footprint; unsafe rotation is rejected
- [ ] No PNG changed
- [ ] python tools/run_tests.py --changed passes

## Test
`python -m unittest discover -s tools/tests -p test_block_rotation.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 for Map Factory automation. Record the real execution tool and model when run.
