# ART-0025 — تسليم B1

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود ألفا غير الصفرية مع حفظ كل بكسل مرئي؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/architecture/entrance_stairs/v001/hero_entrance_stairs_south.png | 1ad183f2a4054081d747003c1c377bd0557a1d50f83fa56953c2a88949881adc | [1320, 1192] |

## النواقص المرصودة
- hero_entrance_stairs_south: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.
- hero_entrance_stairs_south: Visible pixels are inside canvas but some margins are less than the approximately 3 percent target.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
