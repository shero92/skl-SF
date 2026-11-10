# ART-0011 — تسليم B1

المصادر مستقلة ولم تُكبّر أو تُعكس. نسخ native_review مشتقات QA بملاءمة موحدة وNearest Neighbor لحدود ألفا غير الصفرية مع حفظ كل بكسل مرئي؛ ليست ملفات دمج معتمدة.

الحالة needs_review. اعتماد المالك وتكامل Claude ومعايرة footprint والتصادم ونقاط تركيب السلم لم تتم. لا يجوز اعتماد مساحة الصورة كمساحة تصادم. المرجع للتكوين والأسلوب فقط.

| الملف | SHA-256 | الأبعاد |
|---|---|---|
| assets_hd/plants/blue_white_planter/v001/hero_blue_white_planter.png | 7a4194588eaada83f4e210d6d76701cf2c6c6ab65bc6ea200b1955923f9f2a6d | [948, 1659] |

## النواقص المرصودة
- hero_blue_white_planter: Actual built-in output is below the literal per-asset master minimum; original preserved without upscaling. Regeneration/owner decision required.

لكل مصدر نسبة تفاصيل أكبر من 4x لحجم Canvas المقترح، لكن بعض الأبعاد المطلقة أقل من حد المواصفة. لم يُخفَ ذلك بتكبير المصدر. يلزم قرار المالك أو إعادة توليد بدقة أعلى قبل إعلان استيفاء المواصفة بالكامل.

التقاط Godot: godot_native_review.png وإيصال godot_review_receipt.json بعد تشغيل سكربت المعاينة المسجل. الأشكال على لوح مراجعة فقط؛ لم تتغير أي خريطة.
