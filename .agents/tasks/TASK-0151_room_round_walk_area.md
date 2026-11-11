---
id: TASK-0151
status: blocked_on_art
owner: claude
agent: claude
priority: medium
branch: claude/room-round-walk-area
depends_on: TASK-0150
issue: none
art_request: ART-0046
touches: .agents/tasks/TASK-0151_room_round_walk_area.md,tools/build_round_walk_area_patch.py,tools/tests/test_round_walk_area.py
test: python tools/run_tests.py --changed
done_when: The walkable cells and colliders of hero_room_01 follow the round terrace: corner cells outside the curved walls are not walkable, the stair opening stays reachable, and a headless test proves the hero cannot leave the floor.
estimate_minutes: 90
---
# hero_room_01: walking grid and colliders for the round terrace

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Movement stays on squares; only the set of walkable cells changes (floor_footprint and navigation).
- Give each curved wall piece a collider that matches its arc, or block the cells it covers.
- Depends on the curved perimeter version (TASK-0150).
