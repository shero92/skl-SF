---
id: TASK-0078
status: todo
owner: aider
agent: aider
priority: high
branch: none
depends_on: TASK-0075
issue: none
art_request: none
touches: scenes/battle/dynamic_battle_camera.gd,tools/verify_battle_camera.gd,tools/tests/test_battle_camera.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_camera.py
done_when: Smooth camera transitions, zoom/follow, shake, hitstop-aware focus and clean restore.
estimate_minutes: 90
---
# Dynamic Camera2D controller

## Goal
Smooth camera transitions, zoom/follow, shake, hitstop-aware focus and clean restore.

## Implementation
Camera2D subclass: focus_on(target, zoom, duration), follow, shake(amplitude_px, duration) limited to 2-3 px at reference resolution, transitions between named presets (hero_rear_3q, hero_front, monster_rear), restore() returns the exact original transform. Motion limited to about 10 percent of the frame. Uses delta time only.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] restore() returns the exact initial offset/zoom after any sequence
- [ ] shake never exceeds the configured amplitude and ends at zero
- [ ] Transitions are monotonic with no overshoot beyond the configured easing
- [ ] Verified headless

## Test
`python -m unittest discover -s tools/tests -p test_battle_camera.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
