---
id: TASK-0036
status: done
owner: codex
branch: codex/hero-recovery-baseline
agent: codex
touches: docs/HERO_ROOM_RECOVERY_AUDIT.md,docs/ASSET_AUDIT.md,docs/MAP_FACTORY_REFERENCE_DIAGNOSIS.md,.agents/tasks/,.agents/planner/goals.json,.agents/planner/requests/REQ-1a8c02ac60e2.json,.agents/graphics/requests/,map_factory/maps/hero_room_01/reference_gaps.json
test: py -3 tools/run_tests.py --only agent_workflow --only goal_task_factory
done_when: Verified recovery audit and draft milestone revision published; canonical records reconciled without visual approval or execution policy changes
started_at: 2026-10-26T19:20:48.830182+01:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Reconcile Hero Room recovery baseline and roadmap

**Source:** request:REQ-1a8c02ac60e2
**Goal:** GOAL-0001
**Type:** investigation
**Priority:** critical

Owner explicitly authorized the recovery plan in this session. This is a supervised documentation/planning task; the automated coding runner's scope excludes docs and planning records. Do not widen its allowlist or execute this task through that runner.

## Acceptance
- [ ] Current catalog/map/PR evidence documented, stale records reconciled.
- [ ] Revised milestones remain a draft review package; no fictional source identity, measurements, production art or approval.
- [ ] Existing ART requests receive reuse-first and visible-first instructions.
- [ ] Workflow/planner tests and PR evidence recorded.

## Evidence / handoff
- Cost tracking started before edits; actual execution agent codex.
- Next: publish audit and draft recovery specification.

## Observed implementation evidence
- Added recovery audit and draft steps TASK-0037..0045, not executable task records.
- Reconciled TASK-0033 merged PR #31, TASK-0007 historical config evidence, source/HD reuse priorities and all 21 existing ART records.
- Existing later milestone tasks remain source-gated. No execution configuration, assets, snapshots or generated boards changed.
- Next: PR checks, then current-version capture implementation.

- Validation: `py -3 tools/run_tests.py --changed --kind python`: 21/21 suites passed, including registry/workflow/planner checks.

## Confirmed merged baseline
- PR #32 merge 3b787b14945e1c7f087d4f79a6d893db6ddf039b is an ancestor of current main. Current runner/planner/workflow checks pass; this record correction unblocks TASK-0039. No visual approval implied.
