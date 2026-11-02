---
id: TASK-0087
status: blocked
owner: unassigned
agent: aider
priority: normal
branch: none
depends_on: TASK-0085
issue: none
art_request: none
touches: scenes/battle/golden_cyclone.gd,tools/verify_battle_golden_cyclone.gd,tools/tests/test_battle_golden_cyclone.py
test: python -m unittest discover -s tools/tests -p test_battle_golden_cyclone.py
done_when: Golden Cyclone attack wiring from the 22 individual body frames and separate effects.
estimate_minutes: 90
---
# Golden Cyclone controller

## Goal
Golden Cyclone attack wiring from the 22 individual body frames and separate effects.

## Implementation
Controller and data only; frames come from game_factory/golden_cyclone as individual PNGs after owner approval.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

## Acceptance criteria
- [ ] Uses only approved individual frames
- [ ] Weapon anchors read from sockets, not guessed

## Test
`python -m unittest discover -s tools/tests -p test_battle_golden_cyclone.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Blocked
- TASK-0074 frames are candidates (001-013, 014 started), not approved; weapon anchors and final GIF unconfirmed. Do not move to todo until this is resolved.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
