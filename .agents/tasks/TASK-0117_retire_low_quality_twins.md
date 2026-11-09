---
id: TASK-0117
status: review
owner: claude
agent: claude
priority: medium
branch: claude/hd-migration
depends_on: none
issue: none
art_request: none
touches: tools/migrate_low_to_hd.py,tools/build_hd_runtime_textures.py,tools/build_hero_room_blueprint.py,tools/audit_room_assets.py,tools/tests/test_hd_migration.py,tools/tests/test_hero_room_reference_relayout.py,tools/tests/test_hero_room_v0013_patch.py,tools/tests/test_directional_furniture.py,tools/test_map.json,assets_hd/hd_map.json,assets_hd/RULES.md,map_factory/scripts/hd_assets.gd,map_factory/scripts/asset_factory.gd,map_factory/scripts/room_factory.gd
test: python tools/run_tests.py --all
done_when: The 128 low-quality assets_generated twins are removed, their layout data is recorded in hd_map.json, every loader, tool and test works without them, and a real capture of hero_room_01 v0017 is visually unchanged.
estimate_minutes: 90
---
# Retire the low-quality twins safely

Owner request 2026-11-09: delete the old low-quality images now that the HD art is used. The low files were still the layout template of the HD runtime textures and registered in the registry, so they were first replaced by recorded data.

## Result (Claude, 2026-11-09)
128 low PNGs (and their .import files) removed; loaders resolve the HD twin; blueprint, registry check and tests read the recorded data. 65/65 tests pass. v0017 renders the same (two captures of the same state differ by at most 1 level in a thin band, the same as the capture noise). Not touched: map_factory/parts (no HD source exists), eight non-twin images in assets_generated, immutable map snapshots (paths unchanged). Next step: HD art for the parts that still have none (ocean tiles, shadows, glows).
