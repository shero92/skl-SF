---
id: TASK-0109
status: done
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: none
issue: none
art_request: none
touches: map_factory/scripts/shadow_painter.gd,map_factory/scripts/room_factory.gd,map_factory/LAYER_SCHEMA.md,tools/verify_shadow_painter.gd,tools/tests/test_shadow_painter.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_shadow_painter.py
done_when: A separate Level4_PaintedShadows node paints each object's cast shadow from its real alpha silhouette along the map light direction, plus a soft contact occlusion under the footprint; it is toggleable, owner-linked, multiply-blended, never darkens the casting object, and Godot headless checks pass.
estimate_minutes: 60
---
# Map Factory: separate painted shadow level from object silhouettes

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_shadow_painter.py pass. Opt in with shadow_mode painted. Scratch render of hero_room_01 v0014: 79 owner-linked painted shadows.
Next step: review and merge the PR, then use the tools on a new room version (v0015).

## Closure (Claude, 2026-11-09)
Merged in PR #111 (shadow base alignment fixed in PR #119); painted shadow level is on in hero_room_01 since v0015.
