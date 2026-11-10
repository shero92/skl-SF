---
id: ART-0029
status: in_progress
owner: codex
task: TASK-0074
dedupe_key: char001_hero_golden_cyclone_individual_body_v001
existing_asset_ids: CHAR001,WPN_HERO_BASIC_SWORD,WPN_IRON_SWORD
output_paths: assets/characters/hero/battle/golden_cyclone/v001/source_frames
---
# 22 مصدرًا مستقلًا لـGolden Cyclone

لا طلب سابق لـGolden Cyclone بين ART-0001..0026؛ ART-0026 للـPhantom Dash المرفوض كمصدر متعدد الوضعيات. لا إعادة توليد لمصادر TASK-0070 المستقلة عالية الجودة دون عيب مثبت.

اتبع docs/GRAPHICS_PRODUCTION_POLICY.md؛ المراجع الأصلية وبصماتها موثقة هناك. كل إطار طلب image_gen مستقل، واحد كامل بلا سلاح أو مؤثر أو ظل. مصدر مفصل 1024px أو أعلى إذا دعمته الأداة، دون فرضه على فئات الأصول الأخرى.

المراحل والحركة في TASK-0074. مصادر محفوظة في assets/characters/hero/battle/golden_cyclone/v001/source_frames وH:/shining force/pixel-art/TASK-0074/ART-0029/v001/source_frames. الجسم والـVFX منفصلان؛ لا نشر تلقائي إلى active manifest. المجهول من anchors null حتى القياس والتحقق؛ needs_review ليس اعتمادًا.

تحديث 2026-11-09: حزمة المرشحات مكتملة في مساراتها المخصصة، 22 مصدر جسم و6 مؤثرات، مع manifest وmetadata وطلبات أصلية وGIF فعلي من Godot. دليل التشغيل والقيود في game_factory/golden_cyclone/v001/README.md؛ الحالة needs_review وليست approved، والاعتماد البصري لدى المالك.

## اعتماد المالك 2026-11-10

وافق المالك على جميع أصول حزمة Golden Cyclone المسلمة وعلى الدمج. owner_approved=true في manifest؛ أوصاف needs_review السابقة توثق حالة التسليم وقت إنتاجه. الموافقة تخص الأصول المسلمة، ولا تشمل المحاولات المرفوضة أو ملفات غير مولدة. ربط هجوم الإنتاج في TASK-0087 منفصل ولم يُدّع اكتماله.
