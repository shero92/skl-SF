# ART-0042 — جدار خلفي مستقل

مصدر PNG مستقل، لا قصاصة من المرجع ولا Sprite Sheet. Agent: codex؛ الأداة built-in image_gen؛ النموذج والكلفة غير مقاسين. الموافقة البصرية تلقائية وفق docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md، لكن الحالة delivered / needs_map_calibration؛ لا تفعيل داخل الخريطة.

المقاس الأصلي [1921, 819]؛ مقاس Canvas المعاينة [470, 200]. تحويل Canvas كامل بـNearest Neighbor، دون قص أو عكس أو دوران أو تكبير. أصل الارتكاز أسفل منتصف الحدود المرئية: [955.5, 769]. نسبة كثافة المصدر لكل بكسل معاينة: [4.087234042553192, 4.095]؛ الحد الأدنى4x متحقق. واجهة الجدار جنوبية؛ الكاميرا من الجنوب تنظر شمالًا إلى أسفل، والضوء من أعلى اليسار.

| الملف | SHA-256 |
| --- | --- |
| assets_hd/architecture/rear_left_window_wall/v001/hero_rear_left_ruined_wall_window.png | a43aa0bbad6d8246083b4e9424f25ad1b9aa3450926f107a8fe3ad3f8ac10667 |

النافذة/الباب والدرجات مرسومة داخل قطعة الجدار نفسها. النباتات والفوانيس والرايات والأثاث والأرض والبحر والظلال الخارجية غير مدمجة. لا تصادم أو وصلات تخمينية: collision وconnection_sockets مجهولة وتحتاج تحديدًا مع إزاحة الجدار في مشهد التكامل. لم تتغير خرائط أو أجزاء قديمة أو ملفات Golden Cyclone.

ملف manifest.json يحمل كل الطلبات والبصمات والمراجع ومقاسات المصدر والمعاينة ونسخ التسليم. استعرض godot_native_review.png: لقطة viewport فعلية1x/2x إلى جانب قصاصة مرجعية لا تدخل اللعبة. لا تثبت اللقطة الالتحام بالجدار المجاور أو ملاءمة ممر المشي. الألوان والنسب والحدود قورنت بصريًا؛ القيم الآلية وحدها ليست اعتمادًا لتكوين الغرفة.

إعادة القياسات: python game_factory/environment/rear_walls_20261111/prepare_review.py
الالتقاط: Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/rear_walls_20261111/review.gd
التحقق: python game_factory/environment/rear_walls_20261111/verify_delivery.py

المصادر محفوظة في الفرع codex/art-0042-0043-rear-walls داخل H:/shining force/skl-SF/.worktrees/art-rear-walls، وفق TASK-0162. المسارات في manifest نسبية لجذر نسخة العمل؛ تظهر في مجلد main بعد دمج التسليم، ولا توجد حاجة إلى cache الأداة في C:.

الفتحة مكوّن alpha<=8 مغلق ومحاط بالحجارة، والوسط alpha0 حقيقي. أكبر حدودها في المعاينة [43.305570015616865, 43.956043956043956] بكسل؛ نحو44×44 وليست40×40 بالضبط. المحاولة الأولى حُفظت لأن الفتحة كانت أطول من المربع.
