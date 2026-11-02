---
id: TASK-0037
status: in_progress
owner: codex
branch: codex/current-map-qa
agent: codex
touches: tools/goal_qa.py,tools/capture_map_previews.gd,tools/tests/test_art_delivery.py
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Capture registry-selected immutable revisions without v0010 assumptions; intermediate capture permits unfinished goals, final comparison retains owner gates; stale captures fail
started_at: 2026-10-26T19:25:53.983512+01:00
cost_usd: unknown
depends_on: TASK-0036
issue: none
art_request: none
---
# Current-version QA capture

**Source:** goal:GOAL-0001:recovery-capture
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/goal_qa.py
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Current-version QA capture

## Acceptance
- [ ] Capture registry-selected immutable revisions without v0010 assumptions; intermediate capture permits unfinished goals, final comparison retains owner gates; stale captures fail
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Capture registry-selected immutable revisions without v0010 assumptions; intermediate capture permits unfinished goals, final comparison retains owner gates; stale captures fail. Evidence: Owner-approved recovery audit: Current-version QA capture. Target: tools/goal_qa.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

- Integration note: existing art_delivery suite contains the new QA tests; test registry/index stay main-owned and unchanged in this worktree.
