---
id: TASK-0128
status: review
owner: claude
agent: claude
priority: high
branch: claude/ysort
depends_on: TASK-0127
issue: none
art_request: none
touches: map_factory/scripts/room_factory.gd,scenes/main.gd,tools/map_factory_godot_smoke.gd,tools/build_v0021_patch.py,tools/verify_depth_sorting.gd,tools/tests/test_depth_sorting.py,tools/test_map.json,map_factory/maps/hero_room_01/,map_factory/maps/index.json,docs/previews/map_factory_renders/t0128_v0021/
test: python tools/run_tests.py --changed
done_when: On hero_room_01 the hero, companion and NPCs are ordered against walls and furniture by their ground Y; legacy maps keep the old layer; verified headlessly with a real capture of the published version.
estimate_minutes: 90
---
# Characters pass in front of and behind walls and furniture

**Problem (verified):** latest maps use the five-level builder. main.gd added `Entities` at a fixed z 35 while walls were z 30 and decor z 40, so the hero was always in front of every wall and always behind every piece of decor: no walking behind a wall, furniture hiding the hero even when the hero stood in front of it. RoomFactory already had an unified `occlusion_mode: world_y_sort` (WorldDepthSort root) that nothing used.

**Fix:** `RoomFactory.entities_parent(room)` puts characters inside WorldDepthSort (same effective z as walls and decor, so only the contact Y decides) and keeps the legacy z 35 layer for maps without it; main.gd uses it. hero_room_01 v0021 sets `occlusion_mode` to `world_y_sort` through Map Factory (no block, asset or position changed); v0001..v0020 are untouched. Shadows (z 20), light shafts and mounted items keep their passes.

## Limits
- Ordering uses each node's origin Y, so long diagonal wall pieces anchored at their far end can cover neighbours; in the v0021 capture the side wall runs overlap the end of the back bookcases slightly (about 1% of pixels differ from v0020). Tune anchors if the owner dislikes it.
- No pixel capture of a hero actually walking behind objects (headless checks structure and Y order).

## Evidence / handoff
- Tests: verify_depth_sorting.gd via test_depth_sorting.py (id depth_sorting); real capture docs/previews/map_factory_renders/t0128_v0021/.
- Next: owner review of the v0021 render; per-piece anchor tuning if needed.
