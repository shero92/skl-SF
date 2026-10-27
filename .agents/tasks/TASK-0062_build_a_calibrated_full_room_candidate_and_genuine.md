---
id: TASK-0062
status: blocked
owner: unassigned
branch: none
agent: codex
touches: tools/candidate_room.py,tools/capture_candidate_room.gd,tools/tests/test_candidate_room.py,map_factory/candidates/
test: py -3 -m unittest discover -s tools/tests -p test_candidate_room.py
done_when: Add tested candidate-only overrides for existing instance position/scale/visibility/mount adjustments, with unchanged registered snapshots/catalog. Reuse accepted HD bed/cover/desk/chest. Compose sleeping left, study right, centered open arch and compass, front stairs, continuous shell. Build 8/10-row unapproved candidate specs under same camera and textures; retain primary authenticated 1448 reference and use existing 1536 goal image as supplementary owner-supplied environment reference. Require real loaded textures, output local full-room comparison plus JSON hashes/camera/version and separate environment-only regions excluding characters/UI. No final signoff or projection change.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0059
issue: none
art_request: none
---
# Build a calibrated full-room candidate and genuine eight-versus-ten-row comparison

**Source:** goal:GOAL-0001:recovery-depth-comparison
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** high
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** tools/candidate_room.py
**Line:** unspecified
**Problem:** Current v4 overlays shell pieces but keeps oversized/misplaced base furniture; comparison pipeline hardcodes the former reference. Owner wants both supplied room images and chose visual depth comparison, not automatic row adoption.
**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## Acceptance
- [ ] Add tested candidate-only overrides for existing instance position/scale/visibility/mount adjustments, with unchanged registered snapshots/catalog. Reuse accepted HD bed/cover/desk/chest. Compose sleeping left, study right, centered open arch and compass, front stairs, continuous shell. Build 8/10-row unapproved candidate specs under same camera and textures; retain primary authenticated 1448 reference and use existing 1536 goal image as supplementary owner-supplied environment reference. Require real loaded textures, output local full-room comparison plus JSON hashes/camera/version and separate environment-only regions excluding characters/UI. No final signoff or projection change.
- [ ] Test: py -3 -m unittest discover -s tools/tests -p test_candidate_room.py
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Add tested candidate-only overrides for existing instance position/scale/visibility/mount adjustments, with unchanged registered snapshots/catalog. Reuse accepted HD bed/cover/desk/chest. Compose sleeping left, study right, centered open arch and compass, front stairs, continuous shell. Build 8/10-row unapproved candidate specs under same camera and textures; retain primary authenticated 1448 reference and use existing 1536 goal image as supplementary owner-supplied environment reference. Require real loaded textures, output local full-room comparison plus JSON hashes/camera/version and separate environment-only regions excluding characters/UI. No final signoff or projection change.. Evidence: Current v4 overlays shell pieces but keeps oversized/misplaced base furniture; comparison pipeline hardcodes the former reference. Owner wants both supplied room images and chose visual depth comparison, not automatic row adoption.. Target: tools/candidate_room.py (line unspecified). Verify with: py -3 -m unittest discover -s tools/tests -p test_candidate_room.py. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.
