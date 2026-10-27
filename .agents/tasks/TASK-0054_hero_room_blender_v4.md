---
id: TASK-0054
status: review
owner: claude
branch: feat/hero-room-blender-v4
agent: claude
touches: tools/blender/,tools/blender_factory.py,tools/tests/test_blender_factory.py,tools/candidate_room.py,tools/capture_candidate_room.gd,tools/tests/test_candidate_room.py,map_factory/candidates/,docs/previews/candidates/,.agents/graphics/deliveries/ART-0022/,.agents/graphics/deliveries/ART-0024/,.agents/graphics/deliveries/ART-0025/,.agents/graphics/requests/ART-0022_hero_room_compass_floor_inlay.md,.agents/graphics/requests/ART-0023_hero_room_side_wall_fixture_views.md,.agents/graphics/requests/ART-0024_hero_room_rope_post_fence.md,.agents/graphics/requests/ART-0025_hero_room_entrance_stairs.md,.agents/planner/requests/REQ-2e14a92e1acb.json,.agents/tasks/TASK-0054_hero_room_blender_v4.md
test: py -3 tools/run_tests.py --only blender_factory --only candidate_room
done_when: golden limestone side walls; ART-0025 stairs, ART-0022 compass inlay and ART-0024 rope-post fence delivered by tools/blender_factory.py deliver with clean scripted QA; tools/blender/README.md is a full build guide; candidate hero_room_01_blender_v4 captured and compared with base/v1/v2/v3; stays unapproved
started_at: 2026-10-27T13:00:00+00:00
cost_usd: unknown
depends_on: TASK-0050
issue: none
art_request: none
---
# Hero Room Blender candidate v4

**Source:** request:REQ-2e14a92e1acb
**Created:** 2026-10-27
**Goal:** GOAL-0001
**Type:** feature
**Priority:** critical
**Art requests:** ART-0022, ART-0024, ART-0025 (delivered, rendered_unreviewed)
**Suggested agent:** claude (owner request)
**File:** tools/blender/builders.py
**Line:** unspecified
**Problem:** Owner decision 2026-10-27 (AGENTS.md rules 4 and 11): v3 side-wall stone reads pale grey and the east wall shadow falls on the sea; entrance stairs (ART-0025), compass floor inlay (ART-0022) and rope-post fence (ART-0024) are missing. Build them with scripted Blender, write a full build guide for Codex, assemble candidate v4 and compare with base/v1-v3. Keep the 64x64 floor grid (D1 open). Owner moved ART-0022..ART-0025 from blocked_reference to requested.

## Acceptance
- [x] Golden limestone side walls; shadows on the floor, not the sea (scripted: mean saturation 0.27 -> 0.41, hue 35; shadow catcher limited to the floor side)
- [x] ART-0025, ART-0022, ART-0024 delivered by `tools/blender_factory.py deliver` with clean scripted QA (0 problems, 0 open warnings)
- [x] `tools/blender/README.md` full build guide
- [x] Candidate v4 captured and compared with base/v1/v2/v3 by metrics (unapproved). The compare sheet was not viewed: `.claude/settings.json` denies `Read(./docs/previews/**)` (owner-controlled)
- [x] Test: py -3 tools/run_tests.py --only blender_factory --only candidate_room
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/blender/{builders.py (entrance_stairs, compass_inlay, rope_fence, floor_side_region, side_wall_path palette + shadow_inside), lib.py (wood, rope, gold, sapphire, soft specular, GOLDEN_*, polygon shadow catcher), render_part.py, README.md (full build guide), specs/ART-0022/0024/0025.json, specs/candidates/hero_room_01_v4_side_walls.json}, tools/blender_factory.py (palette stats + palette_check), tools/candidate_room.py (offset_px, props layer, refloor_cells, per-piece metrics), tools/capture_candidate_room.gd (refloor, props layer), tests, .agents/graphics/deliveries/ART-0022|0024|0025/, map_factory/candidates/hero_room_01_blender_v4.json + renders/hero_room_01_blender_v4/, docs/previews/candidates/hero_room_01_blender_v4_*, ART-0022..0025 requests -> requested (owner).
- Measured pieces (opaque px vs calibration): inlay 268x260 (267x259), post 26x77 (29x78), west run 94x174 / east run 88x143 (92x126 / 87x121 under uniform depth; taller here because the 64 px grid keeps the deeper floor, D1 open), stairs 3 steps, 105 px below the floor edge.
- Capture (mean abs RGB diff to the reference, lower is closer): whole base 74.72 -> v4 73.89 (v1 74.71, v2 73.59, v3 74.23; v1-v3 base 74.68). Per piece base -> v4: stairs 80.58 -> 64.25, west wall 77.77 -> 73.92, east wall 79.22 -> 78.17, fences 75.04 -> 73.36 / 74.10 -> 73.05, broken edges -1 to -3, compass inlay 54.39 -> 55.75 (worse; 2 tuning rounds: lighter field +1.44 -> +1.36, calibrated centre +1.86 reverted to the joint).
- Honest assessment: numerically v4 is the second-closest candidate (after v2) and the stairs are a clear gain; the inlay does not yet beat the procedural tiles by this metric (characters stand on it in the reference, so the region is noisy). No visual judgement was possible; not approved (candidate_unapproved). East fence sits partly behind the oversized P023 chest (ART-0021 pending).
- Tests: py -3 tools/run_tests.py --only blender_factory --only candidate_room 2/2 (Blender render tests included); py -3 tools/run_tests.py --changed 30/30; source checks agent_costs report / agent_workflow / generate_project_indexes (--sources-only --base origin/main) and run_tests --check-index --sources-only all rc=0.
- PR: https://github.com/shero92/skl-SF/pull/52
- Next: owner views docs/previews/candidates/hero_room_01_blender_v4_compare.png (or allows Claude to read *_compare.png only) and decides on D1; then tune the inlay from that review.
