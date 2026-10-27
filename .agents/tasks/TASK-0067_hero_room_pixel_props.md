---
id: TASK-0067
status: review
owner: claude
branch: feat/hero-room-props
depends_on: TASK-0066
issue: none
art_request: none
---
# Hero Room 64 px pixel-art props (furniture, arch, columns) from Blender

**Goal:** second tranche of the owner's 2026-10-27 request (after TASK-0066 terrain): grid-aligned 64 px pixel-art props from the Hero Room reference, built by `tools/blender/props.py` from `tools/blender/specs/candidates/hero_room_01_props.json` and staged under `map_factory/candidates/renders/hero_room_01_props/`: bed, study table with stools, bookshelf, chest, blue-white vase, planter palm, brass globe, blue rug, wall banner, wall lantern, stone arch with columns, single column. Candidate pieces only: they do not fulfil or replace ART-0001/0010/0011/0015/0019/0020/0021 deliveries.

## Acceptance
- [x] `"grid": [w, d]` outputs: frame is whole 64 px cells, footprint in the bottom rows, transparent background, separate shadow.
- [x] Atlas packs multi-cell props and records `atlas_rect` (cells) for a Godot TileSet.
- [x] Tests: `py -3 tools/run_tests.py --only blender_factory`.
- [x] Staged with manifest, `rendered_unreviewed`; nothing approved or moved to `map_factory/parts/`.

## Evidence / handoff
- Changed files: `tools/blender/props.py` (12 builders), `tools/blender/builders.py` (registers props), `tools/blender/lib.py` (`grid_window`), `tools/blender/render_part.py` (grid frame), `tools/blender_factory.py` (multi-cell atlas, grid QA), `tools/art_qa.py` (grid mode), `tools/tests/test_blender_factory.py`, `tools/blender/README.md`, `tools/blender/specs/candidates/hero_room_01_props.json`, `map_factory/candidates/renders/hero_room_01_props/` (12 props + @4x masters + shadows, atlas 512x704, manifest).
- Staged: `py -3 tools/blender_factory.py stage tools/blender/specs/candidates/hero_room_01_props.json --out map_factory/candidates/renders/hero_room_01_props` -> 12 files, 0 problems, 0 warnings, shared 96-colour palette. Cells: arch 3x5, bed 2x5, rug 3x2, table 2x3, bookshelf 2x3, column 1x4, banner/lantern 1x3, chest/vase/planter/globe 1x2. Status rendered_unreviewed.
- Tests: `py -3 tools/run_tests.py --changed` (see commit).
- Visual review: none; per AGENTS.md rule 11 the agent did not open the renders.
- Next: assemble terrain (TASK-0066) and props in a Godot tile-map candidate and capture it beside the reference for the owner's review.
