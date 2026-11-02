---
id: ART-0026
status: needs_regeneration
owner: codex
task: TASK-0072
dedupe_key: CHAR001_phantom_dash_rear_body_v001
existing_asset_ids: CHAR001,WPN_HERO_BASIC_SWORD,WPN_IRON_SWORD
output_paths: game_factory/hero_attack_style/v001/phantom_dash_body_source.png
---
# phantom_dash: رسوم الجسم الخلفية المائلة

## قرار المالك 2026-11-01 — مرفوض كمصدر إنتاجي

المصدر المولد متعدد الوضعيات محفوظ للتاريخ فقط، ولا يستخرج منه أي إطار إنتاجي. حالته needs_regeneration. المصدر الفعلي 1254×1254، SHA-256 3784bdc287f928981eaf17d26565bf4ec81b82c36e413cbc6bcb27d9e8599da3. المواصفات القديمة أدناه أصبحت وصفًا تاريخيًا ملغى؛ السياسة الملزمة docs/GRAPHICS_PRODUCTION_POLICY.md في TASK-0074 والجذر. طابور الإصلاح في game_factory/golden_cyclone/v001/regeneration_queue.json على فرع codex/golden-cyclone.

لا توجد طلبات ART سابقة للهجومين phantom_dash أو skybreaker_combo في قائمة ART-0001..0025. رسوم TASK-0070 الحالية مرجع هوية وبداية تقنية، وليست رسوم المنظور الخلفي الجديد.

المراجع الأصلية المعتمدة للتصميم واللون:
- assets/characters/hero/battle/idle_ready/sources/hero_battle_idle_ready_01__attempt_01.png — SHA-256 95e7246dcd2370db7704854ccac033563c4b109cc4d209d1a6648f7b0d99f098.
- assets/characters/hero/battle/step/sources/hero_battle_step_01__attempt_01.png — SHA-256 f3fc5ef8e888f384410b19bb30b85fcc4c12fdc2805b7988273df30675edc2e9.

المخرج المستهدف: Sprite Sheet شفافة 4×4، ست عشرة وضعية مستقلة مرتبة زمنيًا، جسم كامل بمنظور خلفي مائل نحو أعلى اليسار؛ لا سيف ولا مؤثر ولا ظل مدمج. يتولى Aider أداة استخراج الخلايا وفحص alpha والحدود والمقياس والارتكاز، ولا يعتبر الناتج جاهزًا آليًا إذا انحرفت الخلايا أو الهوية.

المرجع المكاني لكل خلية: 256×256، ارتكاز الأرض [128,240] ومقياس جسم ثابت. يجب قياس القيم الفعلية بعد التوليد؛ الأرقام المطلوبة ليست إثباتًا على تحققها. لا إعادة تحجيم مستقلة لكل وضعية لتغطية اختلافات الرسم.

التسلسل: استعداد، تحميل، دفع، اندفاع، غرس قدم، لف الجذع، ضربة قطرية، نهاية ضربة، متابعة، استقرار، تراجع خطوتين، استعداد. اللحظة 430 ms هي الاصطدام؛ توقف 50 ms؛ الزمن الكلي 1050 ms.

المصدر الدائم: H:/shining force/pixel-art/TASK-0072/ART-0026/v001/.
الحالة needs_review حتى فحص Godot وموافقة المالك. لا اعتماد ذاتي.
