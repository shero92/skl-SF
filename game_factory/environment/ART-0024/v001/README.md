# ART-0024 — تسليم B2

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود alpha-128 مع هامش 8px؛ قد تستثني بكسلات ألفا ضعيفة خارج المنطقة، والمصدر الكامل محفوظ؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/decor/rope_post_fence/v001/hero_rope_post.png | f8622227f1085197dc47bd1ef96f29f03fb69d61302647de0e39e1392ab5c15e | [836, 1881] |
| assets_hd/decor/rope_post_fence/v001/hero_rope_swag_west_rail.png | 56dd9716f6b29d46726fef5d1784fa233acb2c7cb6491a3ce3ba46d5698850a8 | [2079, 756] |
| assets_hd/decor/rope_post_fence/v001/hero_rope_swag_east_rail.png | 429ce3027fb3d7ed47655ae60f2a2181ad195ccf89c8b39ef834032526b8365c | [1983, 793] |

## النواقص المرصودة
- hero_rope_post: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- hero_rope_swag_east_rail: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
