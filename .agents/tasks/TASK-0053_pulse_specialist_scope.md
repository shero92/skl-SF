---
id: TASK-0053
status: review
owner: claude
branch: fix/pulse-specialist-scope
agent: claude
touches: tools/runner_safety.py,tools/goal_task_factory.py,tools/tests/test_goal_task_factory.py,.agents/planner/requests/REQ-75b821835f83.json,.agents/tasks/TASK-0053_pulse_specialist_scope.md
test: py -3 tools/run_tests.py --only goal_task_factory
done_when: Pulse accepts exactly docs/HERO_ROOM_CALIBRATION.md (not docs/), records specialist steps blocked with their real requirements, and a refused step no longer stops updates to independent tasks; regression test reproduces the original failure
started_at: 2026-10-27
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Pulse: allow approved calibration doc and record specialist blockers

**Source:** request:REQ-75b821835f83
**Created:** 2026-10-27
**Goal:** manual request
**Type:** bug
**Priority:** critical
**Suggested agent:** claude (owner request)
**File:** tools/goal_task_factory.py
**Line:** unspecified
**Problem:** manual_agents session interrupted: goal_task_factory.py pulse exits 1 with 'Outside Map Factory coding scope: docs/HERO_ROOM_CALIBRATION.md' because create() applies coding touches rules to the specialist recovery-calibration step, and one failing step aborts the whole pulse

## Acceptance
- [x] Pulse accepts exactly docs/HERO_ROOM_CALIBRATION.md (not docs/), records specialist steps blocked with their real requirements, and a refused step no longer stops updates to independent tasks; regression test reproduces the original failure
- [x] Test: py -3 tools/run_tests.py --only goal_task_factory
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/runner_safety.py (APPROVED_DOCS: exact docs/HERO_ROOM_CALIBRATION.md only), tools/goal_task_factory.py (specialist blocker line, refused steps reported without aborting the pulse), tools/tests/test_goal_task_factory.py (regression tests).
- Reproduced: pulse on a copy of the main records exited 1 with "Outside Map Factory coding scope: docs/HERO_ROOM_CALIBRATION.md"; the new tests fail without the fix (2 failures, 1 error) and pass with it.
- Tests: test_goal_task_factory 13/13; py -3 tools/run_tests.py --changed 6/6 (agent_workflow, goal_task_factory, goal_pulse_continuous, local_planner, parallel_safety, lf_writers); test_manual_agents OK.
- Dry run on a copy of the main records: exit 0, creates TASK-0038 (recovery-calibration) as blocked graphics/specialist with its requirements; no real pulse was run.
- Not done: the calibration itself (TASK-0038 stays blocked); no review task changed to done.
- PR: https://github.com/shero92/skl-SF/pull/48
