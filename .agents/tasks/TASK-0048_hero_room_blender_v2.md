---
id: TASK-0048
status: review
owner: claude
branch: feat/hero-room-blender-v2
agent: claude
touches: tools/blender/,tools/blender_factory.py,tools/art_qa.py,tools/tests/test_blender_factory.py,tools/candidate_room.py,tools/tests/test_candidate_room.py,.agents/graphics/deliveries/ART-0004/,.agents/graphics/deliveries/ART-0014/,.agents/graphics/requests/ART-0004_hero_room_side_wall_views.md,.agents/graphics/requests/ART-0014_hero_room_broken_floor_edge.md,map_factory/candidates/,docs/previews/candidates/,.agents/planner/requests/REQ-3564d4efedcc.json,.agents/tasks/TASK-0048_hero_room_blender_v2.md
test: py -3 tools/run_tests.py --only blender_factory --only candidate_room
done_when: Blender side walls show their inner face (lean shear keeps the foot on the floor grid), warmer darker limestone, lower sun, ivy and flowers; ART-0004 and ART-0014 re-delivered; candidate v2 captured in Godot and compared with the reference and v1; still unapproved
started_at: 2026-10-26T22:19:22.290205+00:00
cost_usd: unknown
depends_on: TASK-0047
issue: none
art_request: none
---
# Hero Room Blender candidate v2

**Source:** request:REQ-3564d4efedcc
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** critical
**Suggested agent:** claude (owner request)
**File:** tools/blender/builders.py
**Line:** unspecified
**Problem:** Owner request 2026-10-26 after candidate v1 (worse than v0011: pale thin side walls): render east/west side walls showing their inner masonry face like the reference, with warmer darker limestone, a lower sun and ivy; re-capture and compare.

## Acceptance
- [ ] Blender side walls show their inner face (lean shear keeps the foot on the floor grid), warmer darker limestone, lower sun, ivy and flowers; ART-0004 and ART-0014 re-delivered; candidate v2 captured in Godot and compared with the reference and v1; still unapproved
- [x] Test: py -3 tools/run_tests.py --only blender_factory --only candidate_room
- [ ] PR and observed test evidence.

## Evidence / handoff
- Toolkit: lib.lean/lean_matrix (x += k*z, foot fixed on the floor grid), lib.ivy (leaf + flower meshes), warmer darker limestone defaults, sun 4.5 -> 2.8 and warmer, ambient 0.35 -> 0.22; wall_run params ivy*/lean.
- Re-delivered ART-0004 (west lean -0.45, east +0.45, ivy) and ART-0014; QA: no problems; east~west no longer similar; open warnings north~south and edge_01~edge_02.
- Candidate v2 (same placements as v1) captured in real Godot. Mean abs RGB diff to the reference: whole base 74.68 / v1 74.71 / v2 73.59; front edge 78.28 / 78.27 / 77.75; side walls 75.05 / 74.22 / 73.45 (v2 region box is wider).
- Visual check by Claude (docs/previews/candidates/hero_room_01_blender_v1_v2_compare.png): v2 is better than v1 (side walls now read as walls with an inner face) but not approvable: the 0.45 lean makes them look like slabs falling outward, stacked runs zigzag at the floor steps, shaded inner faces look grey-beige not golden, ivy/flowers are too small to read at 64 px/tile, walls are taller and plainer than the reference's low ruined walls, and the front broken edge is still hidden.
- Tests: test_blender_factory.py 12/12 (new lean test), test_candidate_room.py 4/4.
- Not approved and not published: no map version, catalog or map_factory/parts change.
- Next (v3): lean ~0.2, lower ruined walls with broken crenellated tops, one continuous mesh per side following the steps, warm fill light on shaded faces, larger and denser ivy and flowers, and a decision on the front edge.
