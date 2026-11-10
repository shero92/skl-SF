---
id: TASK-0087
status: todo
owner: unassigned
agent: aider
priority: normal
branch: none
depends_on: TASK-0085
issue: none
art_request: none
touches: scenes/battle/golden_cyclone.gd,tools/verify_battle_golden_cyclone.gd,tools/tests/test_battle_golden_cyclone.py,tools/test_map.json
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

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Uses only approved individual frames
- [ ] Weapon anchors read from sockets, not guessed

## Test
`python -m unittest discover -s tools/tests -p test_battle_golden_cyclone.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Blocked
- Resolved 2026-11-10: owner accepted delivered TASK-0074 frames/VFX and merge; all 22 sources, measured anchors, actual Godot GIF and both-sword checks delivered in PR #120. TASK-0085 is done. Production wiring is now eligible; it is not implemented by this approval.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
