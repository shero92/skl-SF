---
id: TASK-0081
status: done
owner: aider
agent: aider
priority: normal
branch: aider/task-0081
depends_on: TASK-0076,TASK-0077
issue: none
art_request: none
touches: scenes/battle/combo_sequence.gd,tools/verify_battle_combo.gd,tools/tests/test_battle_combo.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_combo.py
done_when: Chain several attacks with defined windows, then a recovery to Idle.
estimate_minutes: 60
---
# Combo attack sequence and recovery

## Goal
Chain several attacks with defined windows, then a recovery to Idle.

## Implementation
Combo definition = ordered attack ids with gap limits. Unavailable special attacks (for example skybreaker_combo until the normal attack is approved) report UNAVAILABLE and are skipped by default. Interrupt and cancel supported.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Chain order and timing verified
- [ ] Unavailable attack is reported, not played
- [ ] Cancel mid-chain restores Idle

## Test
`python -m unittest discover -s tools/tests -p test_battle_combo.py`, then `python tools/run_tests.py --changed`.

## Estimate
60 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
