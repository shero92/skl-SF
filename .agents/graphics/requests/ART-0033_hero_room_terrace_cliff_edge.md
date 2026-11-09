---
id: ART-0033
status: requested
owner: graphics-specialist
task: TASK-0102
dedupe_key: hero_room_terrace_cliff_edge
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0033/terrace_edge_straight.png,.agents/graphics/deliveries/ART-0033/terrace_edge_corner_left.png,.agents/graphics/deliveries/ART-0033/terrace_edge_corner_right.png,.agents/graphics/deliveries/ART-0033/cliff_face_front_a.png,.agents/graphics/deliveries/ART-0033/cliff_face_front_b.png,.agents/graphics/deliveries/ART-0033/cliff_face_front_c.png,.agents/graphics/deliveries/ART-0033/cliff_rubble_cluster.png,.agents/graphics/deliveries/ART-0033/foam_at_cliff_base.png
---
# Irregular terrace perimeter and cliff depth

**Why:** Current floor is a clean rectangle on flat water. Target main floor x=190-1390,y=315-800 has an irregular sandstone terrace edge, and x=90-1460,y=640-950 shows layered cliff rock, rubble and foam below the front perimeter.

**Source image and SHA-256:** map_factory/references/hero_room_01_target_20261103.png (1536x1024), sha256 47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b. Review of the gaps: docs/HERO_ROOM_20261103_VISUAL_TARGET.md (section TASK-0102 review); side by side docs/previews/map_factory_renders/hero_room_01_v0014_vs_target.png.

**Outputs (one independent RGBA PNG each, transparent background):** terrace_edge_straight, terrace_edge_corner_left/right, cliff_face_front_a/b/c, cliff_rubble_cluster, foam_at_cliff_base (independent RGBA, no baked cast shadow).

**Style rules:** match assets_hd masters (pixel density, palette, outline, warm upper-left light); cite an assets_hd master as the style reference; no baked cast shadow; never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no characters; no procedural placeholder art. Names are descriptive; catalog ids are assigned later.

## Request checklist
- [x] Duplicate scan against ART-0001..ART-0031 (none cover these pieces).
- [x] Reference path and hash attached.
- [ ] Owner reviews the specification; keep `requested` until then.

## Graphics specialist checklist
- [ ] All required clean PNGs produced.
- [ ] SHA-256 manifest written (pixel_size, origin, facing, footprint); mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and room relayout (v0015) tested; PR merged; mark `integrated`.
