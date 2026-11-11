---
id: ART-0040
status: requested
owner: graphics-specialist
task: TASK-0102
dedupe_key: hero_room_wall_lantern_east_pointing
existing_asset_ids: L06
output_paths: .agents/graphics/deliveries/ART-0040/hero_wall_lantern_east.png
---
# East-pointing brass wall lantern for the west wall

**Why:** ART-0023 delivered only the west-pointing lantern (`hero_wall_lantern_west`, part L06), used on the east wall since hero_room_01 v0024. The west wall still shows the old flat L01/L02 lanterns, so the two side walls do not match.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261110.webp`, sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`. Style reference: `assets_hd/lighting/` master of `hero_wall_lantern_west` (same brass, glass and bracket; do not edit or mirror-paste it).

**Outputs:** one independent RGBA PNG at the path above.
- Lantern hanging from a bracket fixed to a wall on its **left**, arm pointing east (the true counterpart of the west view, drawn with light from the upper left, not a flipped copy).
- On-canvas size about 29x53 px (master at least 400x720). Lit warm glass, no glow halo, wall, shadow or text. Origin = the bracket's wall mount point documented in the manifest.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale on the west wall; mark `reviewed`.

## Integration checklist
- [ ] Registered asset and map tested; PR merged; mark `integrated`.
