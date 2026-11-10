---
id: TASK-0136
status: review
owner: codex
agent: codex
branch: codex/hero-room-b2-target
depends_on: TASK-0134
issue: none
art_request: ART-0020,ART-0008,ART-0006,ART-0024,ART-0022
touches: assets_hd/furniture/study_bookshelf_views/v001,assets_hd/furniture/headboard_shelf/v001,assets_hd/architecture/sphere_stair_post/v001,assets_hd/decor/rope_post_fence/v001,assets_hd/decor/compass_inlay/v001,game_factory/environment/batch_B2_20261110,game_factory/environment/ART-0020/v001,.agents/graphics/deliveries/ART-0020,.agents/graphics/requests/ART-0020_hero_room_study_bookshelf_views.md,game_factory/environment/ART-0008/v001,.agents/graphics/deliveries/ART-0008,.agents/graphics/requests/ART-0008_hero_room_headboard_shelf.md,game_factory/environment/ART-0006/v001,.agents/graphics/deliveries/ART-0006,.agents/graphics/requests/ART-0006_hero_room_sphere_finial.md,game_factory/environment/ART-0024/v001,.agents/graphics/deliveries/ART-0024,.agents/graphics/requests/ART-0024_hero_room_rope_post_fence.md,game_factory/environment/ART-0022/v001,.agents/graphics/deliveries/ART-0022,.agents/graphics/requests/ART-0022_hero_room_compass_floor_inlay.md,.agents/tasks/TASK-0136_hero_room_target_batch_b2.md
test: python tools/graphics_validation.py --changed; python tools/run_tests.py --changed
done_when: Eight independent B2 sources with measured manifests, native reviews, real Godot captures and one draft PR; other bookshelf/headboard views explicitly deferred per target spec.
---
# Hero Room target batch B2

Owner explicitly assigned this batch and authenticated target. New images only; preserve old deliveries in archives, masters, maps and Golden Cyclone. Full sphere-topped post follows newer target spec, superseding old cap-only wording. Two bookshelf views and south headboard view now; remaining views deferred. No visual approval or integration.

- Delivered: eight independent PNG masters, four nonselected attempts retained, five real Godot captures.
- Tests: graphics_validation.py --changed exit0 (production scope excludes candidates); independent technical QA8/8; run_tests.py --changed --timeout120 **80/80 passed**, exit0.
- Sources and metadata copied to project root with SHA receipt; master minima deviations documented, no upscaling.
- Next: owner review; Claude annotates mounts/footprints and integrates accepted assets. Other bookshelf/headboard facings deferred per current spec.
