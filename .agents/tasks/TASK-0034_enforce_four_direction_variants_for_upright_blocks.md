---
id: TASK-0034
status: in_progress
owner: claude
branch: work/task-0034-d4862094
agent: claude
touches: tools/map_factory_cli.py,tools/tests/test_map_cardinal.py
test: py -3 -m unittest discover -s tools/tests -p test_map_cardinal.py
done_when: CLI rejects rotate mode for upright categories and requires n/e/s/w variant IDs; flat floors and rugs keep rotate mode
started_at: 2026-10-26T13:16:28.905324+00:00
cost_usd: unknown
depends_on: TASK-0009
issue: none
art_request: none
---
# Enforce four-direction variants for upright blocks

**Source:** goal:GOAL-0001:g1-m3-four-direction-enforce
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** normal
**Suggested agent:** claude (owner reassigned from codex on 2026-10-26 to run in parallel with TASK-0033; routing heuristic, not a performance claim)
**File:** tools/map_factory_cli.py
**Line:** unspecified
**Problem:** Upright walls and furniture may be rotated instead of using north/east/south/west artwork variants

## Acceptance
- [ ] CLI rejects rotate mode for upright categories and requires n/e/s/w variant IDs; flat floors and rugs keep rotate mode
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_map_cardinal.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: CLI rejects rotate mode for upright categories and requires n/e/s/w variant IDs; flat floors and rugs keep rotate mode. Evidence: Upright walls and furniture may be rotated instead of using north/east/south/west artwork variants. Target: tools/map_factory_cli.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_map_cardinal.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Runner evidence
- Claimed by local runner at 2026-10-26T13:16:28.895762+00:00
