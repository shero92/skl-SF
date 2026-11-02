---
id: TASK-0085
status: blocked
owner: unassigned
agent: aider
priority: normal
branch: none
depends_on: TASK-0084
issue: none
art_request: none
touches: scenes/battle/modular_actor_adapter.gd,tools/verify_battle_adapter.gd,tools/tests/test_battle_adapter.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_adapter.py
done_when: Bind the controller to the existing ModularBattleCharacter (weaponless hero with swappable swords).
estimate_minutes: 60
---
# Adapter to ModularBattleCharacter

## Goal
Bind the controller to the existing ModularBattleCharacter (weaponless hero with swappable swords).

## Implementation
Adapter implements the actor interface using scenes/modular_battle_character.gd without modifying it.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Both swords swap through the adapter
- [ ] Original character scripts unchanged (git diff empty)

## Test
`python -m unittest discover -s tools/tests -p test_battle_adapter.py`, then `python tools/run_tests.py --changed`.

## Estimate
60 minutes.

## Blocked
- TASK-0070 Game Factory (branch codex/game-factory; task record not on main yet) is not merged into main, so scenes/modular_battle_character.gd does not exist on the base branch. Do not move to todo until this is resolved.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
