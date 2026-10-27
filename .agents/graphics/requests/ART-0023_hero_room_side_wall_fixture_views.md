---
id: ART-0023
status: blocked_reference
owner: graphics-specialist
task: TASK-0038
dedupe_key: hero_room_side_wall_fixture_views
existing_asset_ids: D001,D004,D009,W015
output_paths: .agents/graphics/deliveries/ART-0023/hero_side_banner_east_facing_short.png,.agents/graphics/deliveries/ART-0023/hero_side_banner_east_facing_long.png,.agents/graphics/deliveries/ART-0023/hero_side_banner_west_facing_long.png,.agents/graphics/deliveries/ART-0023/hero_wall_lantern_west.png
---
# Side-wall banner and west-pointing lantern views

**Why:** The source side-wall banners are foreshortened side views (aspect 0.19-0.31); D001/D004 are front views (aspect 0.55-0.59), so scaling gives width ratios of 1.76-3.52. The right side-wall lantern points west; D008/D009 brackets point east.

**Source image and SHA-256:** map_factory/references/hero_room_01_original.png (1448x1086), sha256 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7, verified 2026-10-27. Measurements: docs/HERO_ROOM_CALIBRATION.md (TASK-0038). Stays `blocked_reference` until the owner reviews these calibrated specs and decision D1 (floor depth).

**Outputs:** one independent RGBA PNG per listed path. Native display size = source px x 0.971 (uniform); ground-plane depth follows D1. Measured source boxes: left back corner banner 28x95 and left side-wall banner 32x170 (east_facing_short native 27x92, east_facing_long native 31x165, also used for the lower-left banner 50x200 -> 49x194 at scale); lower-right banner 55x180 (west_facing_long native 53x175); right lantern 30x55 (native 29x53). Mount anchor = top rod/bracket centre on the host wall face; no collision; layer decorations. Palette/style must match the accepted HD set (W021, W022, A017, A018, D019, P023-P026). Never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no baked cast shadow (separate *_shadow only if listed); procedural or low-detail drawing is not acceptable.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests (ART-0001..ART-0021) and deliveries (ART-0004, ART-0014).
- [x] Original reference path and hash attached.
- [ ] Specifications reviewed by owner; mark `requested`.

## Graphics specialist checklist
- [ ] All required clean PNGs produced.
- [ ] SHA-256 manifest written (pixel_size, origin, facing, footprint/mount/collision); mark `delivered`.

## QA checklist
- [ ] Independent visual review against the source at Godot native scale; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and map tested; PR merged; mark `integrated`.
