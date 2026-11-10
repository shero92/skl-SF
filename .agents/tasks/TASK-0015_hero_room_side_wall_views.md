---
id: TASK-0015
status: done
owner: claude
branch: claude/integrate-art-0004-0014
agent: claude
touches: .agents/graphics/deliveries/ART-0004/
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Owner-approved specialist delivery for ART-0004 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: 2026-10-26T21:40:51.164754+00:00
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0004
---
# Specialist delivery: Four-perspective side-wall run blocks

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0004

## Blocker / acceptance
- Request: ../graphics/requests/ART-0004_hero_room_side_wall_views.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

## Claim
- Claimed by Claude Code under the owner's Blender decision (2026-10-26): pieces are built and rendered with tools/blender_factory.py (no AI image generation); visual check happens on the final Godot capture.
- Owner decision 2026-10-26: keep the orthographic projection; east/west side walls show only their top and end (classic top-down JRPG rooms).

## Evidence
- Delivery: .agents/graphics/deliveries/ART-0004/ (4 native PNGs, 4 masters, 4 shadows, manifest.json with measured SHA-256).
- Command: py -3 tools/blender_factory.py deliver ART-0004 --agent claude (34 s).
- Not yet in map_factory/parts or any map; needs Godot assembly and the owner's check of the final capture.

## Closure (Claude, 2026-11-09)
Owner accepted the delivery in chat (2026-11-09: "I ACCEPT THEM CONTINUE"). ART-0004 is integrated: catalog IDs W023 to W026 (north, east, south, west wall runs), PNGs in map_factory/parts, request status integrated, exact delivered bytes (SHA-256 verified by tools/art_delivery.py). Tests: tools/tests/test_blender_catalog.py. The pieces are registered and available; hero_room_01 v0017 does not place them yet (it uses the owner HD walls), so the room render is unchanged. Next step: place them in a new room version if the owner wants them in the room.
