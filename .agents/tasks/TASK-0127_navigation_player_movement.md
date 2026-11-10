---
id: TASK-0127
status: review
owner: claude
agent: claude
priority: high
branch: claude/nav-player
depends_on: none
issue: none
art_request: none
touches: map_factory/scripts/navigation_grid.gd,map_factory/scripts/room_factory.gd,scenes/player.gd,scenes/main.gd,scenes/game_factory_actor.gd,scenes/game_factory_demo.gd,tools/verify_navigation_grid.gd,tools/tests/test_navigation_grid.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: HeroPlayer movement uses the Map Factory navigation block through one validator shared with the game factory actor; closed by default, slides along edges, no diagonal wall crossing; verified headlessly.
estimate_minutes: 90
---
# Navigation metadata drives player movement

**Problem (verified):** HeroPlayer (scenes/player.gd) ignored the snapshot `navigation` block entirely; only game_factory_actor.gd used it, with its own copy of the cell logic that stopped dead instead of sliding and treated a missing block as "everything blocked".

**Fix:** `NavigationGrid` (map_factory/scripts/navigation_grid.gd) parses the existing schema_version 1 block (regions, links, default; no new schema). `RoomFactory` exposes it as the `navigation` meta; main.gd gives it to the player; player and actor ask `allowed_motion()` (full step, else the axis that still works, else zero). Maps without a block stay unrestricted.

## Limits (not claimed)
- Only the walk mode is wired; fly and swim are parsed but no character uses them.
- Furniture obstacles stay on the room's StaticBody2D collision; `obstacles` entries are not used by the grid.
- hero_room_01 navigation is marked `needs_review`; the hero is now confined to its safe-walk region (cells 1..15 x 2..8 plus the stairs row).
- Dialogue stop and companion movement are unchanged.

## Evidence / handoff
- Tests: verify_navigation_grid.gd via test_navigation_grid.py (id navigation_grid).
- Next: owner review of the walkable region; obstacle footprints from placed blocks.
