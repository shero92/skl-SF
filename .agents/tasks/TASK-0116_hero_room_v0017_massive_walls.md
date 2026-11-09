---
id: TASK-0116
status: done
owner: claude
agent: claude
priority: medium
branch: claude/hero-room-v0017
depends_on: TASK-0115
issue: none
art_request: none
touches: map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/versions/v0017.json,map_factory/maps/hero_room_01/patches/v0017.json,map_factory/maps/index.json,docs/previews/map_factory_renders/t0116_v0017/evidence.json
test: python tools/run_tests.py --changed
done_when: hero_room_01 v0017 is published immutably after v0016 with the wall pieces scaled to 1.5 so the side and rear walls read as massive ruins; a real Godot capture passes the evidence gate; visual_approval stays false.
estimate_minutes: 30
---
# Hero Room v0017: massive ruin walls

Only the scale of 29 existing wall pieces (W01 to W14 except the low front wall W10) changes, using registered assets; no art is generated. The scale 1.5 is not an integer multiple, so edges are slightly softer than native pixels; the real fix is the connected wall art of ART-0032.

## Result (Claude, 2026-11-09)
v0017 published with tools/map_factory_cli.py apply; v0014 to v0016 untouched. Evidence capture passed (docs/previews/map_factory_renders/t0116_v0017/). Next step: owner review of the render, then relayout with ART-0032..0035 art.

## Closure (Claude, 2026-11-09)
Merged in PR #114; v0017 published (visual_approval of the room stays false).
