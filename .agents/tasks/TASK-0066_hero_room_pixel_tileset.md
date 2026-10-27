---
id: TASK-0066
status: review
owner: claude
branch: feat/hero-room-tileset
depends_on: none
issue: none
art_request: none
---
# Hero Room 64 px pixel-art tileset from Blender

**Goal:** owner request 2026-10-27: turn the Hero Room reference (`map_factory/references/hero_room_01_original.png`) into 64x64 pixel-art tiles for a tactics RPG map. This task delivers the first tranche, the terrain tiles (sandstone floor variants, wall face and top, cliff rock and cliff top, sea, shore foam, grass/flowers, stair step), built by `tools/blender/builders.py` from `tools/blender/specs/candidates/hero_room_01_tileset.json`, staged under `map_factory/candidates/renders/hero_room_01_tileset/`. Furniture, arch/columns, banners and plants follow in later tasks.

## Acceptance
- [x] Fixed-frame tile rendering: each tile renders to exactly 64x64, fully opaque (spec `"tile": true`).
- [x] Optional palette reduction (`"pixel_art": {"colors": N}`) after the 4x downscale.
- [x] `art_qa` tile mode: opaque, 64-multiple size; sprite checks unchanged.
- [x] Tests: `py -3 tools/run_tests.py --only blender_factory`.
- [x] Staged with manifest, status `rendered_unreviewed`; no art approved, nothing in `map_factory/parts/`.

## Evidence / handoff
- Changed files: `tools/blender/lib.py` (fixed frame, `periodic_material`, `wrap_copies`), `tools/blender/builders.py` (`terrain_tile`), `tools/blender/render_part.py` (tile frame), `tools/blender_factory.py` (`pixel_art`, `atlas`, seam warnings), `tools/art_qa.py` (tile mode, seam metric), `tools/tests/test_blender_factory.py` (3 tests), `tools/blender/README.md`, `tools/blender/specs/candidates/hero_room_01_tileset.json`, `map_factory/candidates/renders/hero_room_01_tileset/` (11 tiles 64x64 + @4x masters, atlas 256x192, manifest).
- Staged: `py -3 tools/blender_factory.py stage tools/blender/specs/candidates/hero_room_01_tileset.json --out map_factory/candidates/renders/hero_room_01_tileset` -> 11 files, 0 problems, 0 warnings; seams all <= 1.9 except sea_foam y (13.9, intended: not periodic in y). Shared 64-colour palette. Status rendered_unreviewed.
- Tests: `py -3 tools/run_tests.py --only blender_factory` PASS (Blender renders included).
- Visual review: none. Per AGENTS.md rule 11 the agent did not open the tiles; the owner reviews the atlas or a captured tile map.
- Next: build a small tile-map candidate in Godot from the atlas and capture it beside the reference; then the furniture/arch/plant tranches.
