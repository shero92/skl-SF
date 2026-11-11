# ART-0021 — صندوق الدراسة: أربعة مناظير مستقلة

Agent: codex. Tool: built-in image_gen. Model/cost: unknown. Task: TASK-0032.

الحالة delivered / needs_review. أربع صور مستقلة لصندوق خشبي بني مغلق؛ لم يُستخدم عكس أو تدوير bitmap. جميع Masters كاملة دون تغيير نسب أو تكبير. لا اعتماد بصري ولا تكامل.

| الاتجاه | مسار Master | SHA-256 | الأبعاد |
|---|---|---|---|
| south | assets_hd/furniture/study_chest_views/v001/hero_study_chest_south.png | b846edba4585f76fa5df8803fb077b9d506a9e731f2e95692f834da46e436d2d | [1448, 1086] |
| north | assets_hd/furniture/study_chest_views/v001/hero_study_chest_north.png | 6827e5bddc01c34332475d70e060b4bbe5d3a9eab3b3d9999b587103f645b993 | [1536, 1024] |
| east | assets_hd/furniture/study_chest_views/v001/hero_study_chest_east.png | 9c811c843ec5b247c5947f151bc98fc9903e4b4542767a3033c98fe55641922a | [1448, 1086] |
| west | assets_hd/furniture/study_chest_views/v001/hero_study_chest_west.png | 8fb9271ba9d6434ce663eb9b3eb2a77259f6f3068881e8944b63cc37c733a839 | [1448, 1086] |

المعاينة الفعلية: godot_native_review.png وإيصال godot_review_receipt.json. تظهر58x73 و191x157 ونسخة2x؛ المقاسان اقتراحا معاينة وليسا إثباتًا لحجم الإدراج. تُحفظ النسب بملاءمة موحدة وNearest Neighbor. يفوق كل مصدر4x الدقة المطلوبة لكل مقاس معاينة.

المحاولة الغربية الأولى غير مختارة لأن شرائط الحديد امتدت إلى جسم الصندوق؛ صُححت إلى دعائم خشبية مع بقاء الحديد على الغطاء. المصدر المرفوض وطلبه وبصمته محفوظة تحت rejected وrequests.

نقاط المراجعة: ثبات العائلة العامة (غطاء مقوّس منخفض، شريطان، قفل أمامي، مفصلتان خلفيتان) واضح في المعاينة؛ يتغير عرق الخشب وبعض تفاصيل المسامير بين المناظير المستقلة. القياس الفيزيائي والتصادم وfootprint بوحدات64px يحتاج معايرة داخل المشهد. تبقى الحقول غير المقاسة null؛ لا يُستخدم كامل مربع الصورة كتصادم.

المصدر المرجعي: hero_room_01_target_20261110.webp بالبصمة4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323؛ للأسلوب والتكوين فقط دون قص أو لصق أو تتبع. مرجع الكثافة والخشب crate_01.png موثق ببصمته في generation_records.json. لم تتغير الأصول الحالية أو الخرائط أو Golden Cyclone.

إعادة المعاينة:
```powershell
python game_factory/environment/ART-0021/v001/prepare_review.py
$g=(Get-Content .agents/planner/config.json -Raw | ConvertFrom-Json).godot_executable
& $g --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0021/v001/review.gd
```

الفحوص: run_tests.py --changed --timeout120 نجح85/85. graphics_validation خرج0 وpng_checked0 لأن Masters المرشحة خارج نطاقه؛ الفحص المستقل تحقّق من المصادر الأربعة وثماني نسخ native. تفاصيل القياس والتحذيرات المحلية غير القاتلة في verification.json.
