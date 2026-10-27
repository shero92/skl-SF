---
id: TASK-0041
status: in_progress
owner: claude
branch: work/task-0041-cf8add5a
agent: claude
touches: tools/art_delivery.py,tools/tests/test_art_delivery.py,map_factory/metadata/asset_index.json
test: py -3 tools/run_tests.py --only art_delivery --only map_registry_validate
done_when: Only signed reviewed delivery bytes integrated by authorized integrator; stable IDs/provenance preserved and measured contracts recorded; no HD reinstallation
started_at: 2026-10-27T12:27:41.914575+00:00
cost_usd: unknown
depends_on: TASK-0038,TASK-0039
issue: none
art_request: none
---
# Integrate reviewed artwork and measured contracts

**Source:** goal:GOAL-0001:recovery-integrate
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** claude (owner reassigned 2026-10-27: Codex usage limit; was codex) (routing heuristic, not a performance claim)
**File:** tools/art_delivery.py
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Integrate reviewed artwork and measured contracts

## Acceptance
- [ ] Only signed reviewed delivery bytes integrated by authorized integrator; stable IDs/provenance preserved and measured contracts recorded; no HD reinstallation
- [ ] Test: py -3 tools/run_tests.py --only art_delivery --only map_registry_validate
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Only signed reviewed delivery bytes integrated by authorized integrator; stable IDs/provenance preserved and measured contracts recorded; no HD reinstallation. Evidence: Owner-approved recovery audit: Integrate reviewed artwork and measured contracts. Target: tools/art_delivery.py (line unspecified). Verify with: py -3 tools/run_tests.py --only art_delivery --only map_registry_validate. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Runner evidence
- Claimed by local runner at 2026-10-27T12:27:41.902299+00:00
