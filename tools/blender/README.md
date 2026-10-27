# Blender part factory — build guide (TASK-0046, TASK-0054)

Owner decisions 2026-10-26/27 (AGENTS.md rules 4 and 11): environment pieces are **built by scripts in Blender**, the room is assembled in Godot from those pieces, and only the **final room comparison sheet** is looked at. Pieces are checked by scripted QA only (`tools/art_qa.py`, palette check, manifests, measured anchors); agents never open piece PNGs. Defects are fixed by changing a builder, spec or projection and re-rendering, never by hand-painting or AI image generation. The nine accepted HD sprites (W021, W022, A017, A018, D019, P023-P026) are never changed or replaced.

## 1. Setup (owner's Windows host)
- Blender 5.2 LTS. Found through `--blender`, `BLENDER_EXECUTABLE`, `blender_executable` in `.agents/planner/config.json`, then the default install path.
- Godot 4.7 (`godot_executable` in the same config) for captures. A fresh worktree first needs `<godot> --path . --headless --import`, or the capture fails with `Identifier "RoomFactory" not declared`.
- Python 3 with Pillow.

## 2. Files
| File | Runs in | Role |
| --- | --- | --- |
| `projection.json` | config | 64 px per tile, supersample 4, camera elevation 45°, sun (upper left), warm fill, world, Cycles samples, padding |
| `lib.py` | Blender | scene, orthographic camera with square-floor pixel aspect, sun + fill, materials (`limestone`, `wood`, `rope`, `gold`, `sapphire`, `flat`), `block`, lean, join, ivy, colour pass + separate shadow pass (optional floor-only catcher polygon) |
| `builders.py` | Blender | parametric pieces; each returns `(objects, anchors)` |
| `render_part.py` | Blender | renders every output of one spec: `<name>.png` master, `<name>_shadow.png`, `<name>.json` (frame, anchors) |
| `specs/ART-*.json` | data | one spec per ART request; output names equal the request's `output_paths` |
| `specs/candidates/*.json` | data | candidate-only pieces (no ART id), staged for one review layout |
| `../blender_factory.py` | Python | finds Blender, renders, native + 4x master + shadow PNGs, technical + palette QA, manifest |
| `../art_qa.py` | Python | transparency, backing, halo, clipping, mirrored/rotated copies |
| `../candidate_room.py` + `../capture_candidate_room.gd` | Python + Godot | assemble a review layout over a published map version, capture, compare with the reference |

## 3. Projection (`projection.json`)
- 1 Blender unit = 1 map tile = `tile_px` (64) pixels. +X east (screen right), +Y north (into the screen), +Z up.
- The camera is orthographic, looks north, tilted down by `camera_elevation_deg`. Pixel aspect keeps the floor grid square, so a 1x1 floor tile is exactly 64x64 and a height `h` appears as `h · cot(elevation) · 64` px (at 45°: 64 px per tile of height).
- Sun azimuth 135 = light from the upper left; shadows fall to the lower right. The warm `fill` (shadowless, from the front right) keeps faces turned away from the sun golden.
- A spec may override any key with `"projection": {...}` (e.g. a warmer `world` for the v4 side walls). Keep the shared file stable: changing it changes every future re-render.
- Calibrate after any projection change: `py -3 tools/blender_factory.py calibrate` must print `"ok": true`.

## 4. Builders (`builders.py`)
Builders model the front facing south (toward the camera). A facing rotates the 3D model, so every facing is a real render, never a mirrored bitmap.

