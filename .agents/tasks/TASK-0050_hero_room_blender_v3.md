---
id: TASK-0050
status: review
owner: claude
branch: feat/hero-room-blender-v3
agent: claude
touches: tools/blender/,tools/blender_factory.py,tools/tests/test_blender_factory.py,tools/candidate_room.py,tools/tests/test_candidate_room.py,map_factory/candidates/,docs/previews/candidates/,.agents/planner/requests/REQ-f98680267cfb.json,.agents/tasks/TASK-0050_hero_room_blender_v3.md
test: py -3 tools/run_tests.py --only blender_factory --only candidate_room
done_when: side_wall_path builder renders one continuous lower ruined wall per side along the floor steps (lean 0.2, crenellations, warm fill light, larger ivy); staged as unapproved candidate art; candidate v3 captured in Godot and compared with the reference, v1 and v2
started_at: 2026-10-26T22:34:43.702054+00:00
cost_usd: unknown
depends_on: TASK-0048
issue: none
art_request: none
---
# Hero Room Blender candidate v3

**Source:** request:REQ-f98680267cfb
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** critical
**Suggested agent:** claude (owner request)
**File:** tools/blender/builders.py
**Line:** unspecified
**Problem:** Owner request 2026-10-26 after candidate v2 (walls lean too far, zigzag at floor steps, grey shaded faces, ivy unreadable): lean about 0.2, lower ruined walls with broken crenellated tops, one continuous mesh per side following the floor steps, warm fill light on shaded faces, larger denser ivy; re-capture and compare.

## Acceptance
- [x] side_wall_path builder renders one continuous lower ruined wall per side along the floor steps (lean 0.2, crenellations, warm fill light, larger ivy); staged as unapproved candidate art; candidate v3 captured in Godot and compared with the reference, v1 and v2
- [x] Test: py -3 tools/run_tests.py --only blender_factory --only candidate_room
- [ ] PR and observed test evidence.

## Evidence / handoff
- Changed files: tools/blender/{builders.py (side_wall_path, path_segments), lib.py (fill light, join, ivy leaf_scale, centred shadow catcher), projection.json (warm fill)}, tools/blender_factory.py (stage command, shared produce), tools/candidate_room.py (source pieces), tools/blender/specs/candidates/hero_room_01_v3_side_walls.json, map_factory/candidates/hero_room_01_blender_v3.json, map_factory/candidates/renders/hero_room_01_blender_v3/, docs/previews/candidates/hero_room_01_blender_v3_*.
- Tests: test_blender_factory.py + test_candidate_room.py 20/20 (Blender render tests included); py -3 tools/run_tests.py --changed 28/28.
- Capture: whole-image difference to reference base 74.68 / v1 74.71 / v2 73.59 / v3 74.23 (lower is closer). Visual: walls are continuous along the steps and much lower; stone still reads pale grey, mostly hidden behind HD props, ivy barely visible, east wall shadow falls on the sea. Not approved (candidate_unapproved).
- PR: https://github.com/shero92/skl-SF/pull/41
- Note: first recorded as TASK-0049 (commit 867e40d trailer); renumbered to TASK-0050 because the planner created another TASK-0049 on main (PR #42).
