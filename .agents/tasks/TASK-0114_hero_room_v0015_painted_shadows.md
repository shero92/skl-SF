---
id: TASK-0114
status: review
owner: claude
agent: claude
priority: high
branch: claude/hero-room-v0015
depends_on: TASK-0109
issue: none
art_request: none
touches: map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/versions/v0015.json,map_factory/maps/hero_room_01/patches/v0015.json,map_factory/maps/index.json,tools/map_factory_cli.py,tools/tests/test_camera_light_shafts.py,tools/map_audit.py,tools/tests/test_map_factory_tools.py,docs/previews/map_factory_renders/t0114_v0015/evidence.json
test: python tools/run_tests.py --changed
done_when: hero_room_01 v0015 is published immutably after v0014 with shadow_mode painted and a lighting block, validated by the CLI, captured with a real Godot render that passes the evidence gate; visual_approval stays false.
estimate_minutes: 45
---
# Hero Room v0015: painted shadows and light pools

Layout unchanged from v0014. The CLI now accepts and validates `shadow_mode` and `lighting`. The map audit treats directional variants (F05_south) as their base asset.

## Result (Claude, 2026-11-09)
v0015 published through tools/map_factory_cli.py apply; v0014 untouched. Evidence capture passed (docs/previews/map_factory_renders/t0114_v0015/). Automatic zone hints are not an approval. Next step: owner reviews the render, then a layout pass once ART-0032..0035 are delivered.
