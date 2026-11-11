---
id: TASK-0160
status: todo
owner: codex
agent: codex
priority: low
branch: codex/art-0040-0037-lantern-sea
depends_on: TASK-0148
issue: none
art_request: ART-0040
touches: .agents/tasks/TASK-0160_art_lantern_sea_light.md,.agents/graphics/deliveries/ART-0040,game_factory/environment/ART-0037/v002
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0040 (east-pointing wall lantern) is delivered and ART-0037 (sea light lattice) is regenerated as a new version without overwriting the rejected one, each with a valid delivery manifest, in a PR whose checks pass.
---
# Codex art: east-pointing wall lantern and sea light lattice regeneration

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0040_hero_room_wall_lantern_east.md and .agents/graphics/requests/ART-0037_hero_room_sea_light_lattice.md.
