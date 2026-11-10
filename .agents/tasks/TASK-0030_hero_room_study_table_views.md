---
id: TASK-0030
status: review
owner: codex
agent: codex
branch: codex/hero-room-b1-target
depends_on: TASK-0134
issue: none
art_request: ART-0019,ART-0039,ART-0011,ART-0025
touches: game_factory/environment/batch_B1_20261110,.agents/tasks/TASK-0030_hero_room_study_table_views.md,.agents/graphics/requests/ART-0019_hero_room_study_table_views.md,.agents/graphics/requests/ART-0011_hero_room_blue_white_planter.md,.agents/graphics/requests/ART-0025_hero_room_entrance_stairs.md,.agents/graphics/requests/ART-0039_hero_room_wooden_stool.md,.agents/graphics/deliveries/ART-0019,.agents/graphics/deliveries/ART-0039,.agents/graphics/deliveries/ART-0011,.agents/graphics/deliveries/ART-0025,assets_hd/furniture/study_table_views/v001,assets_hd/furniture/study_stool/v001,assets_hd/plants/blue_white_planter/v001,assets_hd/architecture/entrance_stairs/v001,game_factory/environment/ART-0019/v001,game_factory/environment/ART-0039/v001,game_factory/environment/ART-0011/v001,game_factory/environment/ART-0025/v001
test: python tools/graphics_validation.py --changed; python tools/run_tests.py --changed
done_when: Seven independent B1 RGBA masters and request copies have measured metadata, native reviews, real Godot captures, tests and one draft PR; owner review and integration remain separate.
---
# Hero Room target — batch B1

Owner explicitly assigned built-in image_gen production. Target SHA-256 verified: 4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323. Follow docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md. Preserve prior masters, maps and Golden Cyclone. One independent generation per PNG. No owner approval claimed.

## Evidence / handoff
- In progress: four study table views, stool, blue-white planter and entrance stairs.
- Next: independent production and QA; Claude integrates after owner review.

- Evidence: seven independent masters, two rejected attempts, four actual Godot viewport captures.
- Tests: changed suite 74/80 initially; after local class-cache import and archived stair schema preservation, failed groups rerun 6/6 passed. graphics_validation exit 0 (candidate masters outside production scope); separate technical QA seven sources passed.
- Limitations: literal master size minima not all met by built-in output; no upscaling. Physical footprints/colliders and stair mounts need scene annotation. Owner approval and Claude integration pending.
- Historical stair delivery archived byte-for-byte; compatibility files entries point to archived original.
- Next: owner reviews B1 candidates and size deviations, Claude integrates only accepted assets.

## Preserved original task contract

# Specialist delivery: Four-perspective study table

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0019

## Blocker / acceptance
- Request: ../graphics/requests/ART-0019_hero_room_study_table_views.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

## Tracking reconciliation
- Concurrent main allocation used TASK-0135 for Claude room v0022 props. This graphics batch now uses its existing ART-0019 parent TASK-0030. Prior receipt TASK-0135_codex_7dc92e3234.json is immutable historical evidence for commit9e2f8d873a6eb8030d18d85bc7cec29c0d3ba30f; it is not the Claude task and not a second bill.
