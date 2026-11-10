# ART-0019 — تسليم B1

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود ألفا غير الصفرية مع حفظ كل بكسل مرئي؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/furniture/study_table_views/v001/hero_study_table_south.png | 1b3ea8a1ee93dcbb6d01747ec70462f0664422e32b23b37a68badb7a0cbb6ff3 | [1448, 1086] |
| assets_hd/furniture/study_table_views/v001/hero_study_table_north.png | 15c67a248c310c1feb3754eeebb0572e3152090d9c1f94ea71be3202f86fedbc | [1448, 1086] |
| assets_hd/furniture/study_table_views/v001/hero_study_table_east.png | 36c47434340e3f1cd52c78e074907b30aff653596b08e784a6479ce33ca00b7b | [1448, 1086] |
| assets_hd/furniture/study_table_views/v001/hero_study_table_west.png | a33878c952c3dcb9790cbbc6a69c34c47bfd2b10e201730bb4591f79affa0acb | [1448, 1086] |

## النواقص المرصودة
- hero_study_table_south: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_study_table_north: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_study_table_east: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_study_table_east: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- hero_study_table_west: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_study_table_west: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
