---
id: ART-0034
status: reviewed
owner: codex
task: TASK-0102
dedupe_key: hero_room_sea_stacks_and_arches
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0034/sea_stack_tall_a.png,.agents/graphics/deliveries/ART-0034/sea_stack_tall_b.png,.agents/graphics/deliveries/ART-0034/sea_stack_tall_c.png,.agents/graphics/deliveries/ART-0034/rock_arch_far_left.png,.agents/graphics/deliveries/ART-0034/rock_arch_far_right.png,.agents/graphics/deliveries/ART-0034/horizon_haze_strip.png,.agents/graphics/deliveries/ART-0034/foam_patch_a.png,.agents/graphics/deliveries/ART-0034/foam_patch_b.png
---
# Open sea backdrop pieces: sea stacks, rock arches, distant coast

**Why:** Current sea is flat tiled water with a hard horizon. Target y=0-360 shows bright azure water, foam, tall sea stacks, natural rock arches and sunlit clouds with soft horizon haze.

**Source image and SHA-256:** map_factory/references/hero_room_01_target_20261103.png (1536x1024), sha256 47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b. Review of the gaps: docs/HERO_ROOM_20261103_VISUAL_TARGET.md (section TASK-0102 review); side by side docs/previews/map_factory_renders/hero_room_01_v0014_vs_target.png.

**Outputs (one independent RGBA PNG each, transparent background):** sea_stack_tall_a/b/c, rock_arch_far_left, rock_arch_far_right, horizon_haze_strip, foam_patch_a/b (independent RGBA; water base itself stays an existing tile unless the owner asks for a new one).

**Style rules:** match assets_hd masters (pixel density, palette, outline, warm upper-left light); cite an assets_hd master as the style reference; no baked cast shadow; never mirror or rotate a bitmap to make another facing; never replace or repaint existing parts; no characters; no procedural placeholder art. Names are descriptive; catalog ids are assigned later.

## Request checklist
- [x] Duplicate scan against ART-0001..ART-0031 (none cover these pieces).
- [x] Reference path and hash attached.
- [ ] Owner reviews the specification; keep `requested` until then.

## Graphics specialist checklist
- [x] All required clean PNGs produced.
- [x] SHA-256 manifest written; review anchors measured, scene footprint/calibration explicitly pending.

## QA checklist
- [ ] Independent visual review at Godot native scale; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and room relayout (v0015) tested; PR merged; mark `integrated`.

## تفويض التنفيذ 2026-11-10

طلب المالك متابعة الرسوم المطلوبة بعد دمج الحزم المعتمدة. Agent: codex؛ الفرع codex/art-0034-0035-coast-plants. كل عنصر PNG مستقل عبر builtin_image_gen. لا تفعيل تلقائي للأصول الجديدة، ولا إعادة توليد لأساس الماء القائم.

تسليم الصور المستقلة ونسخ المراجعة والطلبات والبصمات ولقطة Godot فعلية اكتمل. الحالة needs_review، وتركيب الخريطة لم ينفذ.

اعتماد المالك الصريح 2026-11-10 مسجل؛ PR #136 دُمج عند c161727cae2ade773517680822c4b405f593b217. معايرة الخريطة لم تنفذ بعد.
