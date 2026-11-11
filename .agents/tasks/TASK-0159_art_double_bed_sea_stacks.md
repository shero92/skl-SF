---
id: TASK-0159
status: todo
owner: codex
agent: codex
priority: medium
branch: codex/art-0048-0049-bed-stacks
depends_on: TASK-0148
issue: none
art_request: ART-0048
touches: .agents/tasks/TASK-0159_art_double_bed_sea_stacks.md,.agents/graphics/deliveries/ART-0048,.agents/graphics/deliveries/ART-0049
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0048 (double bed, foot to the south) and ART-0049 (arch island and stack cluster) are delivered as independent PNGs that match their reference crops, each with a valid delivery manifest, in a PR whose checks pass.
---
# Codex art: double bed and sea-stack islands

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0048_hero_room_double_bed_three_quarter.md and .agents/graphics/requests/ART-0049_hero_room_sea_stack_islands.md.
