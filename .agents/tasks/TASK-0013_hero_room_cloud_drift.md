---
id: TASK-0013
status: in_progress
owner: codex
branch: codex/hero-room-cloud-variants
agent: codex
touches: .agents/tasks/TASK-0013_hero_room_cloud_drift.md,.agents/graphics/requests/ART-0002_hero_room_cloud_drift.md,.agents/graphics/deliveries/ART-0002,assets_hd/background/drifting_clouds/v001,game_factory/environment/ART-0002/v001
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Owner-approved specialist delivery for ART-0002 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0002
---
# Specialist delivery: Independent drifting cloud variants

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0002

## Blocker / acceptance
- Request: ../graphics/requests/ART-0002_hero_room_cloud_drift.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

Owner next graphics assignment: three independent cloud silhouettes per authenticated current Hero Room target; sources, metadata and real Godot review. No runtime scrolling implementation or approval.
