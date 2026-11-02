---
id: TASK-0076
status: todo
owner: aider
agent: aider
priority: high
branch: none
depends_on: TASK-0075
issue: none
art_request: none
touches: scenes/battle/battle_animation_controller.gd,tools/verify_battle_controller.gd,tools/tests/test_battle_controller.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_controller.py
done_when: Attacker/defender aware controller: Idle -> Attack -> Recovery -> Idle with safe cancel and reset.
estimate_minutes: 90
---
# BattleAnimationController state machine

## Goal
Attacker/defender aware controller: Idle -> Attack -> Recovery -> Idle with safe cancel and reset.

## Implementation
play_attack(attack_id, attacker, defender) returns a result dict (ok/reason). Unknown attack or missing assets returns a clear failure and changes nothing. Uses BattleTimeline. Emits started/hit/finished/cancelled signals. Actors are duck-typed (set_view(view), set_frame(name,index), reset()); no dependency on ModularBattleCharacter yet.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Valid attack walks Idle->Attack->Recovery->Idle
- [ ] A second play_attack while busy is rejected (documented)
- [ ] cancel() and reset() always return actors to Idle
- [ ] Missing attack id returns reason MISSING_ATTACK without side effects

## Test
`python -m unittest discover -s tools/tests -p test_battle_controller.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
