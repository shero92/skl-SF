# B3 — مصادر غرفة البطل ونتائج المحاولات

Agent: codex. Tool: built-in image_gen. Model/cost: unknown. Task: TASK-0016.

الحالة: خمسة مصادر أساسية delivered / needs_review (الباب بأربعة اتجاهات والجدار v001). ART-0023 يعاد استخدامه من PR151. ART-0037 غير مكتمل ويبقى requested / needs_regeneration. لا اعتماد بصري أو تكامل.

| الأصل | مسار Master | SHA-256 | الأبعاد |
|---|---|---|---|
| hero_compass_wood_door_south | assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_south.png | 34acf2630af2711a24973a5be029e7f9e61a7d2f011485a217a7667a9f99e6b3 | [1024, 1536] |
| hero_compass_wood_door_north | assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_north.png | b9988dfa32702f3ff61dd07efe88d4fcbbb71b489639af3a41c6c87a7b01bbb3 | [1024, 1536] |
| hero_compass_wood_door_east | assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_east.png | 8b7f3c16b988e807a2e13bcc21e61b0778ef9db83c7bb870589b5c3b9d1c7044 | [1024, 1536] |
| hero_compass_wood_door_west | assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_west.png | 1c31d20f14e94579775a99195394fb1299572bbfb7dd03193ebb7d7891c1b827 | [1024, 1536] |
| wall_straight_window_opening | assets_hd/architecture/window_wall/v001/wall_straight_window_opening.png | 7217926d76bce518ddd5b5446d035c566868bd54f0f6674fd6374ec14e4d8b4d | [1717, 916] |

فتحة v001: [58.83, 76.75] px تقريبًا؛ اتصالها بالجدار المنخفض يحتاج مواءمة.

البديل v002 محفوظ دون تغيير v001: `assets_hd/architecture/window_wall/v002/wall_straight_window_opening.png`، SHA-256 `32b5f8bf358a4f803d946f43751d873935bbac19aa91ed936c95be4eb713b503`. الفتحة65.41x52.82 مقابل60x75، لذلك حالته needs_regeneration. أبعاده2086x754 أقل6px من الحد الرأسي المكتوب760.

## ما لم يكتمل
- شبكة البحر: محاولتان1254x1254 أقل من2048x2048؛ تجاوز ألفا178، والمحاولة الأولى بلا فجوات ألفا0. لم نكبّر المصدر أو نعدّل ألفا لإخفاء الإخفاق. لا ملف إنتاجي على المسار المطلوب؛ صور المحاولات تحت rejected مع بصماتها. التقاط Godot2x2 لكل محاولة فوق مشتق QA من بحر المشروع. seamless غير مصدق.
- الجدار: v001 يطابق الفتحة تقريبًا ويحتاج وصلًا لجدار بارتفاع مناسب؛ البديل المنخفض v002 لا يطابق ارتفاع الفتحة. كلاهما محفوظ للمراجعة، ولا دمج تلقائي.
- الباب: north ظهر وظيفي؛ east/west منظران مائلان مستقلان. أطوال الزخارف الزرقاء وبعض الحفر تختلف بين الاتجاهات؛ يلزم صقل قبل وصفها turnaround متطابقة.
- Footprint بوحدات64px، نقاط تركيب الباب/الوصل والتصادم تحتاج معايرة Claude داخل المشهد.

## ما لم يُختر ولماذا
- أول جدار: فتحة ضيقة؛ المحاولة التالية v001 حسّنت الفتحة.
- جدار منخفض أولي (attempt03): الفتحة أصغر من المطلوب؛ توسعت في البديل v002 مع بقاء نقص ارتفاعها.
- محاولتا البحر: الحجم وألفا لا يستوفيان المواصفة. الملفات الأصلية والطلبات محفوظة.

## إعادة الاستخدام
- `reused_ART-0023.json` يحوي مسارات وبصمات المصادر الأربعة من https://github.com/shero92/skl-SF/pull/151 ؛ لا توليد مكرر ولا ادعاء اعتمادها. يلزم دمج PR151 بصورة منفصلة بعد المراجعة.

## معاينات فعلية
- `game_factory/environment/ART-0005/v001/godot_native_review.png`
- `game_factory/environment/ART-0038/v001/godot_native_review.png` ونسخة v002 للمقارنة مع جار موجود؛ أظهر البحر شفافية الفتحة.
- `game_factory/environment/ART-0037/v001/godot_tiled_review_attempt_01.png` وattempt02.
- QA backdrop مقتطع من أصل بحر المشروع فقط، وليس من صورة الهدف. Masters والمرجع والخريطة لم تتغير.

إعادة التشغيل: prepare_review.py للمصادر الأساسية؛ check_sea.py للمحاولات المرفوضة؛ Godot --script res://game_factory/environment/batch_B3_20261110/review.gd -- --art=ART-0038 --revision=v001 (أوv002)، وreview_sea.gd -- --attempt=1/2.

## بصمات الملفات غير الأساسية المحفوظة
| المصدر | SHA-256 | الحالة |
|---|---|---|
| assets_hd/architecture/window_wall/v002/wall_straight_window_opening.png | 32b5f8bf358a4f803d946f43751d873935bbac19aa91ed936c95be4eb713b503 | needs_regeneration |
| assets_hd/architecture/window_wall/v002/rejected/wall_straight_window_opening_attempt_03.png | 1af8f93c40dc634e2edcc7b2ab5136c00b7132dc3ec29b0ca3e0444296f98521 | needs_regeneration |
| assets_hd/background/sea_light_lattice/v001/rejected/sea_light_lattice_tile_attempt_01.png | 1f680568fa846eb377b3a345905d83ef845ec48d1bcb44ca216b320ebb432e75 | needs_regeneration |
| assets_hd/background/sea_light_lattice/v001/rejected/sea_light_lattice_tile_attempt_02.png | ecf86d0fccc322711483686f69f6dfd5de1074515807cc4e51e563e7755e0d1e | needs_regeneration |

الفحوص: run_tests.py --changed --timeout120 نجح84/84. graphics_validation خرج0 وpng_checked0 لأن المصادر المرشحة خارج نطاقه؛ الفحص المستقل يغطي5 مصادر أساسية ويكشف إخفاقات البديل والبحر منفصلة. requirements_complete=false؛ النجاح البرمجي لا يساوي اعتمادًا بصريًا.
