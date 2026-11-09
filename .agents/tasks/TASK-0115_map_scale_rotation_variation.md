---
id: TASK-0115
status: done
owner: claude
agent: claude
priority: medium
branch: claude/rotation-variation
depends_on: TASK-0114
issue: none
art_request: none
touches: map_factory/metadata/transform_rules.json,tools/map_factory_cli.py,tools/map_variation.py,tools/tests/test_map_variation.py,tools/test_map.json,map_factory/LAYER_SCHEMA.md,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/versions/v0016.json,map_factory/maps/hero_room_01/patches/v0016.json,map_factory/maps/index.json
test: python -m unittest discover -s tools/tests -p test_map_variation.py
done_when: The CLI limits scale and allows free rotation only for rotation-safe or flat pieces; a seeded variation tool produces update patches; hero_room_01 v0016 applies it to the flower clusters; tests pass.
estimate_minutes: 45
---
# Scale and rotation rules with seeded variation

Owner question 2026-11-09: can parts be turned 360 degrees or scaled. Free rotation is limited to rotation-safe and flat pieces; upright perspective pieces keep their four facing variants.

## Result (Claude, 2026-11-09)
Rules file, CLI validation, tools/map_variation.py and v0016 (flower clusters tilted and rescaled with seed 7) added. visual_approval stays false. Next step: review the render, then list more rotation-safe ids as new art (rubble, leaves) arrives.

## Closure (Claude, 2026-11-09)
Merged in PR #113; v0016 published.
