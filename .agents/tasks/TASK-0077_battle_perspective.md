---
id: TASK-0077
status: todo
owner: aider
agent: aider
priority: high
branch: none
depends_on: TASK-0075
issue: none
art_request: none
touches: scenes/battle/battle_perspective.gd,tools/verify_battle_perspective.gd,tools/tests/test_battle_perspective.py
test: python -m unittest discover -s tools/tests -p test_battle_perspective.py
done_when: Pick the correct view per attacker: hero attacking = HERO_REAR_3Q, monster attacking = HERO_FRONT, with MONSTER_REAR available.
estimate_minutes: 45
---
# Perspective resolver for hero and monster views

## Goal
Pick the correct view per attacker: hero attacking = HERO_REAR_3Q, monster attacking = HERO_FRONT, with MONSTER_REAR available.

## Implementation
Data-driven table mapping (attacker_kind, phase) to view id and required asset keys. Missing rear/front assets yield warning MISSING_REAR_ART / MISSING_FRONT_ART; never fabricate a rear view by flipping a side frame.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

## Acceptance criteria
- [ ] Resolver returns the documented view for every (attacker, phase)
- [ ] Missing art reports a warning and no fake substitute
- [ ] No 3D rotation of 2D sprites anywhere

## Test
`python -m unittest discover -s tools/tests -p test_battle_perspective.py`, then `python tools/run_tests.py --changed`.

## Estimate
45 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
