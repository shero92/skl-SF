---
id: TASK-0086
status: blocked
owner: unassigned
agent: aider
priority: high
branch: none
depends_on: TASK-0085
issue: none
art_request: none
touches: scenes/battle/phantom_dash.gd,tools/verify_battle_phantom_dash.gd,tools/tests/test_battle_phantom_dash.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_phantom_dash.py
done_when: Phantom Dash attack (1050 ms, hit at 430, hitstop 50) driven by approved rear frames.
estimate_minutes: 90
---
# Phantom Dash controller

## Goal
Phantom Dash attack (1050 ms, hit at 430, hitstop 50) driven by approved rear frames.

## Implementation
Data file listing frames, durations, sockets and VFX; controller wiring only. Refuses to report ready while required frames are needs_review or missing.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Timing matches HERO_ATTACK_STYLE exactly
- [ ] MISSING_REAR_ART shown when art is absent

## Test
`python -m unittest discover -s tools/tests -p test_battle_phantom_dash.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Blocked
- Needs approved hero rear frames (ART-0026 / TASK-0072, needs_review) and TASK-0085. Do not move to todo until this is resolved.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
