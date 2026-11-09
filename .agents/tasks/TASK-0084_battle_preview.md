---
id: TASK-0084
status: done
owner: claude
agent: aider
priority: normal
branch: claude/task-0084
depends_on: TASK-0076,TASK-0077,TASK-0078,TASK-0080
issue: none
art_request: none
touches: scenes/battle/battle_preview.gd,scenes/battle/battle_preview.tscn,tools/verify_battle_preview.gd,tools/tests/test_battle_preview.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_preview.py
done_when: Standalone preview: attack, view and weapon selectors, play/pause/restart, frame step, 0.25x speed, camera and VFX toggles.
estimate_minutes: 120
---
# Battle animation preview scene with selectors

## Goal
Standalone preview: attack, view and weapon selectors, play/pause/restart, frame step, 0.25x speed, camera and VFX toggles.

## Implementation
Uses stub actors implementing the controller actor interface so it works before Game Factory merges. Pixel-snapped nearest-neighbour presentation. Exposes a headless capture hook that saves the viewport to a path given on the command line.

Scope: new battle-only files under scenes/battle/, tools/ and game_factory/battle/. Do not modify existing scenes, characters, UI, damage code or any image. Aider must not generate or edit images.

Router registration: add ONE entry for your new test file to tools/test_map.json (id, kind python, covers, command, paths) so test_router (every test file must be routed) passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] All controls change state as documented in headless verification
- [ ] Capture hook writes a real viewport image only when given a path
- [ ] No gameplay or damage code touched

## Test
`python -m unittest discover -s tools/tests -p test_battle_preview.py`, then `python tools/run_tests.py --changed`.

## Estimate
120 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 (docs/AUTONOMOUS_24H_PLAN.md). Record the real execution tool and model when run.
Executed by Claude Code (Sonnet 5.5) on 2026-11-09 because Aider is paused (zero API balance); stacked on integrate/claude-0080-0082.
