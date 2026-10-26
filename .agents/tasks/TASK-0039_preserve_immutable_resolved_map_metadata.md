---
id: TASK-0039
status: blocked
owner: unassigned
branch: none
agent: codex
touches: tools/map_factory_cli.py,tools/map_factory_layers.py,tools/tests/test_map_factory.py,tools/tests/test_map_layers.py
test: py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate
done_when: Catalog measurement corrections do not rewrite or invalidate historical resolved graphs; new revisions use corrected measurements; corruption remains rejected
started_at: unknown
cost_usd: unknown
depends_on: TASK-0036
issue: none
art_request: none
---
# Preserve immutable resolved map metadata

**Source:** goal:GOAL-0001:recovery-immutable
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/map_factory_cli.py
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Preserve immutable resolved map metadata
**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## Acceptance
- [ ] Catalog measurement corrections do not rewrite or invalidate historical resolved graphs; new revisions use corrected measurements; corruption remains rejected
- [ ] Test: py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Catalog measurement corrections do not rewrite or invalidate historical resolved graphs; new revisions use corrected measurements; corruption remains rejected. Evidence: Owner-approved recovery audit: Preserve immutable resolved map metadata. Target: tools/map_factory_cli.py (line unspecified). Verify with: py -3 tools/run_tests.py --only map_factory --only map_layers --only map_registry_validate. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
