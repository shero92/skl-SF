---
id: TASK-0008
status: blocked
owner: claude
branch: work/task-0008-4149caeb
agent: claude
touches: map_factory/maps/hero_room_01/reference_gaps.json
test: py -3 -m unittest tools.tests.test_map_reference
done_when: map_factory/maps/hero_room_01/reference_gaps.json maps every spec item to an existing asset ID or a gap entry with level (0-4), proposed native size and 4-direction needs; no unrelated substitutes; uncertain matches listed as gaps; no PNGs opened
started_at: 2026-10-26T10:05:16.630587+00:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Map GOAL-0001 written spec to existing asset IDs and missing-art gaps

**Source:** ai:a57e0bb18ae11b5f
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** investigation
**Priority:** critical
**Suggested agent:** claude (routing heuristic, not a performance claim)
**File:** map_factory/metadata/asset_index.json
**Line:** unspecified
**Problem:** No table links each item of the GOAL-0001 goal.md written spec to an existing asset ID or a missing-art gap per level 0-4 (goal step g1-m1-gap-audit). Later art requests (g1-m8) depend on it.

## Acceptance
- [ ] map_factory/maps/hero_room_01/reference_gaps.json maps every spec item to an existing asset ID or a gap entry with level (0-4), proposed native size and 4-direction needs; no unrelated substitutes; uncertain matches listed as gaps; no PNGs opened
- [ ] Test: py -3 -m unittest tools.tests.test_map_reference
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: map_factory/maps/hero_room_01/reference_gaps.json maps every spec item to an existing asset ID or a gap entry with level (0-4), proposed native size and 4-direction needs; no unrelated substitutes; uncertain matches listed as gaps; no PNGs opened. Evidence: No table links each item of the GOAL-0001 goal.md written spec to an existing asset ID or a missing-art gap per level 0-4 (goal step g1-m1-gap-audit). Later art requests (g1-m8) depend on it.. Target: map_factory/metadata/asset_index.json (line unspecified). Verify with: py -3 -m unittest tools.tests.test_map_reference. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 30000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Allowed touches
- map_factory/maps/hero_room_01/reference_gaps.json

## Runner evidence
- Claimed by local runner at 2026-10-26T10:05:16.620715+00:00

## Runner evidence
- Runner failed; inspect local runner-state.json
