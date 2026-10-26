---
id: TASK-0049
status: todo
owner: unassigned
branch: none
agent: codex
touches: tools/local_planner.py
test: py -3 -m unittest discover -s tools/tests -p test_local_planner.py
done_when: PR checks validate records without writing generated files; main checks remain strict; successful planner merges regenerate only on main under lock.
started_at: unknown
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Reconcile planning PR checks with main-only generated outputs

**Source:** ai:c80dc20028884d85
**Created:** 2026-10-27
**Goal:** manual request
**Type:** bug
**Priority:** critical
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/local_planner.py
**Line:** unspecified
**Problem:** Open request REQ-7175675bbea0: PR 17 is blocked because generated task boards and file indexes are stale by design on task branches (ADR-006 main-only generation), but PR checks still demand them.

## Acceptance
- [ ] PR checks validate records without writing generated files; main checks remain strict; successful planner merges regenerate only on main under lock.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_local_planner.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: PR checks validate records without writing generated files; main checks remain strict; successful planner merges regenerate only on main under lock.. Evidence: Open request REQ-7175675bbea0: PR 17 is blocked because generated task boards and file indexes are stale by design on task branches (ADR-006 main-only generation), but PR checks still demand them.. Target: tools/local_planner.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_local_planner.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Allowed touches
- tools/local_planner.py
