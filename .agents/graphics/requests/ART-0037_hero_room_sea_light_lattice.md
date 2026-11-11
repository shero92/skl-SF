---
id: ART-0037
status: requested
owner: graphics-specialist
task: TASK-0102
dedupe_key: hero_room_sea_light_lattice_overlay
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0037/sea_light_lattice_tile.png
---
# Seamless sea light-lattice overlay

**Why:** The owner target shows the whole sea covered by a loose lattice of fine white and pale-cyan glint lines with soft sparkle nodes (visible between the sea stacks and around the island). hero_room_01 v0021 shows flat azure water tiles only. No existing request covers a water-surface overlay (ART-0003 is the cliff-base foam loop, ART-0034 the rocks and arches).

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261110.webp`, sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323` (same design as `hero_room_01_target_20261103.png`). Style references: `assets_hd/background/sea/sea_01.png`, `assets_hd/background/wave_foam/wave_foam_01.png`.

**Outputs:** one independent RGBA PNG at the path above.
- Master 2048x2048, transparent background, **seamless on both axes** (left edge continues into right edge, top into bottom; verify by tiling 2x2).
- Content: thin (1-2 px at the 512 px on-canvas size) white and pale-cyan lines forming an irregular square-ish lattice, a few brighter sparkle nodes at crossings, alpha between 0 and about 70 percent so it reads as light on water, never as a solid texture.
- No land, rocks, foam clumps, text, solid fill or visible tile seam; no baked shadow.
- On-canvas use: tile of 512x512 px repeated over the ocean layer, additive or normal blend (Claude decides at integration).

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale (tiled 2x2, over the real ocean); mark `reviewed`.

## Integration checklist
- [ ] Registered asset and map tested; PR merged; mark `integrated`.

## B3 unsuccessful attempts — TASK-0016
- Two independent image_gen outputs retained under `assets_hd/background/sea_light_lattice/v001/rejected/` and `.agents/graphics/deliveries/ART-0037/rejected/`.
- Neither satisfies2048x2048 /4x512 or max-alpha178. First output also has no alpha0 gaps. No delivered production PNG; status remains requested, quality needs_regeneration.
- Technical manifest and actual Godot2x2 captures: game_factory/environment/ART-0037/v001/. No procedural substitute, upscaling or external service used.
