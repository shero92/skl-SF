---
id: TASK-0150
status: blocked_on_art
owner: claude
agent: claude
priority: high
branch: claude/room-curved-perimeter
depends_on: TASK-0156
issue: none
art_request: ART-0044
touches: .agents/tasks/TASK-0150_room_curved_perimeter.md,tools/register_curved_walls.py,tools/build_curved_perimeter_patch.py
test: python tools/run_tests.py --changed
done_when: After ART-0042 to ART-0047 are delivered and merged, the straight perimeter walls, front low walls and cliff chunks of hero_room_01 are replaced by the curved pieces in a new immutable version, with a real Godot capture and green tests.
estimate_minutes: 120
---
# hero_room_01: curved perimeter from ART-0042 to ART-0047

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Blocked until Codex delivers ART-0042, ART-0043, ART-0044, ART-0045, ART-0046 and ART-0047 (TASK-0156 to TASK-0158).
- Remove the PerimeterWall_*, BackWall*, FrontLowWall* and terrace cliff blocks; place the six new pieces with free_transform.
- Keep lanterns, banners, ivy and flowers as separate pieces and re-seat them on the new walls so they are not hidden.
