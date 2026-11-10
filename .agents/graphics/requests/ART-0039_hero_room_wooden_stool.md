---
id: ART-0039
status: delivered
owner: graphics-specialist
task: TASK-0102
dedupe_key: hero_room_study_wooden_stool
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0039/study_wooden_stool.png
---
# Small wooden stool for the study table

**Why:** In the owner target a small round-seat wooden stool stands in front of the study table (canvas about x 835-860 in the 1125 px reference, which is about x 1140-1175, y 585-655 on the 1536x1024 canvas) next to two benches. The benches exist (`assets_hd/furniture/bench_plain`, `bench_blue_runner`) but no stool does, and ART-0019 covers only the table.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261110.webp`, sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`. Style reference: `assets_hd/furniture/bench_plain/bench_plain_01.png` (same oak, same plank and outline treatment; do not edit it).

**Outputs:** one independent RGBA PNG at the path above.
- South-facing three-quarter view, on-canvas size about 36x40 px (master at least 500x560).
- Round or slightly rounded seat of warm oak with visible grain and a lighter top face, three visible turned legs with a cross-rail, same palette and outline weight as the bench masters, light from the upper left.
- No cushion, floor, shadow, other furniture or text. Origin = bottom centre of the visible pixels.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale next to the benches and table; mark `reviewed`.

## Integration checklist
- [ ] Registered asset and map tested; PR merged; mark `integrated`.

## B1 owner target delivery (TASK-0030)
- Owner explicitly assigned production against `map_factory/references/hero_room_01_target_20261110.webp`, SHA-256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`; supersedes older blocked reference/native proposals for this candidate.
- Independent sources and exact delivery filenames: `.agents/graphics/deliveries/ART-0039/manifest.json`.
- Actual native review and Godot capture: `game_factory/environment/ART-0039/v001/`.
- Status delivered means candidate files supplied, not visual approval or complete spec compliance. Actual output size shortfalls and margins are recorded in the manifest. No source upscaling. Footprint/collider and scene calibration remain integration work.
- Owner review pending; Claude integrates after review. No map/catalog or earlier asset was changed.
