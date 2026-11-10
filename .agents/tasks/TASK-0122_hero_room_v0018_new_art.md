---
id: TASK-0122
status: review
owner: claude
agent: claude
priority: high
branch: claude/room-art-0032-0035
depends_on: TASK-0116
issue: none
art_request: none
touches: tools/register_environment_art.py,tools/build_v0018_patch.py,tools/map_data.py,map_factory/metadata/asset_index.json,map_factory/parts/,map_factory/maps/hero_room_01/,map_factory/maps/index.json,docs/previews/map_factory_renders/t0122_v0018/
test: python tools/run_tests.py --changed
done_when: The owner-agreed ART-0032..0035 masters are registered as runtime parts and hero_room_01 v0018 is published with them; a real Godot capture passes the evidence gate; visual_approval stays false.
estimate_minutes: 120
---
# Hero Room v0018: use the new ART-0032..0035 art

Owner request 2026-11-10: all new graphics agreed, start using them.

## Result (Claude, 2026-11-10)
- tools/register_environment_art.py: 34 masters (assets_hd, unchanged) -> trimmed BOX-downscaled parts W027-W035, E025-E040, V025-V033 with owner approval recorded.
- v0018 (tools/build_v0018_patch.py, published with map_factory_cli.py apply): cliff base and foam under the front edge and sides, coast stacks/arches/foam, planters, mounds, palms, hanging vines, connected side wall runs (host instances reused so lanterns, banners and ivy stay mounted). Real capture in docs/previews/map_factory_renders/t0122_v0018/.
- Not used yet: straight/corner wall pieces, parapet cap, terrace straight edge, haze strip. Side walls recede diagonally and slightly overlap the floor. Not owner-reviewed; visual_approval false.
- Next: owner review of the render, then tune positions and replace the rear wall.
