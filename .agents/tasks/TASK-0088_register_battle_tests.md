---
id: TASK-0088
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0071,TASK-0075,TASK-0076,TASK-0077,TASK-0078,TASK-0080
issue: none
art_request: none
touches: tools/test_map.json,tools/tests/test_battle_registry.py
test: python -m unittest discover -s tools/tests -p test_battle_registry.py
done_when: Make the test router run the battle suites when their files change.
estimate_minutes: 45
---
# Register battle tests in tools/test_map.json

## Goal
Make the test router run the battle suites when their files change.

## Implementation
Add one entry per battle test (paths = scene script + verify script + python test). The test checks every tools/tests/test_battle_*.py is registered and ids are unique. Edit the JSON textually, keeping existing formatting.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

## Acceptance criteria
- [ ] Every battle test registered once
- [ ] tools/run_tests.py --changed selects them for battle paths
- [ ] Existing entries byte-identical

## Test
`python -m unittest discover -s tools/tests -p test_battle_registry.py`, then `python tools/run_tests.py --changed`.

## Estimate
45 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
