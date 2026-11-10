# B2 — تسليم مصادر غرفة البطل

ثمانية مصادر مستقلة، حالة delivered / needs_review فقط. المكتبة: south/north؛ الرف: south؛ بقية مناظيرهما مؤجلة وفق المواصفة. لا تكامل ولا اعتماد بصري.

| الأصل | مسار Master | SHA-256 | الأبعاد |
|---|---|---|---|
| hero_study_bookshelf_south | assets_hd/furniture/study_bookshelf_views/v001/hero_study_bookshelf_south.png | 116feab55c4a93c208f2c360e42f5f9e05dbd0d7ab072c02edd61641f45372b4 | [1616, 973] |
| hero_study_bookshelf_north | assets_hd/furniture/study_bookshelf_views/v001/hero_study_bookshelf_north.png | fcb3079d48951276a1e245fa1bffdad591a5176282b6b002d66813b8733196c7 | [1536, 1024] |
| hero_headboard_shelf_south | assets_hd/furniture/headboard_shelf/v001/hero_headboard_shelf_south.png | eaf81250b1acb7893ad977767d973a879c48cc3491389e1550c15027d7083f22 | [1564, 1006] |
| hero_stone_sphere_finial | assets_hd/architecture/sphere_stair_post/v001/hero_stone_sphere_finial.png | 7480fde019f3e1cf63059109e1f08a7deaaa29ded16851eb550e5d62a548d475 | [1024, 1536] |
| hero_rope_post | assets_hd/decor/rope_post_fence/v001/hero_rope_post.png | f8622227f1085197dc47bd1ef96f29f03fb69d61302647de0e39e1392ab5c15e | [836, 1881] |
| hero_rope_swag_west_rail | assets_hd/decor/rope_post_fence/v001/hero_rope_swag_west_rail.png | 56dd9716f6b29d46726fef5d1784fa233acb2c7cb6491a3ce3ba46d5698850a8 | [2079, 756] |
| hero_rope_swag_east_rail | assets_hd/decor/rope_post_fence/v001/hero_rope_swag_east_rail.png | 429ce3027fb3d7ed47655ae60f2a2181ad195ccf89c8b39ef834032526b8365c | [1983, 793] |
| hero_compass_floor_inlay | assets_hd/decor/compass_inlay/v001/hero_compass_floor_inlay.png | 4af0f23f62758cf2ba5baee1e8bf69af628689b827a1aef40d2465e37f69b955 | [1465, 1073] |

المحاولات غير المختارة أربع: رف بزهرة مقصوصة؛ عمودان بكرة أكبر من النسبة المستهدفة؛ خلفية مكتبة بجرم أزرق وصناديق لا تطابق الأمام. التصحيح المختار خلفي فعلي، بجرم نحاسي وصناديق مدعمة. اللون البني في RGB خلف العمود والمكتبة ألفا صفرية ولا يظهر في Godot؛ لم يُحذف من المصدر.

النقص: بعض أبعاد Masters المطلقة (خصوصًا المكتبة) أقل من حد المواصفة، مع تحقق4x للكل؛ لا تكبير. Footprint والتصادم ونقاط تركيب الرف ونهايات الحبال تحتاج معايرة المشهد. الأصل الجديد للعمود كامل حسب المواصفة الأحدث.

النسخ القديمة للـ ART-0022 وART-0024 محفوظة في archive_pre_B2_20261110. حقل files للتوافق يشير للقديم؛ حقل items يصف الجديد. لا نقل لنقاط التثبيت القديمة إلى الجديد.

معاينة native مشتقة من حدود alpha128 مع8px إضافية وNearest Neighbor موحد؛ قد تستبعد ألفا ضعيفة خارج المنطقة. Masters محفوظة كاملة. لكل ART لقطة Godot فعلية وإيصال بصمات.

إعادة المعاينة: python game_factory/environment/batch_B2_20261110/prepare_review.py ثم Godot --script res://game_factory/environment/batch_B2_20261110/review.gd -- --art=ART-0020 (أو أحد IDs الدفعة).

الفحوص: python tools/run_tests.py --changed --timeout 120 نجح80/80. graphics_validation خرج0 وpng_checked=0؛ المصادر الثمانية فُحصت منفصلًا في technical_qa.json.
