---
id: TASK-0154
status: todo
owner: claude
agent: claude
priority: medium
branch: claude/room-region-report
depends_on: TASK-0148
issue: none
art_request: none
touches: .agents/tasks/TASK-0154_room_region_progress_report.md,tools/room_region_report.py,tools/tests/test_room_region_report.py,map_factory/references/hero_room_01_regions.json
test: python tools/run_tests.py --changed
done_when: One command writes a sheet of every named region of the target next to the same region of the latest Godot capture, plus a per-region difference number, so each new room version shows which regions moved closer to the target. It never sets visual approval.
estimate_minutes: 60
---
# Target-vs-game region report for every room version

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Regions come from the crop boxes already used in ART-0042 to ART-0049 plus the bed, table, arch and stair areas.
- The number is a progress hint only; owner approval of the look stays separate.
