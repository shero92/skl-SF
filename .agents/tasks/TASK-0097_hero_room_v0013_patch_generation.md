---
id: TASK-0097
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0096
issue: none
art_request: none
touches: tools/build_hero_room_blueprint.py,tools/tests/test_hero_room_v0013_patch.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_v0013_patch.py
done_when: tools/build_hero_room_blueprint.py can emit patches/v0013.json (patch version parameter) containing the full new layout using only v2 ids, without overwriting v0012.
estimate_minutes: 90
---
# Hero Room v0013 patch generation from approved assets

## Problem (evidence)
AUDIT: the room patch is written by tools/build_hero_room_blueprint.py main() to patches/v0012.json; the new layout from TASK-0091..0096 needs a v0013 patch that the operator applies with tools/map_factory_cli.py.

## Goal
tools/build_hero_room_blueprint.py can emit patches/v0013.json (patch version parameter) containing the full new layout using only v2 ids, without overwriting v0012.

## Implementation
Add a --patch-version argument (default 12 keeps current behavior) so main() writes patches/v0013.json with parent version 12. Add a pure function build_patch(version) usable from tests without writing files. Test: build_patch(13) has zero legacy ids, floor G-only, perimeter walls, lantern count >= 6, banner count >= 4, all four furniture directions declared, no object outside the canvas, and at least 70 distinct approved v2 PNGs used. Do not write any file in the test.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files (scenes/battle/, tools/verify_battle_*). Do NOT call main() of tools/build_hero_room_blueprint.py from tests or code you add: it rewrites committed v0012 patch files; import and call only layout_entries()/resolve_entries()/helper functions. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Router registration: add ONE entry for test_hero_room_v0013_patch.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] build_patch(13) satisfies all assertions; v0012 patch unchanged
- [ ] No PNG or generated asset changed
- [ ] `python tools/run_tests.py --changed` passes

## Expected result in Godot
After merge the operator applies v0013, validates, runs the Godot capture and compares with the reference. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_hero_room_v0013_patch.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
