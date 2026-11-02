---
id: TASK-0079
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: none
issue: none
art_request: none
touches: game_factory/battle/weapon_sockets.schema.json,tools/weapon_sockets.py,tools/tests/test_weapon_sockets.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_weapon_sockets.py
done_when: Per-frame weapon socket data so swords stay separate from the body sprite and never land in the wrong hand or layer.
estimate_minutes: 60
---
# Weapon socket schema and validator

## Goal
Per-frame weapon socket data so swords stay separate from the body sprite and never land in the wrong hand or layer.

## Implementation
JSON schema: attack_id, frame_name, socket {x, y, rotation_deg}, layer (behind_hand|in_hand|front), supported weapon ids (WPN_HERO_BASIC_SWORD, WPN_IRON_SWORD). tools/weapon_sockets.py validates files: every frame has a socket, no NaN, rotation in range, valid layer, no duplicate frames, and rejects data not sourced from annotation or measurement. CLI prints a report and sets the exit code.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Valid fixture passes; missing/duplicate/out-of-range fixtures fail with named reasons
- [ ] Never writes or edits images
- [ ] Python tests pass

## Test
`python -m unittest discover -s tools/tests -p test_weapon_sockets.py`, then `python tools/run_tests.py --changed`.

## Estimate
60 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
