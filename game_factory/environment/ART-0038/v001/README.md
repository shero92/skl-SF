# ART-0038 — تسليم B3

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود alpha-128 مع هامش 8px؛ قد تستثني بكسلات ألفا ضعيفة خارج المنطقة، والمصدر الكامل محفوظ؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/architecture/window_wall/v001/wall_straight_window_opening.png | 7217926d76bce518ddd5b5446d035c566868bd54f0f6674fd6374ec14e4d8b4d | [1717, 916] |

## النواقص المرصودة
- wall_straight_window_opening: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.
- wall_straight_window_opening: End joins/course heights need comparison and scene calibration against existing wall; not certified seamless.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
