# ART-0005 — تسليم B3

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود alpha-128 مع هامش 8px؛ قد تستثني بكسلات ألفا ضعيفة خارج المنطقة، والمصدر الكامل محفوظ؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_south.png | 34acf2630af2711a24973a5be029e7f9e61a7d2f011485a217a7667a9f99e6b3 | [1024, 1536] |
| assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_north.png | b9988dfa32702f3ff61dd07efe88d4fcbbb71b489639af3a41c6c87a7b01bbb3 | [1024, 1536] |
| assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_east.png | 8b7f3c16b988e807a2e13bcc21e61b0778ef9db83c7bb870589b5c3b9d1c7044 | [1024, 1536] |
| assets_hd/architecture/compass_wood_door_views/v001/hero_compass_wood_door_west.png | 1c31d20f14e94579775a99195394fb1299572bbfb7dd03193ebb7d7891c1b827 | [1024, 1536] |

## النواقص المرصودة
- hero_compass_wood_door_south: Blue inset lengths and some decorative carving differ between independently generated views; owner review/refinement required before claiming a consistent turnaround set.
- hero_compass_wood_door_north: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- hero_compass_wood_door_north: Blue inset lengths and some decorative carving differ between independently generated views; owner review/refinement required before claiming a consistent turnaround set.
- hero_compass_wood_door_east: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- hero_compass_wood_door_east: Blue inset lengths and some decorative carving differ between independently generated views; owner review/refinement required before claiming a consistent turnaround set.
- hero_compass_wood_door_west: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- hero_compass_wood_door_west: Blue inset lengths and some decorative carving differ between independently generated views; owner review/refinement required before claiming a consistent turnaround set.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
