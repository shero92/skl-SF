---
id: TASK-0025
status: review
owner: claude
branch: art/ART-0014
agent: claude
touches: .agents/graphics/deliveries/ART-0014/
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Owner-approved specialist delivery for ART-0014 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: 2026-10-26T21:48:35.043037+00:00
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0014
---
# Specialist delivery: Irregular broken front floor-edge pieces

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0014

## Blocker / acceptance
- Request: ../graphics/requests/ART-0014_hero_room_broken_floor_edge.md
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

## Evidence
- Delivery: .agents/graphics/deliveries/ART-0014/ (4 native PNGs, 4 masters, 4 shadows, manifest.json with measured SHA-256).
- Command: py -3 tools/blender_factory.py deliver ART-0014 --agent claude (about 24 s).
- QA fix found during this task: the halo rule flagged dark shaded geometry; it now compares each soft edge pixel with its opaque neighbours (tools/art_qa.py, with tests).
- Not yet in map_factory/parts or any map; needs Godot assembly and the owner's check of the final capture.
