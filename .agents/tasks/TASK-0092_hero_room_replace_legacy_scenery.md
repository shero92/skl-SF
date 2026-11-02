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
touches: tools/build_hero_room_blueprint.py,tools/tests/test_hero_room_scenery.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_scenery.py
done_when: Background islands and corner foundations come from approved v2 assets (sea stacks, near and far cliff rock segments); no legacy E*/S* ids remain in the layout.
estimate_minutes: 90
---
# Replace needs_cleanup islands and foundations with approved v2 parts

## Problem (evidence)
AUDIT: background_objects use E015/E016/E017 (islands) and front_objects E023/E024 (coastal foundations), all needs_cleanup without qa_approval. The E023/E024 foundations at the bottom corners sit exactly over the W10 low broken wall segments placed at y=893, so the lower wall is not visible in the v0012 render.

## Goal
Background islands and corner foundations come from approved v2 assets (sea stacks, near and far cliff rock segments); no legacy E*/S* ids remain in the layout.

## Implementation
In tools/build_hero_room_blueprint.py replace E015-E017 with approved sea_stack_island_small/medium and distant_rock_arch_formation ids, and E023/E024 with approved near_cliff_rock_segment placements positioned so they do not overlap the lower wall run. Use v2 ids by registry key; keep canvas and floor untouched. Test: no id from the E, F00x or S0xx families in the layout; every id is in v2; cliff boxes do not overlap lower wall boxes.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files (scenes/battle/, tools/verify_battle_*). Do NOT call main() of tools/build_hero_room_blueprint.py from tests or code you add: it rewrites committed v0012 patch files; import and call only layout_entries()/resolve_entries()/helper functions. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Router registration: add ONE entry for test_hero_room_scenery.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] No legacy scenery ids in layout; cliffs do not hide the lower wall
- [ ] No PNG or generated asset changed
- [ ] `python tools/run_tests.py --changed` passes

## Expected result in Godot
Ocean islands and bottom corner cliffs appear from approved art and the lower wall stays visible. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_hero_room_scenery.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
