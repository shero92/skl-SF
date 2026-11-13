---
id: TASK-0170
status: review
owner: codex
agent: codex
priority: high
branch: codex/seabreak-painted-world
depends_on: TASK-0169
issue: none
art_request: ART-0052
touches: AGENTS.md,INDEX.md,docs/INDEX.md,.agents/project/PROJECT.md,docs/story,docs/design/STORY_CANON_AR.md,assets_hd/background/hidden_island_painted/v001,game_factory/environment/ART-0052/v002,game_factory/environment/ART-0052/v003,assets_hd/background/hidden_island_grid_painted/v001,assets_hd/background/seabreak_painted_world/v001,game_factory/environment/ART-0052/v001,.agents/graphics/requests/ART-0052_painted_coastal_world.md,.agents/graphics/deliveries/ART-0052,map_factory/painted_worlds,map_factory/worlds/seabreak_coast_01.json,scenes/world/painted_coast.gd,scenes/world/painted_coast.tscn,tools/tests/test_painted_coast.py,tools/verify_painted_coast.gd,tools/capture_painted_coast.gd,tools/test_map.json,docs/PAINTED_COAST.md,docs/OWNER_PHOTO_WORLD_20261113.md,map_factory/metadata/source_art_index.json,docs/SOURCE_ART_CATALOG.md,.agents/tasks/TASK-0170_painted_coastal_world.md,map_factory/INDEX.md,map_factory/maps/index.json,tools/prepare_hidden_island.py,tools/source_art_catalog.py,tools/tests/test_source_art_catalog.py,tools/verify_seabreak_coast.gd,docs/SEABREAK_COAST.md
test: python tools/run_tests.py --changed
done_when: Six independent native-resolution wild Hidden Island paintings grounded in the owner story match the owner's reference art direction, replace the default exterior tile rendering, have measured safe walking and scene connections, preserve room return and existing maps, and are delivered with sources, metadata, real Godot captures and passing checks.
---
# تصحيح رسوم العالم الخارجي إلى لوحات عالية التفاصيل

طلب المالك2026-11-13 حرفيًا: "the graphic must be like this , no need to use tiles, use photo with high graphic". المرجع المرفق للأسلوب فقط، ولا ينقل البطل المرسوم أو أثاث الغرفة إلى الخارج.

Agent: codex. Image tool: built-in image_gen. Model/tokens/cost unknown. العمل في نسخة وفرع مستقلين؛ لا تعديل لنسخة المالك الرئيسية أو رسوم الشخصيات أو تاريخ الخرائط. اللوحات الكاملة هي النتيجة المطلوبة صراحة، وليست مصادر لقص أجزاء إنتاجية.

## توجيه القصة2026-11-13

المالك طلب قراءة docs/story وفهرستها لجميع الوكلاء وإعادة الخارج بحسب القصة: جزيرة مخفية برية، والبطل الإنسان الوحيد المعروف. قراءة الافتتاح والسيف وفهرس بقية المشاهد ومرجع الأسرار ومقارنة النسخة الأقدم كشفت غياب ملفcanonالمحال إليه واختلاف دور الصديق في النسخة الأقدم. جُمعت الحقائق المعتمدة من الملفات المحلية وتوجيه المالك في docs/design/STORY_CANON_AR.md؛ نيرو وصديق الشعاب وسيلي شخصيات مستقلة. لا أحداث أو أسماء جديدة.

حُفظت ملفات القصة المحلية11ملفًا مع إيصال بصمات، وأضيفت مداخل القراءة إلىINDEX.md وdocs/INDEX.md وAGENTS.md وPROJECT.md. هذه مداخل دلالية يدوية، وليست إعادة توليد FILES/INDEX الآلي على فرع العمل.

اللوحات المعمارية الخمس الأولى محفوظة فيART-0052/v001 كمحاولات غير مختارة للقصة، دون تعديل أو حذفmasters. الإصدارv002 المطلوب يضم: home_descent، mossveil_edge، mossveil_roots، stormwatch_ascent، stormwatch_overlook، bone_tide_shore. هذه تقسيمات بيئية لمرحلة الافتتاح؛ لا منارات أو ساحات ذهبية مصانة أو مدن أو سكان بشر. الشخصيات والحيوانات والطقس والأحداث القصصية تظل طبقات وأنظمة منفصلة؛ لا أسرار مبكرة مخبوزة في الصور.

توجيه الموقع: المرجع هو غرفة المالك الحالية ودرجها الجنوبي فوق البحر. أول مشهد home_descent يمتد من أسفل نفس الدرج شمال اللوحة إلى ممر بري جنوبًا، لا كوخ مختلف. نُقل معرف طلبنا غير المنشور منART-0051إلىART-0052لتجنب طلب الكائنات الطائرة الذي سجله عامل الغرفة؛ تحتفظ أوامر التوليد الأصلية بمعرفها وقت التنفيذ.

توضيح العرض الأخير: أرض بخانات مربعة ثابتة مثل الغرفة وShining Force، مع رسوم عالية التفاصيل وطابع بري؛ لا منظور سينمائي متلاشٍ. مصدر المشهد الأول يعيد نفس الدرج عند شمال الصورة، ثم تتصل خانات الأرض جنوبًا. الإصدار المختارv003، وتحفظ محاولة الكوخ والمنظور الطبيعي السابق دون استعمالها.

## التسليم الفعلي

6لوحاتمختارة،8محاولاتمحفوظة،14استدعاء. قصة المالك مفهرسة فيAGENTS/INDEX/PROJECTوالمرجع المجمع. فحوص المشروع92/92، فحص المصدر8، العالم4،705PNGدون أخطاء. Godotاختبر3832خطوة و13وصلة والخروج والعودة.7لقطات فعلية وبصماتها فيART-0052/v003. RGBالمصدر محفوظ وRGBAالتسليم مطابق للألوان دون تكبير. فهرس المصدر161سجلًا/36مجموعة. تحديثات الغرفة8ملفاتمطابقةبايتًا للالتزام المنشورe50403d1؛ لا نسخ لتغييرات المالك الخاصة. مراجعة النشر الأولية رفضت الأمر قبل التنفيذ للاشتباه بقائمة واسعة، ثم تدقيق القائمة أثبت102ملفًا للمهمة و8ملفات موروثة منشورة، بلا ملفات غير متوقعة. الخطوة التالية مراجعة التكوين ودمج الفرع؛ لا ادعاء اعتماد بصري للخريطة أو تنفيذ أحداث القصة.
