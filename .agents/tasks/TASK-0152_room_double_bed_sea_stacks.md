---
id: TASK-0152
status: blocked_on_art
owner: claude
agent: claude
priority: medium
branch: claude/room-bed-sea-stacks
depends_on: TASK-0159
issue: none
art_request: ART-0048
touches: .agents/tasks/TASK-0152_room_double_bed_sea_stacks.md,tools/register_bed_sea_stacks.py,tools/build_bed_sea_stacks_patch.py
test: python tools/run_tests.py --changed
done_when: After ART-0048 and ART-0049 are merged, the double bed replaces RoyalBed and the two sea-stack pieces stand on the horizon in a new immutable version with a real Godot capture.
estimate_minutes: 45
---
# hero_room_01: double bed and sea-stack islands

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Blocked until Codex delivers ART-0048 and ART-0049 (TASK-0159).
- The bed keeps its grid cells and the interaction; only the drawn part changes.
