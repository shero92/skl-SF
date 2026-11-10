---
id: TASK-0016
status: review
owner: codex
branch: codex/hero-room-b3-target
agent: codex
touches: assets_hd/architecture/window_wall/v002,game_factory/environment/ART-0038/v002,assets_hd/architecture/compass_wood_door_views/v001,assets_hd/architecture/window_wall/v001,assets_hd/background/sea_light_lattice/v001,game_factory/environment/batch_B3_20261110,game_factory/environment/ART-0005/v001,.agents/graphics/deliveries/ART-0005,.agents/graphics/requests/ART-0005_hero_room_compass_wood_door.md,game_factory/environment/ART-0038/v001,.agents/graphics/deliveries/ART-0038,.agents/graphics/requests/ART-0038_hero_room_window_wall_piece.md,game_factory/environment/ART-0037/v001,.agents/graphics/deliveries/ART-0037,.agents/graphics/requests/ART-0037_hero_room_sea_light_lattice.md,.agents/tasks/TASK-0016_hero_room_compass_wood_door.md
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Owner-approved specialist delivery for ART-0005 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0005
---
# Specialist delivery: Closed arched wooden compass-emblem door

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0005

## Blocker / acceptance
- Request: ../graphics/requests/ART-0005_hero_room_compass_wood_door.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

## B3 owner production assignment
- Existing TASK-0016 expanded to B3: independent wooden compass door views, window wall and sea lattice candidates, per authenticated target. Reuse ART-0023 from PR151; do not regenerate or claim its owner approval.
- Scope only new assets, metadata, QA and one draft PR. Preserve originals, maps and Golden Cyclone.
- Tests: python tools/graphics_validation.py --changed; python tools/run_tests.py --changed.
- Next: generate independently and validate output/tiling; disclose any failed seam or resolution requirements.

- Current output: five primary sources (door4 + window v001), low-profile window v002 alternative; source and review revisions preserved. ART-0023 reused from PR151. Sea tile remains requested/needs_regeneration after two failed attempts.

- Tests: `python tools/graphics_validation.py --changed` exit0, png_checked0 (candidate masters out of production scope); independent primary source QA5/5. `python tools/run_tests.py --changed --timeout120`: **84/84 passed**, exit0.
- Five real Godot captures (door, window primary, window alternative, sea attempts1/2); receipts/hashes verified. Ten independent source outputs including attempts saved to project root with metadata; no cache dependency.
- Incomplete: sea tile generation size/alpha; window end join calibration / alternative aperture height; door decoration consistency; footprint/mount/collision annotation. No visual approval or integration.
- Next: owner reviews delivered candidates; regenerate failed sea and refine window/door limitations before declaring full target compliance.
