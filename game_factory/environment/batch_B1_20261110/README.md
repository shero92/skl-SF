# B1 — تسليم مصادر غرفة البطل

Agent: codex. Tool: built-in image_gen. Model/usage/cost: unknown.

الدفعة تحتوي سبعة مصادر مستقلة. جميعها RGBA حقيقية وتتجاوز 4x حجم العرض المقترح، لكنها لا تستوفي كل حدود الأبعاد المطلقة في المواصفة؛ لا يوجد تكبير اصطناعي. الحالة delivered / needs_review، ولا يوجد اعتماد بصري أو تكامل.

| الأصل | مسار Master | SHA-256 | الفعلي | الحد المكتوب |
|---|---|---|---|---|
| hero_study_table_south | assets_hd/furniture/study_table_views/v001/hero_study_table_south.png | 1b3ea8a1ee93dcbb6d01747ec70462f0664422e32b23b37a68badb7a0cbb6ff3 | [1448, 1086] | [1450, 1080] |
| hero_study_table_north | assets_hd/furniture/study_table_views/v001/hero_study_table_north.png | 15c67a248c310c1feb3754eeebb0572e3152090d9c1f94ea71be3202f86fedbc | [1448, 1086] | [1450, 1080] |
| hero_study_table_east | assets_hd/furniture/study_table_views/v001/hero_study_table_east.png | 36c47434340e3f1cd52c78e074907b30aff653596b08e784a6479ce33ca00b7b | [1448, 1086] | [1450, 1080] |
| hero_study_table_west | assets_hd/furniture/study_table_views/v001/hero_study_table_west.png | a33878c952c3dcb9790cbbc6a69c34c47bfd2b10e201730bb4591f79affa0acb | [1448, 1086] | [1450, 1080] |
| study_wooden_stool | assets_hd/furniture/study_stool/v001/study_wooden_stool.png | 4d0b2936583ff4abd81cf57ae2648d7d186f98701e2da72cb67a09d93bf9b86f | [1190, 1322] | [500, 560] |
| hero_blue_white_planter | assets_hd/plants/blue_white_planter/v001/hero_blue_white_planter.png | 7a4194588eaada83f4e210d6d76701cf2c6c6ab65bc6ea200b1955923f9f2a6d | [948, 1659] | [1100, 1300] |
| hero_entrance_stairs_south | assets_hd/architecture/entrance_stairs/v001/hero_entrance_stairs_south.png | 1ad183f2a4054081d747003c1c377bd0557a1d50f83fa56953c2a88949881adc | [1320, 1192] | [2200, 1960] |

المرفوض: محاولة الطاولة الجنوبية الأولى بسبب خلفية فاتحة شبه شفافة؛ محاولة النبتة الأولى بسبب ضيق هوامش الأوراق. المحاولتان محفوظتان في rejected مع بصماتهما. نسخة السلم السابقة محفوظة حرفيًا مع manifest في `.agents/graphics/deliveries/ART-0025/archive_pre_B1_20261110/`.

المتعذر/المؤجل: تحقيق كل أبعاد Master المطلقة عبر خرج الأداة الحالي؛ معايرة footprint بوحدات 64px ونقاط السلم والتصادم داخل المشهد؛ مراجعة المالك؛ تكامل Claude. لا يُستخدم null كدليل جاهزية.

المرجع WEBP تحقق ببصمته المطلوبة. قورنت لقطة v0021 الموجودة محليًا في نسخة ci-regen2؛ لم تُقص أو تُلصق أو تُتبع أي بكسلات من المرجع.

إعادة المعاينة:
```powershell
python game_factory/environment/batch_B1_20261110/prepare_review.py
$g=(Get-Content .agents/planner/config.json -Raw | ConvertFrom-Json).godot_executable
foreach ($art in @('ART-0019','ART-0039','ART-0011','ART-0025')) { & $g --path . --rendering-method gl_compatibility --script res://game_factory/environment/batch_B1_20261110/review.gd -- "--art=$art" }
```

المعاينات تستخدم Nearest Neighbor وملاءمة موحدة لحدود ألفا غير الصفرية، وتحفظ كل بكسل مرئي. توجد لقطة Godot أصلية وإيصال بصمات تحت مجلد كل ART. تحذيرات user log وshader cache في بيئة العزل لم تمنع التقاط viewport.

`graphics_validation.py --changed`: exit 0، png_checked=0 لأن Masters المرشحة خارج نطاق إنتاج الأداة. الفحص المستقل في technical_qa.json يغطي المصادر السبعة، ولا يمثل اعتمادًا فنيًا.

الفحوص: الجولة الأولى 74/80؛ عولجت ذاكرة أصناف Godot المحلية وتوافق أرشيف السلم، ثم نجحت إعادة الفحوص الستة 6/6. تغطت المجموعات الثمانون بنجاح بعد المعالجة. التفاصيل والأوامر في verification.json.
