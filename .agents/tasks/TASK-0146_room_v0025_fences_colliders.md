---
id: TASK-0146
status: review
owner: claude
agent: claude
priority: medium
branch: claude/room-v0025
depends_on: TASK-0145
issue: none
art_request: none
touches: tools/build_v0025_patch.py,map_factory/metadata/asset_index.json,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/blocks/latest.json,map_factory/maps/hero_room_01/layers/latest.json,map_factory/maps/index.json,docs/previews/map_factory_renders/t0146_v0025/hero_room_01_v0025.png
test: python tools/run_tests.py --changed
done_when: hero_room_01 v0025 shows both rope fences on the floor, the B1-B3 furniture parts block the hero with base colliders, a real Godot capture exists and tests are green; visual approval stays false.
estimate_minutes: 45
---
# hero_room_01 v0025 - visible rope fences and furniture colliders

The v0023 rope posts sat behind the side walls under Y-sorting. `tools/build_v0025_patch.py` moves both fences onto the visible floor corners. The catalog gives P27-P34, V034, A20-A24 and D21 a provisional base collider (bottom strip of the sprite), so the hero no longer walks through the new table, shelf, plant, posts and stool.

## Evidence / handoff
- Real Godot capture: docs/previews/map_factory_renders/t0146_v0025/ (visual_approval stays false).
- Collider sizes are estimates from the sprite base, not owner-reviewed; the target's curved front edge is not reproduced.
