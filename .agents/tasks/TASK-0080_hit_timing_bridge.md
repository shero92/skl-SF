---
id: TASK-0080
status: done
owner: aider
agent: aider
priority: normal
branch: aider/task-0080
depends_on: TASK-0075,TASK-0076
issue: none
art_request: none
touches: scenes/battle/hit_timing_bridge.gd,tools/verify_hit_timing.gd,tools/tests/test_battle_hit_timing.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_hit_timing.py
done_when: Expose the timeline hit as a single signal so existing damage code can subscribe; do not change the damage system.
estimate_minutes: 45
---
# Hit timing to damage-event bridge

## Goal
Expose the timeline hit as a single signal so existing damage code can subscribe; do not change the damage system.

## Implementation
hit_timing_bridge.gd connects the controller hit signal to hit_confirmed(attacker, defender, attack_id, hit_index). Guarantees one emission per hit even with pause, frame step, restart and cancel.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] One emission per hit across pause/step/restart/cancel scenarios
- [ ] No file outside scenes/battle changed

## Test
`python -m unittest discover -s tools/tests -p test_battle_hit_timing.py`, then `python tools/run_tests.py --changed`.

## Estimate
45 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
