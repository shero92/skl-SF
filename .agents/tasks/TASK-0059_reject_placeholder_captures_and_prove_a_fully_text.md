---
id: TASK-0059
status: todo
owner: unassigned
branch: none
agent: codex
touches: tools/goal_qa.py,tools/capture_map_previews.gd,tools/tests/test_art_delivery.py
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Keep coding checkout image-free. Give only isolated deterministic renderer its required committed environment textures, including inherited sparse settings; verify actual loads for every rendered texture and fail before publishing if fallback/draft or resource missing. Receipt records texture inventory hashes and missing/fallback count, map commit/version/camera. Unit-test missing resources and real-render integration; capture v0011 or latest without viewing restricted art. Preserve historical files and final owner gate.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0037
issue: none
art_request: none
---
# Reject placeholder captures and prove a fully textured isolated Godot render

**Source:** goal:GOAL-0001:recovery-textured-capture
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** bug
**Priority:** critical
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/goal_qa.py
**Line:** unspecified
**Problem:** HERO_ROOM_CALIBRATION section 1 identifies capture c8558d87 as labelled draft placeholders; goal_qa creates a renderer worktree without explicitly clearing inherited sparse checkout. Existing receipt authenticates PNG bytes but not successful texture loads.

## Acceptance
- [ ] Keep coding checkout image-free. Give only isolated deterministic renderer its required committed environment textures, including inherited sparse settings; verify actual loads for every rendered texture and fail before publishing if fallback/draft or resource missing. Receipt records texture inventory hashes and missing/fallback count, map commit/version/camera. Unit-test missing resources and real-render integration; capture v0011 or latest without viewing restricted art. Preserve historical files and final owner gate.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Keep coding checkout image-free. Give only isolated deterministic renderer its required committed environment textures, including inherited sparse settings; verify actual loads for every rendered texture and fail before publishing if fallback/draft or resource missing. Receipt records texture inventory hashes and missing/fallback count, map commit/version/camera. Unit-test missing resources and real-render integration; capture v0011 or latest without viewing restricted art. Preserve historical files and final owner gate.. Evidence: HERO_ROOM_CALIBRATION section 1 identifies capture c8558d87 as labelled draft placeholders; goal_qa creates a renderer worktree without explicitly clearing inherited sparse checkout. Existing receipt authenticates PNG bytes but not successful texture loads.. Target: tools/goal_qa.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
