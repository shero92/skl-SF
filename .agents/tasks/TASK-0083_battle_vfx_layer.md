---
id: TASK-0083
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0075,TASK-0079
issue: none
art_request: none
touches: scenes/battle/battle_vfx_layer.gd,tools/verify_battle_vfx.gd,tools/tests/test_battle_vfx.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_vfx.py
done_when: Effects live on their own layer, never baked into body or weapon, and follow the weapon socket path.
estimate_minutes: 75
---
# Separate VFX layer and sword trail path

## Goal
Effects live on their own layer, never baked into body or weapon, and follow the weapon socket path.

## Implementation
VFX layer node with named effect slots, per-frame socket sampling to build a trail polyline, on/off toggle, clear(). Uses existing effect assets by id only; none generated.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Toggling VFX off leaves body and weapon untouched
- [ ] Trail points equal the socket samples
- [ ] clear() leaves no children

## Test
`python -m unittest discover -s tools/tests -p test_battle_vfx.py`, then `python tools/run_tests.py --changed`.

## Estimate
75 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
