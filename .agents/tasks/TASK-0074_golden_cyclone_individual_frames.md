---
id: TASK-0074
status: in_progress
owner: codex
agent: codex
branch: codex/golden-cyclone
depends_on: none
issue: none
art_request: ART-0027
touches: AGENTS.md,docs/GRAPHICS_PRODUCTION_POLICY.md,docs/ASSET_QUALITY_POLICY.md,docs/HERO_ATTACK_SOURCE_AUDIT.md,game_factory/README.md,game_factory/hero_correction/README.md,game_factory/weapons/README.md,map_factory/MAP_FACTORY_RULES.md,game_factory/golden_cyclone,assets/characters/hero/battle/golden_cyclone,.agents/tasks/TASK-0074_golden_cyclone_individual_frames.md,.agents/graphics/requests/ART-0027_golden_cyclone.md
test: python tools/run_tests.py --changed
done_when: 22 مصادر جسم مستقلة مطابقة للهوية ومؤثرات منفصلة وبيانات صادقة؛ الاعتماد والتكامل والتصدير النهائي لا يدعيان دون تحقق فعلي.
---
# Golden Cyclone وسياسة الإطار المستقل

تفويض المالك الصريح بتاريخ 2026-11-01: سياسة دائمة موحدة، تدقيق المصادر السابقة، ثم 22 إطارًا مستقلًا متتابعًا عبر image_gen المدمج. يقرأ كل إطار ويُفحص قبل توليد التالي. لا collage ولا تقطيع مصدر sheet ولا مصادر منخفضة التفاصيل. تحفظ الأصول السابقة والمراجع المقفلة.

Codex لا يكتب كودًا أو سكربتات أو اختبارات أو إعدادات أتمتة. لا Aider أو Claude أو Gemini أو API صور خارجي. شروط التكامل التي تتطلب أدوات جديدة تسجل معلقة ولا تُختلق نتائجها.

المراحل: 001–004 anticipation؛ 005–008 buildup؛ 009–014 full spin؛ 015–018 strike؛ 019–022 recovery. البداية والنهاية HERO_REAR_3Q؛ دوران الجسم اتجاهي مرسوم مستقلًا، واليد اليمنى خالية والذراع اليسرى تحمل العلامة الزرقاء.

المراجع والبصمات في docs/GRAPHICS_PRODUCTION_POLICY.md. كل مصدر محفوظ كذلك في H:/shining force/pixel-art/TASK-0074/ART-0027/v001/.

الحالة: قيد الإنتاج؛ لا اعتماد بصري ولا تشغيل Godot للحركة الجديدة. التالي: تثبيت السياسة وتدقيق المصدر ثم إنتاج 001 وفحصه.
