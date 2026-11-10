# ART-0020 — تسليم B2

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود alpha-128 مع هامش 8px؛ قد تستثني بكسلات ألفا ضعيفة خارج المنطقة، والمصدر الكامل محفوظ؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/furniture/study_bookshelf_views/v001/hero_study_bookshelf_south.png | 116feab55c4a93c208f2c360e42f5f9e05dbd0d7ab072c02edd61641f45372b4 | [1616, 973] |
| assets_hd/furniture/study_bookshelf_views/v001/hero_study_bookshelf_north.png | fcb3079d48951276a1e245fa1bffdad591a5176282b6b002d66813b8733196c7 | [1536, 1024] |

## النواقص المرصودة
- hero_study_bookshelf_south: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_study_bookshelf_south: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- hero_study_bookshelf_north: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_study_bookshelf_north: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
