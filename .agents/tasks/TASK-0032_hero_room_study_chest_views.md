---
id: TASK-0032
status: review
owner: codex
branch: codex/hero-room-b4-chest
agent: codex
touches: .agents/tasks/TASK-0032_hero_room_study_chest_views.md,.agents/graphics/requests/ART-0021_hero_room_study_chest_views.md,.agents/graphics/deliveries/ART-0021,assets_hd/furniture/study_chest_views/v001,game_factory/environment/ART-0021/v001
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Owner-approved specialist delivery for ART-0021 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0021
---
# Specialist delivery: Four-perspective study-zone closed chest

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0021

## Blocker / acceptance
- Request: ../graphics/requests/ART-0021_hero_room_study_chest_views.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

## Owner next graphics assignment
Produce four independent plain oak chest views, per current target reference SHA4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323. Keep approved crate/chest assets unchanged. Native review58x73 per calibrated visible placement; source >=4x, separate collision annotation. Built-in image_gen only. No map/catalog integration or visual approval.

## Actual delivery evidence
- Four independently generated plain-oak closed chest facings; west attempt1 retained and corrected (body iron straps to wood stiles). Exact delivery filenames and SHA manifests supplied.
- Actual Godot viewport capture at placement58x73/catalog191x157/catalog2x. Source masters unchanged, native QA derivatives only.
- `python tools/graphics_validation.py --changed`: exit0, png_checked0 (candidate masters outside production scope); independent source QA4/4 and8 derivatives verified.
- `python tools/run_tests.py --changed --timeout120`: **85/85 passed**, exit0.
- Sources/metadata copied to project root with SHA receipt; no cache dependency. Owner review and footprint/collider/depth calibration pending.
- Next: owner reviews candidate set, Claude integrates accepted art without altering prior masters/maps.
