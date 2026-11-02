---
id: TASK-0075
status: todo
owner: aider
agent: aider
priority: high
branch: none
depends_on: none
issue: none
art_request: none
touches: scenes/battle/battle_timeline.gd,tools/verify_battle_timeline.gd,tools/battle_godot_harness.py,tools/tests/test_battle_timeline.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_timeline.py
done_when: Deterministic attack timeline independent of frame rate, plus the shared headless-Godot harness used by every battle test.
estimate_minutes: 60
---
# Battle timeline core and Godot test harness

## Goal
Deterministic attack timeline independent of frame rate, plus the shared headless-Godot harness used by every battle test.

## Implementation
Timeline of frames with per-frame durations and named events. Hitstop is part of the stated duration. One hit event fires once on entering the hit window; pause/restart/cancel/seek; seek never fires events; restart starts a fresh cycle; slow speed. tools/battle_godot_harness.py reads godot_executable from .agents/planner/config.json, runs `--headless --path . --script res://tools/verify_*.gd` and returns (code, output); it must fail, never skip, when Godot is missing. Reference timing: docs/HERO_ATTACK_STYLE.md (1050 ms, hit at 430, hitstop 50; file lives in worktree TASK-0072 until merged).

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Events fire exactly once at 30/60/144 Hz simulated ticks
- [ ] Pause, frame step and seek never emit the hit twice or at all
- [ ] cancel restores the initial state
- [ ] Godot headless verify script passes through the python test

## Test
`python -m unittest discover -s tools/tests -p test_battle_timeline.py`, then `python tools/run_tests.py --changed`.

## Estimate
60 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
