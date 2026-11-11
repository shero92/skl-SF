---
id: TASK-0153
status: blocked_on_art
owner: claude
agent: claude
priority: low
branch: claude/room-lantern-sea-light
depends_on: TASK-0160
issue: none
art_request: ART-0040
touches: .agents/tasks/TASK-0153_room_side_lantern_sea_light.md,tools/build_lantern_sea_light_patch.py
test: python tools/run_tests.py --changed
done_when: After ART-0040 and the regenerated ART-0037 are merged, the west wall carries the east-pointing lantern and the sea shows the light lattice in a new immutable version with a real Godot capture.
estimate_minutes: 30
---
# hero_room_01: west wall lantern and sea light lattice

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Blocked until Codex delivers ART-0040 and regenerates ART-0037 (TASK-0160).
