---
id: ART-0038
status: delivered
owner: graphics-specialist
task: TASK-0102
dedupe_key: hero_room_rear_left_window_wall_piece
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0038/wall_straight_window_opening.png
---
# Straight ruined wall run with a window opening

**Why:** The owner target has a small rectangular window opening in the rear-left wall (canvas about x 240-285, y 165-215) through which the sea is visible, with a potted flower on the sill. ART-0032 delivered nine connected wall pieces, none with an opening, and no request covers one.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261110.webp`, sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`. Style and footprint reference: `assets_hd/architecture/connected_ruin_walls/v001/wall_straight_long_a.png` (do not edit it).

**Outputs:** one independent RGBA PNG at the path above.
- Same limestone, mortar lines, ivy and white flowers, lighting (upper left) and perspective as `wall_straight_long_a`; same on-canvas footprint 320x190 px (master at least 1280x760, about 4x).
- A rectangular opening about 60x75 px on canvas with a thin stone sill and a small stone lintel; the opening is **truly transparent** (the sea behind must show through).
- Top edge irregular and broken like the other run pieces; both ends cut cleanly so the piece joins `wall_straight_long_a/b` and the corner pieces.
- No glass, curtain, interior, plant on the sill (the potted flower is a separate prop), baked shadow, ground or text.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale, joined to neighbouring wall pieces; mark `reviewed`.

## Integration checklist
- [ ] Registered asset and map tested; PR merged; mark `integrated`.

## B3 delivery — TASK-0016
- Owner explicitly assigned generation against authenticated target SHA-256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`.
- Exact outputs and independent source hashes in `.agents/graphics/deliveries/ART-0038/manifest.json`; native review and actual Godot captures in `game_factory/environment/ART-0038/v001`.
- Delivered candidates only. No owner approval, integration or map edits. See batch_B3_20261110/README.md for measured limitations.
- Primary v001 opening approximately58x76; neighboring low wall join requires calibration. Low-profile alternative v002 is retained separately and needs regeneration (opening65.41x52.82 instead60x75).
