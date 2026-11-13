# العالم الخارجي — Seabreak Coast

طلب المالك2026-11-12: الخروج من غرفة البطل إلى مكان واسع يمكن السير فيه واكتشاف العالم.

المشروع القابل للتجربة: `H:/shining force/skl-SF/.worktrees/seabreak-coast/project.godot`؛ الفرع `codex/seabreak-coast`، أساسه غرفة TASK-0168 عند commit `2c0b2ab6366622866adaaaef972fead73773d54f`. لا ملفات جديدة في نسخة المالك الرئيسية؛ تظهر بعد دمج الفرع.

## التشغيل

افتح نسخة عمل المهمة في Godot واضغط F5. انزل درج الغرفة لتنتقل تلقائيًا إلى الخارج. تحرك بـWASD أو الأسهم، واتبع الطرق الحجرية لاستكشاف المناطق. البوابة الزرقاء الكبيرة شمال نقطة الوصول تعيدك إلى الغرفة. يمكن تشغيل `scenes/world/seabreak_coast.tscn` مباشرة بـF6 لمعاينة الخارج.

الخريطة `6144×4096`، أي16مرة مساحة Canvas الغرفة1536×1024. الأرض2161خانة64px، والمشي2029خانة؛ هذا ليس قياسًا لزمن اللعب أو ادعاء عالم مفتوح مكتمل. يوجد طريق دائري ودرب جانبي وست وجهات:

| الوجهة | موضع الخانة | التكوين |
| --- | --- | --- |
| Sanctuary Gate |18,12| بوابة العودة ودرج الوصول وحديقة ساحلية |
| Compass Court |42,25| بوصلة كبيرة وأعمدة وبداية تفرع الطرق |
| Palm Gardens |72,18| نخيل وأزهار ومقاعد وإطلالات شرقية |
| Beacon Terrace |77,47| أربعة أعمدة كبيرة فوق البحر |
| Sunken Archive |29,48| قوس أطلال وأعمدة مكسورة ومسار يمر بين ركيزتي القوس |
| Quiet Overlook |11,37| مطل جانبي هادئ خارج الحلقة الرئيسية |

الكاميرا تتبع البطل وتلتزم بحدود العالم؛ البحر متحرك بأصول المحرك الحالية. العالم مبني من أجزاء مستقلة موجودة في الكتالوج، وليس صورة مسطحة. وضع الصورة في غرفة البطل يبقى كما هو. تتوفر أنظمة المحرر/المعدات/الحلبة الحالية داخل مشاهد الغرفة؛ المشهد الخارجي هنا مخصص للتجول والعودة.

## أين توجد الخريطة والقطع والبيانات؟

- `map_factory/maps/index.json`: موضع أحدث خريطة ومفتاحها `seabreak_coast_01`.
- `map_factory/maps/seabreak_coast_01/latest.json`: أحدث نسخةv0003. كل من versions/blocks/layers/changes يحتفظ بالإصدارات السابقة؛ v0001 للأرض الأولى، v0002 لإعادة استخدام العشب، v0003 لقواعد العوائق وإخلاء الطرق من7جدران.
- `map_factory/worlds/seabreak_coast_01.json`: مواضع الوصول والعودة ومناطق الانتقال والمعالم و132خانة ممنوعة عند قواعد الأجزاء. المناطق غير الموصوفة والماء مغلقة للمشي؛ fly/swim لا يمنحان للبطل.
- `map_factory/metadata/asset_index.json`: سجلاG13/G14 للعشب إضافة إلى الأجزاء القديمة. نسختاPNG في `map_factory/parts/floors/G13_Coastal_Grass_A.png` و`G14_Coastal_Grass_B.png`.
- `map_factory/worlds/seabreak_source_reuse.json` و`grass_source_receipt.json`: SHA-256 للمصادر العالية الأصلية ولنسختي64×64. هما نفس ملفيnative من ART-0041/PR188 دون تغيير بايتات؛ master1254×1254 وفرعه ورابطPR موثقة. لا يعتمد تشغيل العالم على وجود فرع المنتج أو cache الصور.
- `scenes/world/room_exit.gd`: ربط الدرج فقط عبر عقدةOutdoorExit في main.tscn. لم يعدل main.gd أوplayer.gd أوdialogue_ui.gd.
- `scenes/world/world_travel.gd`: علامة عودة مؤقتة، دون إعدادautoload أو كتابة حفظ اللاعب.
- `scenes/world/seabreak_coast.gd` و`.tscn`: تركيب البيئة والبطل الموجود والكاميرا والبوابة.
- `docs/previews/seabreak_coast/`: ثماني لقطاتviewport فعلية، وإيصال المحرك وبصمات الصورة والخريطة والربط، وverification.json وسجلات الاختبارات.