| Builder | Used by | Key params | Anchors |
| --- | --- | --- | --- |
| `calibration_tile` | `calibrate` | — | `tile_top_left` |
| `wall_run` | ART-0004 | `length`, `height`, `thickness`, `row_height`, `lean`, `ivy*` | `foot_center_front`, `foot_left`, `foot_right`, `top_center_front` |
| `broken_floor_edge` | ART-0014 | `kind` edge/corner_left/corner_right, `thickness`, `chips` | tile corners |
| `side_wall_path` | candidate side walls | `path` (floor-edge vertices, y = −row), `inside` left/right, `height`, `lean`, palette (`stone_base/dark`, `cap_base/dark`, `mortar`, `specular`), `shadow_inside` (tiles of floor that receive the shadow), `ivy*` | `grid_origin` (floor cell 0,0 top-left) |
| `entrance_stairs` | ART-0025 | `steps`, `tread_width`, `run`, `rise`, `cheek_width`, `cheek_height`, `foundation` | `top_center` (middle of the floor front edge), `top_left`, `top_right` |
| `compass_inlay` | ART-0022 | `half_x`, `half_y` (half diagonals), `field`, `ring`, `long_point`, `short_point` | `center`, `north/south/east/west` |
| `terrain_tile` | candidate `hero_room_01_tileset` (TASK-0066) | `kind` floor/wall_top/wall_face/cliff_face/grass/sea/sea_foam, `seed`, `rows`, `row_offsets`, `row_shift`, `wear`, `moss`, `ivy`, `flowers`, stone colours | `tile_top_left` |
| `rope_fence` | ART-0024 | `posts` (feet relative to the first), `height`, `radius`, `sag`, `rope` | `foot`/`front_post_foot`, `back_post_foot` |

Colours are **linear RGB**. Golden limestone for v4 is `lib.GOLDEN_STONE` (0.66, 0.40, 0.14 / dark 0.33, 0.17, 0.05) with `specular` 0.2; the older (0.70, 0.49, 0.25) reads pale grey once converted to sRGB under the warm sun. Avoid fully metallic flat faces: in an orthographic view they mirror the dim world and read grey (`lib.gold` is mostly dielectric).

Adding a builder: write `def name(spec, facing) -> (objects, anchors)`, register it in `BUILDERS`, add a spec, then a Blender render test in `tools/tests/test_blender_factory.py` that checks size and anchors numerically. A builder may set `spec["shadow_region"]` (ground polygon in tiles) to limit where its shadow lands. Curves must be converted to meshes before framing (a curve's bound box is padded by a tile).

## 5. Spec format
```json
{
  "art_id": "ART-0024",            // or "candidate": "<candidate id>" for staged pieces
  "task": "TASK-0054",
  "builder": "rope_fence",
  "projection": {},                // optional overrides of projection.json
  "params": {},                    // shared by all outputs
  "palette_check": {"min_saturation": 0.3, "min_pixel_saturation": 0.35, "hue_deg": [15, 45]},
  "expected_similar": [{"pair": ["a", "b"], "reason": "why the look-alike is intended"}],
  "outputs": [{"name": "snake_case", "facing": "south", "shadow": true, "builder": "optional override",
               "params": {}}],     // per-output params override the shared ones
  "notes": "calibration source and decisions"
}
```
Map tiles (TASK-0066): `"tile": true` frames every output as exactly one cell (`params.tiles` [w, h], default 1x1), opaque, shadows baked in. `lib.periodic_material` (world position wrapped onto circles, 4D noise) and `lib.wrap_copies` (linked copies one tile away) make tiles continue across every edge; keep stone joints off the cell edges (`row_offsets`, `row_shift`). `"pixel_art": {"colors": N}` reduces all native PNGs to one shared palette without dithering (masters stay untouched); `"atlas": {"columns": N}` packs the tiles into `<id>_atlas.png` and records each file's `atlas_cell`. Per-output `"wrap": "x"` limits the seam check (e.g. foam at a cliff foot). QA for tiles: fully opaque, plus `seam_x`/`seam_y` (wrap-edge step / mean neighbour step, warning above `seam_limit`, default 2.5) in `manifest.json` `qa.seams`.
Output names must be unique snake_case; for ART specs `.agents/graphics/deliveries/<ART>/<name>.png` must equal the request's `output_paths` exactly.

## 6. Commands
```text
py -3 tools/blender_factory.py calibrate                       # 1x1 tile renders exactly 64x64
py -3 tools/blender_factory.py render <spec> --out <dir>       # raw masters + metadata (scratch)
py -3 tools/blender_factory.py deliver ART-0025                # spec -> .agents/graphics/deliveries/ART-0025/ + manifest.json
py -3 tools/blender_factory.py stage tools/blender/specs/candidates/hero_room_01_v4_side_walls.json --out map_factory/candidates/renders/hero_room_01_blender_v4
```
`deliver`/`stage` write the native PNG (4x master downscaled), `@4x` master, `_shadow.png`, and `manifest.json` with SHA-256, pixel size, anchors, params, palette stats (`mean_rgb`, `hue_deg`, `saturation`, `pixel_saturation`, `opaque_size`), QA problems/warnings and provenance. Exit code 1 = QA problems: change the builder/spec and re-run. Status is always `rendered_unreviewed`; neither command changes ART/TASK status, writes `map_factory/parts/` or approves art.

## 7. Candidate layout (`map_factory/candidates/<id>.json`)
```json
{"candidate_id": "hero_room_01_blender_v4", "base": {"map_id": "hero_room_01", "version": 11},
 "status": "candidate_unapproved",
 "hide_instances": ["EntryStairUpper"],            // base instances (and their shadows) hidden in the candidate capture
 "hide_floor_cells": [[3, 9]],                     // floor sprites replaced by ground pieces
 "refloor_cells": [[7, 4, 4, 4]],                  // cell 7,4 shows the plain tile of cell 4,4 (texture, scale, rotation)
 "pieces": [{"art": "ART-0025" | "source": "<staged render folder>", "file": "<output name>", "anchor": "<anchor>",
             "point": "top_left|left_center|right_center|center|bottom_center", "cells": [[x, y]],
             "offset_px": [dx, dy], "layer": "ground|walls|props"}]}
```
Position = map `ground_offset` + (cell + point) · 64 + `offset_px`; the piece's anchor pixel lands there. Layers: `ground` (z 11, above the floor), `walls` (z 30, candidate wall pass, under the furniture), `props` (inside the base `Level3_Decorations`, y-sorted with the furniture by the anchor's y — use for fences and free-standing pieces). Calibrated contacts come from `docs/HERO_ROOM_CALIBRATION.md` (64 px grid kept while decision D1 is open).

