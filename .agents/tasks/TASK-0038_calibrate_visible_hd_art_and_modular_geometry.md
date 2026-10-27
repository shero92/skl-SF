---
id: TASK-0038
status: blocked
owner: unassigned
branch: none
agent: graphics
touches: docs/HERO_ROOM_CALIBRATION.md,.agents/graphics/requests/
test: py -3 tools/agent_workflow.py --check
done_when: Signed source identity and source-versus-render measurements classify reuse/repair/new/deferred views with exact native size, ground/mount/seam/collision contacts
started_at: unknown
cost_usd: unknown
depends_on: TASK-0052,TASK-0037
issue: none
art_request: none
---
# Calibrate visible HD art and modular geometry

**Source:** goal:GOAL-0001:recovery-calibration
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** investigation
**Priority:** high
**Suggested agent:** specialist (routing heuristic, not a performance claim)
**File:** docs/HERO_ROOM_CALIBRATION.md
**Line:** unspecified
**Problem:** Owner-approved recovery audit: Calibrate visible HD art and modular geometry
**Blocked by:** specialist step — requires: a calibration/graphics specialist performs it (coding runners never claim it); new graphics need an art request in .agents/graphics/requests/, independent visual review and owner approval; TASK-0052 proves source identity; TASK-0001 retains whole-room comparison acceptance and must not create a calibration cycle.

## Acceptance
- [ ] Signed source identity and source-versus-render measurements classify reuse/repair/new/deferred views with exact native size, ground/mount/seam/collision contacts
- [ ] Test: py -3 tools/agent_workflow.py --check
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Signed source identity and source-versus-render measurements classify reuse/repair/new/deferred views with exact native size, ground/mount/seam/collision contacts. Evidence: Owner-approved recovery audit: Calibrate visible HD art and modular geometry. Target: docs/HERO_ROOM_CALIBRATION.md (line unspecified). Verify with: py -3 tools/agent_workflow.py --check. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