## التحقق الفعلي والحدود

`python -u tools/run_tests.py --changed --timeout 600`: **91/91** مجموعة فحص نجحت. إعادة فحوص الخريطة/الملاحة/السجل/الانتقال بعد تنقيح العوائق: **4/4**. `graphics_validation.py --changed` فحص705PNG بلا أخطاء أو تحذيرات. مصدر فهرس الاختبارات صالح؛ INDEX.md الآلي يتجدد علىmain.

اختبار Godot شغّل حركةHeroPlayer الحالية3451خطوة إلى الوجهات الست، ثم غيّر المشهد من الغرفة إلى العالم وعاد منه فعلًا. فحص موضعي العودة في وضعي الصورة وMap Factory، ومنع الانتقال أثناء توقف البطل، وعدم تكرار الانتقال بعد العودة. اللقطات من Godot4.7.2، ولقطةoverview تستخدم zoom0.25 للمراجعة فقط؛ اللعب نفسهzoom1.0.

قواعد العوائق تقديرات محافظة على شبكة64px، وليست مضلعات فيزيائية مقاسة منalpha لكلSprite؛ محفوظة كـneeds_review. الأشجار والأجزاء تحجب البطل بترتيبY الحالي. لا ادعاء اعتماد المالك لتكوين الخريطة؛ visual_qa يبقىneeds_review رغم الموافقة التلقائية على الصور. يلزم مرور بصري من المالك للمقياس والازدحام والحواف. التنقل داخل المباني الأخرى/السباحة/قتال جديد ليست وظائف هذه المنطقة.

## إعادة البناء والاختبار

على نسخة مشروع نظيفة لا تحتوي الخريطة، شغّل بالترتيب:

```powershell
python tools/build_seabreak_coast.py
python tools/polish_seabreak_coast.py
python tools/refine_seabreak_coast.py
```

هذه الأدوات ترفض إعادة كتابة الإصدارات المنشورة. أي تحسين تالٍ ينبغي أن يكونpatch جديدًا فوقlatest.

للتحقق دون إعادة إنشاء الخريطة:

```powershell
python -m unittest discover -s tools/tests -p test_seabreak_coast.py
python tools/run_tests.py --only map_factory --only map_registry_validate --only navigation_grid --only seabreak_coast --timeout 120
```

التقاط المشاهد الفعلية: شغّل Godot بإعدادالمشروع و`--script res://tools/capture_seabreak_coast.gd`. لإثبات السير والانتقال: `--headless --script res://tools/verify_seabreak_coast.gd`. الإيصال لا يعتمد علىhash لملف يتغير آليًا أثناء العرض.

Agent: codex. Tool: existing Godot + Python + approved reusable art. New image-generation calls:0. Model/tokens/cost:unknown؛ إيصال التكلفة الحقيقي يرافقCommit. PR مُتسلسل فوق `claude/photo-backdrop-test` للحفاظ على تعديلات الغرفة ودمج أساسها أولًا؛ لا دفع إلىmain.

طلب الدمج: https://github.com/shero92/skl-SF/pull/191؛ قابل للدمج دون تعارض مع تحديث غرفة0a309120 عند الفحص. الاختبارات المحلية ضد أساس2c0b2ab6 الموضح أعلاه.
