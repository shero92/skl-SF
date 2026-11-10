---
id: TASK-0074
status: done
owner: codex
agent: codex
branch: codex/golden-cyclone-resume
depends_on: none
issue: none
art_request: ART-0029
touches: AGENTS.md,docs/GRAPHICS_PRODUCTION_POLICY.md,docs/ASSET_QUALITY_POLICY.md,docs/HERO_ATTACK_SOURCE_AUDIT.md,game_factory/README.md,game_factory/hero_correction/README.md,game_factory/weapons/README.md,map_factory/MAP_FACTORY_RULES.md,game_factory/golden_cyclone,assets/characters/hero/battle/golden_cyclone,.agents/tasks/TASK-0074_golden_cyclone_individual_frames.md,.agents/graphics/requests/ART-0029_golden_cyclone.md,tools/golden_cyclone_assets.py,tools/tests/test_golden_cyclone_assets.py,tools/verify_golden_cyclone_preview.gd,scenes/battle/golden_cyclone_preview.gd,scenes/battle/golden_cyclone_preview.tscn,scenes/battle/battle_animation_controller.gd,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: 22 مصادر جسم مستقلة مطابقة للهوية ومؤثرات منفصلة وبيانات صادقة؛ الاعتماد والتكامل والتصدير النهائي لا يدعيان دون تحقق فعلي.
scope_approval: owner explicit scope expansion 2026-11-01/02 (Game Factory characters, weapons, factory output roots)
---
# Golden Cyclone وسياسة الإطار المستقل

تفويض المالك الصريح بتاريخ 2026-11-01: سياسة دائمة موحدة، تدقيق المصادر السابقة، ثم 22 إطارًا مستقلًا متتابعًا عبر image_gen المدمج. يقرأ كل إطار ويُفحص قبل توليد التالي. لا collage ولا تقطيع مصدر sheet ولا مصادر منخفضة التفاصيل. تحفظ الأصول السابقة والمراجع المقفلة.

تحديث الاستئناف 2026-11-09: سياسة المالك 2026-11-02 وطلب «continue» يجيزان لـCodex تنفيذ أدوات فحص/محاذاة/تصدير هذه الأصول ومشهد معاينتها واختباراته. لا Aider أو Claude أو Gemini أو API صور خارجي في هذه المهمة. الإطارات تبقى needs_review ولا يفعل سجل الإنتاج قبل الموافقة. استؤنف العمل من main عند 036e4bad، مع حفظ worktree السابق. TASK-0087 يبقى محظورًا لاعتماد فن الإنتاج؛ لا تعديل لملفاته أو الادعاء بإتمامه. الإضافات ضمن هذه المهمة هي أدوات المرشحات ومشهد مراجعة مستقل يستخدم مكونات battle الحالية.

نطاق الاستئناف الإضافي: tools/golden_cyclone_assets.py، tools/tests/test_golden_cyclone_assets.py، tools/verify_golden_cyclone_preview.gd، scenes/battle/golden_cyclone_preview.gd و.tscn، وإدخال اختبار واحد في tools/test_map.json. لا تعديل main أو ModularBattleCharacter أو حساب الضرر أو ملفات TASK-0087.

المراحل: 001–004 anticipation؛ 005–008 buildup؛ 009–014 full spin؛ 015–018 strike؛ 019–022 recovery. البداية والنهاية HERO_REAR_3Q؛ دوران الجسم اتجاهي مرسوم مستقلًا، واليد اليمنى خالية والذراع اليسرى تحمل العلامة الزرقاء.

المراجع والبصمات في docs/GRAPHICS_PRODUCTION_POLICY.md. كل مصدر محفوظ كذلك في H:/shining force/pixel-art/TASK-0074/ART-0029/v001/.

الحالة: حزمة المرشحات مكتملة ومختبرة في مشهد Godot مستقل؛ اعتماد المالك والتكامل الإنتاجي معلقان. التالي: مراجعة الهوية واستمرارية الحركة وحجب اليد.

## تسليم المرشحات 2026-11-09

اكتملت 22 PNG جسم مستقلة و6 VFX مع مشتقات اللعبة والارتكاز والتوقيت والفهرس والطلبات، وGIFين من Godot الفعلي. فحص أدوات التصدير والمشهد 8/8؛ السيفان 44 حالة إطار. دليل الاستخدام game_factory/golden_cyclone/v001/README.md ونتائج الفحص qa/verification_summary.md. كل الأصل الجديد needs_review ولا تفعيل تلقائي. التالي مراجعة المالك للحركة والهوية واليد ثم تحديد تصحيحات الإصدار.

فحص التغييرات الشامل: 53/54 أولًا؛ أصلح newline صريح في أداة المهمة، ثم نجح lf_writers وgolden_cyclone_assets مجددًا 2/2. جميع المجموعات الـ54 اجتازت عبر التشغيلين. الفرع مخصص لتسليم مرشح للمراجعة؛ لا merge أو push إلى main. الصور وبياناتها منسوخة كذلك إلى جذر المشروع دون تفعيل. التكلفة والاستهلاك غير المقاسين unknown في إيصال المهمة.

اعتماد المالك 2026-11-10؛ دُمج PR #120 عند 118e43db8dc4c9b2722dcfbf74d083af7daee511. اكتمل تسليم الرسوم؛ TASK-0087 مسؤول عن تكامل الإنتاج.
