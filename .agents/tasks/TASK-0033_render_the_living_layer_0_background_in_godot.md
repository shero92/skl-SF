---
id: TASK-0033
status: todo
owner: unassigned
branch: none
agent: codex
touches: map_factory/scripts/background_factory.gd,map_factory/scripts/room_factory.gd
test: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke
done_when: Sea cycles E010-E014 wave frames at the JSON fps, clouds scroll, foam animates, all at z 0; Godot smoke asserts animated background nodes exist
started_at: unknown
cost_usd: unknown
depends_on: TASK-0009
issue: none
art_request: none
---
# Render the living layer 0 background in Godot

**Source:** goal:GOAL-0001:g1-m4-bg-render
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** map_factory/scripts/room_factory.gd
**Line:** unspecified
**Problem:** room_factory.gd has no animated background: sea, sky and foam render static

## Acceptance
- [ ] Sea cycles E010-E014 wave frames at the JSON fps, clouds scroll, foam animates, all at z 0; Godot smoke asserts animated background nodes exist
- [ ] Test: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Sea cycles E010-E014 wave frames at the JSON fps, clouds scroll, foam animates, all at z 0; Godot smoke asserts animated background nodes exist. Evidence: room_factory.gd has no animated background: sea, sky and foam render static. Target: map_factory/scripts/room_factory.gd (line unspecified). Verify with: py -3 tools/run_tests.py --only map_layers --only godot_map_smoke. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