## 8. Capture and compare
```text
py -3 tools/candidate_room.py resolve map_factory/candidates/hero_room_01_blender_v4.json   # check placements, no Godot
py -3 tools/candidate_room.py capture map_factory/candidates/hero_room_01_blender_v4.json
```
Writes `docs/previews/candidates/<id>_base.png`, `_candidate.png`, `_compare.png` (reference | base | candidate) and `_metrics.json`: mean absolute RGB difference to the goal reference (lower is closer) for the whole image, per layer region and **per placed piece** (`pieces`). The reference contains characters and UI, so absolute numbers stay high. Compare pieces by their base→candidate delta, not across regions.

## 9. Iterate
1. Read the per-piece metrics and the manifest QA/palette numbers. The only image an agent may view is `<id>_compare.png`, when the owner's permission settings allow it.
2. Change the builder, spec params or layout (never the PNGs), then `deliver`/`stage` again and re-capture.
3. At most 3 rounds per task; then report the numbers honestly. Candidates stay `candidate_unapproved` until the owner approves the final capture. Nothing enters `map_factory/parts/` or the catalog before that.
4. Tests: `py -3 tools/run_tests.py --only blender_factory --only candidate_room` (the Blender render tests run only where Blender is installed).

## Hero Room history
| Candidate | Change | Whole-image diff (base → candidate) |
| --- | --- | --- |
| v1 (TASK-0047) | ART-0004 wall runs, ART-0014 edges | 74.68 → 74.71 |
| v2 (TASK-0048) | leaning side walls, warmer stone, ivy | 74.68 → 73.59 |
| v3 (TASK-0050) | continuous low ruined side walls | 74.68 → 74.23 |
| v4 (TASK-0054) | golden walls ending at row 7, floor-only wall shadows, ART-0025 stairs, ART-0022 inlay, ART-0024 fences | 74.72 → 73.89 |
