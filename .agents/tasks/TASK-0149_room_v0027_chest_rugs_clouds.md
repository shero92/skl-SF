---
id: TASK-0149
status: review
owner: claude
agent: claude
priority: high
branch: claude/room-v0027
depends_on: TASK-0148
issue: none
art_request: ART-0015
touches: .agents/tasks/TASK-0149_room_v0027_chest_rugs_clouds.md,tools/register_b4_art.py,tools/build_v0027_patch.py,docs/previews/map_factory_renders/t0149_v0027/hero_room_01_v0027.png,map_factory/metadata/asset_index.json,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/blocks/latest.json,map_factory/maps/hero_room_01/layers/latest.json,map_factory/maps/index.json
test: python tools/run_tests.py --changed
done_when: The merged deliveries ART-0021 (chest, four views), ART-0015 (two oblique rugs) and ART-0002 (three clouds) are registered in the Map Factory catalog and placed in hero_room_01 v0027 with tools/room_design.py; a real Godot capture exists; tests are green; visual approval stays false.
estimate_minutes: 60
---
# hero_room_01 v0027: chest views, oblique rugs and clouds

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Register the three merged deliveries as catalog parts (same pattern as tools/register_b3_art.py).
- Bedroom rug under the bed instead of the enlarged D01; study rug under the table; chest views replace the old crates where the target shows a chest; clouds in the sky layer.
- Compare the capture with the target using tools/art_reference_crop.py boxes for the bed and table areas.

## Evidence / handoff
- Parts F027-F030 (chest north/east/south/west), D27/D28 (oblique rugs), B12-B14 (clouds) registered by `tools/register_b4_art.py`.
- v0027: oblique rugs replace BedRug/TableRug as free decals; chest south and west views replace CrateF12/CrateF10; three clouds in the sky.
- Real Godot capture: docs/previews/map_factory_renders/t0149_v0027/ (visual_approval stays false).
- Chest canvas (76 px wide) and chest colliders are provisional; the north and east chest views are registered but not placed.
