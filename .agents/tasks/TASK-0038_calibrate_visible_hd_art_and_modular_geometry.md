---
id: TASK-0038
status: done
owner: claude
branch: fix/task-0038-calibration
agent: claude
touches: docs/HERO_ROOM_CALIBRATION.md,.agents/graphics/requests/
test: py -3 tools/agent_workflow.py --check
done_when: Signed source identity and source-versus-render measurements classify reuse/repair/new/deferred views with exact native size, ground/mount/seam/collision contacts
started_at: 2026-10-27T11:37:47Z
cost_usd: unknown
depends_on: TASK-0052,TASK-0037
issue: none
art_request: ART-0022
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
- [x] Signed source identity and source-versus-render measurements classify reuse/repair/new/deferred views with exact native size, ground/mount/seam/collision contacts
- [x] Test: py -3 tools/agent_workflow.py --check
- [x] PR and observed test evidence.

## Agent prompt
Outcome: Signed source identity and source-versus-render measurements classify reuse/repair/new/deferred views with exact native size, ground/mount/seam/collision contacts. Evidence: Owner-approved recovery audit: Calibrate visible HD art and modular geometry. Target: docs/HERO_ROOM_CALIBRATION.md (line unspecified). Verify with: py -3 tools/agent_workflow.py --check. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Owner approval 2026-10-27: owner reviewed docs/HERO_ROOM_CALIBRATION.md in chat and approved it; status set to done. This approves the calibration document only, not visual approval of the room or of any art request.
- py -3 tools/agent_workflow.py --check on main after merge -> validated.
- Owner decision 2026-10-27: Claude performs this graphics/calibration task once, with image reads allowed. No art was generated or edited.
- Source identity: map_factory/references/hero_room_01_original.png sha256 42511e4e...25a7 (1448x1086) matches the reference json. Capture hero_room_01_v0011.png sha256 c8558d87...bb5 is image-free (placeholders, so it verifies anchors only).
- Changed files: docs/HERO_ROOM_CALIBRATION.md (new); new requests ART-0022..ART-0025; calibration sections appended to ART-0001/0004/0005/0006/0007/0008/0010/0011/0015/0019/0020/0021 (ART-0015 gets an added bedroom-rug output); this task file.
- Findings: 36 visible components classified reuse/repair/new/deferred with native sizes, contacts and ratios. Floor projection mismatch D1: source tile 104x62 vs 64x64, render floor 27% too deep. Collision coverage 0-22% for 7 colliders. 9 of 15 mount anchors fall outside their hosts. No wall run is butt-jointed (overlaps up to 222 px, gaps up to 131 px).
- Tests: py -3 tools/run_tests.py --changed -> 30/30 passed. py -3 tools/agent_workflow.py --sources-only -> validated (exit 0). --check reports only stale generated queues, which are regenerated on main per rule 9a; --write + --check in a temp copy -> validated.
- Not done: no textured source-vs-Godot capture (needs TASK-0037/TASK-0001); sun shafts, sea stacks, vines and the UI-occluded front band were not measured; owner decisions D1 etc. are listed in section 8 of the doc. Not visual approval.
- PR: https://github.com/shero92/skl-SF/pull/49 (merged 17a29b7)
- Next: owner reviews D1 and the calibrated requests (move ART-0022..0025 to requested or cancel the cancel candidates).
