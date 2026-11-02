---
id: TASK-0082
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0076,TASK-0077
issue: none
art_request: none
touches: scenes/battle/battle_reactions.gd,tools/verify_battle_reactions.gd,tools/tests/test_battle_reactions.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_reactions.py
done_when: Defender reactions (hit, block) driven by the hit signal, with the correct view when the hero is attacked.
estimate_minutes: 60
---
# Monster response and hero hit/block states

## Goal
Defender reactions (hit, block) driven by the hit signal, with the correct view when the hero is attacked.

## Implementation
Reaction table keyed by attack outcome; missing reaction art reports MISSING_REACTION_ART. No new art is created.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Hero attacked uses the front view id
- [ ] Missing art is reported, not faked
- [ ] Reactions never outlive cancel/reset

## Test
`python -m unittest discover -s tools/tests -p test_battle_reactions.py`, then `python tools/run_tests.py --changed`.

## Estimate
60 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
