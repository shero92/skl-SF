---
id: TASK-0156
status: todo
owner: codex
agent: codex
priority: high
branch: codex/art-0042-0043-rear-walls
depends_on: TASK-0148
issue: none
art_request: ART-0042
touches: .agents/tasks/TASK-0156_art_rear_walls.md,.agents/graphics/deliveries/ART-0042,.agents/graphics/deliveries/ART-0043
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0042 and ART-0043 are delivered as independent PNGs that match their reference crops, each with a delivery manifest listing request_id and files (path and sha256), in a PR whose checks pass.
---
# Codex art: rear-left wall with window and rear-right wall with arched door niche

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0042_hero_room_rear_left_ruined_wall_window.md and .agents/graphics/requests/ART-0043_hero_room_rear_right_wall_arched_door_niche.md.
- Draw from the reference crop named in each request; one piece per file; no lanterns, plants or banners baked in.
