---
id: ART-0022
status: requested
owner: graphics-specialist
task: TASK-0038
dedupe_key: hero_room_compass_floor_inlay
existing_asset_ids: F014,O020
output_paths: .agents/graphics/deliveries/ART-0022/hero_compass_floor_inlay.png
---
# Oblique compass-rose floor inlay

**Why:** The source centre floor carries a single 45-degree rotated, obliquely foreshortened sapphire/gold compass rhombus (source 575,490-850,700; 275x210). v0011 uses nine 64px procedural square tiles F014-F022 and O020 is a top-down circle; neither matches projection or craftsmanship.

**Source image and SHA-256:** map_factory/references/hero_room_01_original.png (1448x1086), sha256 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7, verified 2026-10-27. Measurements: docs/HERO_ROOM_CALIBRATION.md (TASK-0038). Stays `blocked_reference` until the owner reviews these calibrated specs and decision D1 (floor depth).

**Outputs:** one independent RGBA PNG per listed path. Native display size = source px x 0.971 (uniform); ground-plane depth follows D1. Flat ground overlay, layer ground, no collision, origin = rhombus centre. Native 267x259 under the current floor depth, or 267x204 if D1 adopts the uniform scale. Rendered centre (733,613). Must sit on the flagstone joints without opaque square margins. Palette/style must match the accepted HD set (W021, W022, A017, A018, D019, P023-P026). Never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no baked cast shadow (separate *_shadow only if listed); procedural or low-detail drawing is not acceptable.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests (ART-0001..ART-0021) and deliveries (ART-0004, ART-0014).
- [x] Original reference path and hash attached.
- [x] Specifications reviewed by owner; mark `requested` (owner decision 2026-10-27, TASK-0054; D1 still open, 64x64 grid kept).

## Graphics specialist checklist
- [ ] All required clean PNGs produced.
- [ ] SHA-256 manifest written (pixel_size, origin, facing, footprint/mount/collision); mark `delivered`.

## QA checklist
- [ ] Independent visual review against the source at Godot native scale; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and map tested; PR merged; mark `integrated`.
