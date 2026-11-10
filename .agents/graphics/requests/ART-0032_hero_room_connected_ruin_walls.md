---
id: ART-0032
status: delivered
owner: codex
task: TASK-0102
dedupe_key: hero_room_connected_ruin_walls
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0032/wall_straight_long_a.png,.agents/graphics/deliveries/ART-0032/wall_straight_long_b.png,.agents/graphics/deliveries/ART-0032/wall_corner_outer_left.png,.agents/graphics/deliveries/ART-0032/wall_corner_outer_right.png,.agents/graphics/deliveries/ART-0032/wall_corner_inner_left.png,.agents/graphics/deliveries/ART-0032/wall_corner_inner_right.png,.agents/graphics/deliveries/ART-0032/wall_side_left_run.png,.agents/graphics/deliveries/ART-0032/wall_side_right_run.png,.agents/graphics/deliveries/ART-0032/parapet_cap_run.png
---
# Connected broken limestone wall set (rear and sides)

**Why:** WL01-WL06 placeholders do not exist; current W01-W14 are single 64x128 blocks that read as separate columns. Target left x=100-640,y=130-700 and right x=965-1510,y=100-710 show continuous broken limestone walls with parapet tops, ivy and mounting points for banners and lanterns.

**Source image and SHA-256:** map_factory/references/hero_room_01_target_20261103.png (1536x1024), sha256 47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b. Review of the gaps: docs/HERO_ROOM_20261103_VISUAL_TARGET.md (section TASK-0102 review); side by side docs/previews/map_factory_renders/hero_room_01_v0014_vs_target.png.

**Outputs (one independent RGBA PNG each, transparent background):** wall_straight_long_a/b, wall_corner_outer_left/right, wall_corner_inner_left/right, wall_side_left/right_run, parapet_cap_run (each as independent RGBA tileable runs at 64-px grid multiples, native size = master/runtime scale in assets_hd/RULES.md).

**Style rules:** match assets_hd masters (pixel density, palette, outline, warm upper-left light); cite an assets_hd master as the style reference; no baked cast shadow; never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no characters; no procedural placeholder art. Names are descriptive; catalog ids are assigned later.

## Request checklist
- [x] Duplicate scan against ART-0001..ART-0031 (none cover these pieces).
- [x] Reference path and hash attached.
- [ ] Owner reviews the specification; keep `requested` until then.

## Graphics specialist checklist
- [x] All required clean PNGs produced.
- [x] SHA-256 manifest written; geometric origins measured, footprint proposed and map calibration explicitly pending.

## QA checklist
- [ ] Independent visual review at Godot native scale; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and room relayout (v0015) tested; PR merged; mark `integrated`.

## تفويض التنفيذ 2026-11-10

طلب المالك تنفيذ المهمة الرسومية التالية بعد قبول التسليمات السابقة. الإنتاج عبر builtin_image_gen؛ كل قطعة PNG مستقلة. لا تفعيل إنتاجي قبل مراجعة القطع الجديدة. المسار الأساسي assets_hd/architecture/connected_ruin_walls/v001؛ نسخ طلب التسليم في .agents/graphics/deliveries/ART-0032؛ البيانات والطلبات في game_factory/environment/ART-0032/v001.

تسليم: تسعة masters مستقلة وأربع محاولات محفوظة، ولقطة Godot فعلية للنسخ الصغيرة. دليل الاستخدام والبيانات: game_factory/environment/ART-0032/v001/README.md وmanifest.json. حالة الأصول needs_review؛ لم تعدل الخرائط أو السجل النشط.
