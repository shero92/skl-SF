---
id: ART-0025
status: blocked_reference
owner: graphics-specialist
task: TASK-0038
dedupe_key: hero_room_entrance_stairs
existing_asset_ids: ST001,ST002,ST003,ST006
output_paths: .agents/graphics/deliveries/ART-0025/hero_entrance_stairs_south.png
---
# Front entrance stairs (visible south view)

**Why:** ST001-ST006 are flat procedural step faces (catalog source original_procedural_or_derived_sprite) and render 12-30 percent too wide. The source stairs between the ball pedestals are carved limestone with worn edges.

**Source image and SHA-256:** map_factory/references/hero_room_01_original.png (1448x1086), sha256 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7, verified 2026-10-27. Measurements: docs/HERO_ROOM_CALIBRATION.md (TASK-0038). Stays `blocked_reference` until the owner reviews these calibrated specs and decision D1 (floor depth).

**Outputs:** one independent RGBA PNG per listed path. Native display size = source px x 0.971 (uniform); ground-plane depth follows D1. Measured visible part 650,795-810,880 (160x85) -> native 155x105 under the current depth (155x83 under D1-a); the lower steps are hidden by the source dialogue UI and stay deferred, so draw at least 3 visible steps and allow extension. Top edge meets the floor front edge (render y 865); cheeks join ST011 pedestals at x 602 and 893. Walkable via the navigation region; side cheeks block. Palette/style must match the accepted HD set (W021, W022, A017, A018, D019, P023-P026). Never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no baked cast shadow (separate *_shadow only if listed); procedural or low-detail drawing is not acceptable.

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
