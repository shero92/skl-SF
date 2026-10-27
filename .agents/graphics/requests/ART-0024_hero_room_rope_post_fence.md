---
id: ART-0024
status: blocked_reference
owner: graphics-specialist
task: TASK-0038
dedupe_key: hero_room_rope_post_fence
existing_asset_ids: D017
output_paths: .agents/graphics/deliveries/ART-0024/hero_rope_post.png,.agents/graphics/deliveries/ART-0024/hero_rope_swag_west_rail.png,.agents/graphics/deliveries/ART-0024/hero_rope_swag_east_rail.png
---
# Wooden rope-and-post terrace fence

**Why:** The source has rope-linked wooden posts on both terrace edges (left 200,610-295,740; right 1210,620-1300,745). No post is registered; D017 is only a hanging rope.

**Source image and SHA-256:** map_factory/references/hero_room_01_original.png (1448x1086), sha256 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7, verified 2026-10-27. Measurements: docs/HERO_ROOM_CALIBRATION.md (TASK-0038). Stays `blocked_reference` until the owner reviews these calibrated specs and decision D1 (floor depth).

**Outputs:** one independent RGBA PNG per listed path. Native display size = source px x 0.971 (uniform); ground-plane depth follows D1. Post: source about 30x80 -> native 29x78, origin bottom-centre, collision about 20x12 at base. Rope swags join post tops: left run 92x126, right run 87x121 native (the posts stand on the edge line descending to the front). Layer front_objects; the rope has no collision. Palette/style must match the accepted HD set (W021, W022, A017, A018, D019, P023-P026). Never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no baked cast shadow (separate *_shadow only if listed); procedural or low-detail drawing is not acceptable.

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
