---
id: TASK-0161
status: todo
owner: codex
agent: codex
priority: low
branch: codex/art-0041-skirmish-tiles
depends_on: TASK-0147
issue: none
art_request: ART-0041
touches: .agents/tasks/TASK-0161_art_skirmish_field_tiles.md,.agents/graphics/deliveries/ART-0041
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0041 (skirmish field tiles and cell markers) is delivered with a valid delivery manifest in a PR whose checks pass.
---
# Codex art: skirmish field tiles and cell markers

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Request: .agents/graphics/requests/ART-0041_skirmish_field_tiles.md.
