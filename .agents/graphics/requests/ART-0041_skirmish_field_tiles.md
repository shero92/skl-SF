---
id: ART-0041
status: requested
owner: graphics-specialist
task: TASK-0147
dedupe_key: skirmish_field_tiles_and_markers
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0041/field_grass_a.png, .agents/graphics/deliveries/ART-0041/field_grass_b.png, .agents/graphics/deliveries/ART-0041/field_rock_block.png, .agents/graphics/deliveries/ART-0041/marker_move.png, .agents/graphics/deliveries/ART-0041/marker_target.png, .agents/graphics/deliveries/ART-0041/marker_active.png
---
# Skirmish field tiles and cell markers

**Why:** The playable skirmish (`scenes/battle/tactical_battle.tscn`, TASK-0147) draws its 10x7 field, rocks and move/target highlights as plain coloured shapes because no battle-field art exists. Unit sprites are not part of this request: they come from the six-character production request.

**Source image and SHA-256:** style only, `map_factory/references/hero_room_01_target_20261110.webp`, sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323` (same limestone, foliage and outline density; no crop or paste).

**Outputs:** six independent RGBA PNGs at the paths above, top-down three-quarter view, light from the upper left.
- `field_grass_a`, `field_grass_b`: seamless 64x64 grass/earth floor tiles (masters at least 512x512) that tile with each other in a checker pattern without visible seams.
- `field_rock_block`: an impassable limestone boulder that fills one 64x64 cell and may rise to 64x96 (master at least 512x768), origin bottom centre.
- `marker_move` (blue), `marker_target` (red), `marker_active` (gold ring): 64x64 translucent cell overlays with a clean 2 px inner border, readable over both grass tiles.
- No text, units, shadows baked outside the cell, or water.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNGs produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale inside the skirmish scene; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and scene tested; PR merged; mark `integrated`.
