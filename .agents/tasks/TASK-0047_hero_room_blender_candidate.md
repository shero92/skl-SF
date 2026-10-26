---
id: TASK-0047
status: review
owner: claude
branch: feat/hero-room-blender-candidate
agent: claude
touches: tools/capture_candidate_room.gd,tools/candidate_room.py,map_factory/candidates/,docs/previews/candidates/,tools/tests/test_candidate_room.py,tools/test_map.json,.agents/planner/requests/REQ-77d767bdc508.json,.agents/tasks/TASK-0047_hero_room_blender_candidate.md
test: py -3 tools/run_tests.py --only candidate_room
done_when: A candidate layout over v0011 is rendered by real Godot into base, candidate and side-by-side comparison PNGs with region metrics against the reference; no published map version or catalog change
started_at: 2026-10-26T21:59:54.270907+00:00
cost_usd: unknown
depends_on: TASK-0046
issue: none
art_request: none
---
# Hero Room Blender candidate assembly and capture

**Source:** request:REQ-77d767bdc508
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** critical
**Suggested agent:** claude (owner request)
**File:** tools/capture_candidate_room.gd
**Line:** unspecified
**Problem:** Owner request 2026-10-26: assemble the next Hero Room with the Blender wall runs and broken floor edges, capture the final Godot image and compare it with the reference. Unapproved art may not enter map_factory/parts or a published map version.

## Acceptance
- [ ] A candidate layout over v0011 is rendered by real Godot into base, candidate and side-by-side comparison PNGs with region metrics against the reference; no published map version or catalog change
- [x] Test: py -3 tools/run_tests.py --only candidate_room
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/candidate_room.py, tools/capture_candidate_room.gd(.uid), map_factory/candidates/hero_room_01_blender_v1.json, docs/previews/candidates/hero_room_01_blender_v1_{base,candidate,compare}.png + _metrics.json, tools/tests/test_candidate_room.py, tools/test_map.json.
- Capture: real Godot 4.7.2 (opengl3, windowed), v0011 base plus 27 candidate placements (8+8 ART-0004 side wall runs, 11 ART-0014 front edge tiles), 0 missing nodes, 4 s.
- Metrics (mean abs RGB diff to the reference, lower is closer): whole base 74.68 / candidate 74.71; front edge region 78.28 / 78.27; side wall region 74.14 / 74.22. The whole room is still far from the reference either way.
- Visual check by Claude of the comparison sheet: candidate v1 is WORSE than v0011. The orthographic side walls read as thin, pale, almost white vertical strips with dark gaps at the floor steps: overexposed light limestone, no ivy, far less detail than the HD style; the reference shows the side walls' inner faces. The broken front edge is almost entirely hidden behind the front wall pieces and stairs.
- Not approved and not published: no map version, catalog or map_factory/parts change.
- Next (v2 loop): fix exposure/material (warmer, darker golden limestone, lower sun), add ivy/flowers, revisit side-wall presentation with the owner, place the broken edge where the reference shows it (or drop it), then re-capture.
