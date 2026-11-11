---
id: TASK-0144
status: review
owner: claude
agent: claude
priority: high
branch: claude/room-v0023
depends_on: TASK-0135
issue: none
art_request: none
touches: tools/register_b1_b2_art.py,tools/build_v0023_patch.py,map_factory/metadata/asset_index.json,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/blocks/latest.json,map_factory/maps/hero_room_01/layers/latest.json,map_factory/maps/index.json,docs/previews/map_factory_renders/t0144_v0023/hero_room_01_v0023.png
test: python tools/run_tests.py --changed
done_when: The Codex B1/B2 candidates are registered as parts and placed in hero_room_01 v0023, captured in a real Godot window, with tests green and visual approval still false.
estimate_minutes: 90
---
# hero_room_01 v0023 - integrate Codex B1/B2

PRs 155 and 161 were merged after the owner reviewed the native captures and said to merge and build. `tools/register_b1_b2_art.py` registers 15 parts (A19 stairs, A20 finial, D20 compass, D21-D23 rope, P27-P30 table views, P31 stool, P32/P33 bookshelf, P34 headboard shelf, V034 plant) as trimmed uniform-fit downscales of the untouched masters. `tools/build_v0023_patch.py` replaces the study table (instance id kept, mounted props re-offset for the south-facing table), right bookcase (candles and armillary are baked into the new shelf), compass, and the four stair tiles, two supports and two pillars (new stair plus finial posts), and adds the headboard shelf, plant and rope fences. Navigation obstacles follow the renamed blocks.

## Evidence / handoff
- Real Godot capture: docs/previews/map_factory_renders/t0144_v0023/ (visual_approval stays false).
- Needs calibration: the west rope fence is hidden behind wall pieces; footprints and colliders of the new parts are unreviewed; bookshelf east/west and table props variants were not delivered.
