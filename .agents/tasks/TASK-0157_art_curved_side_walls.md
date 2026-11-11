---
id: TASK-0157
status: todo
owner: codex
agent: codex
priority: high
branch: codex/art-0044-0045-side-walls
depends_on: TASK-0148
issue: none
art_request: ART-0044
touches: .agents/tasks/TASK-0157_art_curved_side_walls.md,.agents/graphics/deliveries/ART-0044,.agents/graphics/deliveries/ART-0045
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0044 and ART-0045 are delivered as independent curved wall PNGs that match their reference crops (the east wall is its own drawing, not a mirror), each with a valid delivery manifest, in a PR whose checks pass.
---
# Codex art: west and east curved side walls

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0044_hero_room_west_curved_side_wall.md and .agents/graphics/requests/ART-0045_hero_room_east_curved_side_wall.md.
