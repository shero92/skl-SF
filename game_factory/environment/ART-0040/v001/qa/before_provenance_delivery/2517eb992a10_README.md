# ART-0040 — فانوس الجدار المتجه شرقًا

عنصر مستقل، نقطة تثبيت على اليسار وذراع يمتد يمينًا، ليقابل فانوس ART-0023 الغربي. توليد image_gen مستقل ثم تحرير مستقل للشفافية؛ لا عكس أو تدوير لصورة الفانوس السابق. الإضاءة من أعلى اليسار. الحالة delivered مع owner_approved=true وفق الموافقة التلقائية؛ لا تفعيل داخل الخريطة.

المصدر الكامل محفوظ في assets_hd/lighting/east_wall_lantern/v001. بيانات القياس والطلب والمراجع ونسخ الفحص هنا؛ نسخة التسليم المحددة في .agents/graphics/deliveries/ART-0040. مقاس المصدر1024×1536 يتجاوز400×720 و4x مقاس المعاينة29×53.

origin هنا نقطة الجدار اليدوية [232,330] وليست أسفل الجسم. إحداثياتها في مشتق المعاينة موثقة في native_origin؛ لا تستخدم bottom_center_origin لتثبيت الفانوس إلى الحائط. لا collider أو ظل مستقل أو هالة ضوء خارجية. موضع التثبيت المحلي على جدار الغرفة وملاءمة المقاس والإخفاء لم تُختبر؛ تبقى لدى التكامل.

## تاريخ المحاولات والشفافية

أنتجت محاولتان؛ الأولى محفوظة في rejected/ كأرشيف غير مختار بعد التحرير، وليست رفضًا من المالك. ظُن في معاينة الأداة أن هناك هالة؛ تركيب alpha على خلفية فاتحة وزرقاء أثبت أن اللون المحيط RGB مخفي تحت alpha0. لا يصح وصف ذلك بهالة مرئية أو عيب فني. النسخة الثانية مختارة، وأكدت لقطة Godot نظافة المحيط. توجد قيم alpha شديدة الضعف تصل إلى حافة Canvas السفلية؛ حدود alpha128 داخل الإطار. مشتق QA يستخدم حدود alpha128+8px، والمصدر الكامل لم يتغير.

## الأدلة وإعادة التشغيل

لقطة Godot فعلية960×720، عرض1x/3x/8x مع Nearest Neighbor وخلفيتين، وخط وردي يشير إلى نقطة التثبيت. لم تُلتقط معاينة تثبيت داخل الغرفة. نسخة target-vs-game في طلب ART-0040 مرجع فقط، ليست أصلًا إنتاجيًا.

python game_factory/environment/ART-0040/v001/prepare_review.py
Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0040/v001/review.gd
python game_factory/environment/ART-0040/v001/verify_delivery.py

## الملف والبصمة

| الملف | SHA-256 |
| --- | --- |
| assets_hd/lighting/east_wall_lantern/v001/hero_wall_lantern_east.png | 5607125059ca9c72d501f740bf28a87621305c4500a84cb703adab5102f7aef5 |
| assets_hd/lighting/east_wall_lantern/v001/rejected/hero_wall_lantern_east_attempt_01.png | 8dd0e43e1f68e2caf4c1f3b9a174c708b482481a96ae0bbfc23e8952c3ba0a8f |
