# ART-0015 — سجاد الدراسة وغرفة النوم

Agent: codex. Tool: built-in image_gen. Model/cost: unknown. Task: TASK-0026.

صورتان مستقلتان بمنظور أرضي مائل، دون تدوير أو عكس أو مطّ لصور Masters القديمة. الحالة delivered / needs_review، بلا اعتماد أو تكامل.

| الأصل | مسار Master | SHA-256 | الأبعاد | نسبة العرض/العمق المرئية |
|---|---|---|---|---|
| hero_study_blue_rug | assets_hd/decor/hero_room_rugs/v001/hero_study_blue_rug.png | 69b47dfad679193f9018eee2187f3c497577fc2fd3a6371f6d8abe70e8d56a79 | [1717, 916] | 2.529 |
| hero_bedroom_blue_rug | assets_hd/decor/hero_room_rugs/v001/hero_bedroom_blue_rug.png | 922ab1d65c73a7974d6b77d4f21619fc83053013a094cdc288614f5c76849c9a | [1457, 1080] | 1.668 |

المعاينة الفعلية: godot_native_review.png؛ نسخة1x و2x. يحفظ Nearest Neighbor والقياس الموحد النسب الأصلية. كل مصدر يتجاوز4x دقة عرضه الفعلية. لا دليل اعتماد بصري من الفحص العددي.

أربع محاولات غير مختارة محفوظة في rejected مع طلباتها وبصماتها: المحاولتان الأوليان شديدتا التقصير المنظوري، والثانيتان تحسن فيهما العمق مع بقاء اختلاف عن النسبة المقترحة. المصادر المختارة تنسج الزخرفة مسطحة دون بروز معدني ظاهر، وتبقي الزوايا كاملة.

المتبقي: قرار عمق الأرضية D1 لم يُحسم في الطلب. الأبعاد الحالية311x160 و304x225، والبديل D1-a311x126 و304x178، موثقة كاقتراحات. الرسوم أقرب إلى نسب D1-a؛ لا تدعي مطابقة أبعاد الفرع الآخر. لا نغير عمق الخريطة ولا نمد الصورة لإخفاء الفرق. القياس والإسقاط والإدراج وfootprint بوحدات64px يحتاج معايرة Claude ومراجعة المالك. السجاد بلا تصادم أو ظل مستقل.

المصادر المرجعية الحالية محفوظة ببصماتها في manifest وgeneration_records؛ صورة الهدف استُخدمت للأسلوب والتكوين فقط دون قص أو لصق أو تتبع. لم تُمس الأصول القديمة أو الخرائط أو Golden Cyclone.

إعادة المعاينة:
```powershell
python game_factory/environment/ART-0015/v001/prepare_review.py
$g=(Get-Content .agents/planner/config.json -Raw | ConvertFrom-Json).godot_executable
& $g --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0015/v001/review.gd
```

الفحوص: run_tests.py --changed --timeout120 نجح85/85. graphics_validation خرج0 وpng_checked0 لأن المصادر المرشحة خارج نطاقه؛ الفحص المستقل يتحقق من المصدرين والشفافية والبصمات وحدود الرسم ودقة4x.
