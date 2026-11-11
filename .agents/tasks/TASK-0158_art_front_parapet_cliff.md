---
id: TASK-0158
status: todo
owner: codex
agent: codex
priority: high
branch: codex/art-0046-0047-front-cliff
depends_on: TASK-0148
issue: none
art_request: ART-0046
touches: .agents/tasks/TASK-0158_art_front_parapet_cliff.md,.agents/graphics/deliveries/ART-0046,.agents/graphics/deliveries/ART-0047
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0046 (left and right front parapet halves) and ART-0047 (round cliff base) are delivered as independent PNGs that match their reference crops, each with a valid delivery manifest, in a PR whose checks pass.
---
# Codex art: front curved parapet pair and round cliff base

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0046_hero_room_front_curved_parapet_pair.md and .agents/graphics/requests/ART-0047_hero_room_round_cliff_base.md.
