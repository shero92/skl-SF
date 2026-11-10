# Weapon Factory

اتبع [السياسة الرسومية الموحدة](../../docs/GRAPHICS_PRODUCTION_POLICY.md) قبل إنتاج أو استيراد أي سلاح. مصدر مستقل لسلاح واحد في PNG، منفصل تمامًا عن الجسم والمؤثرات. يحفظ الإصدار السابق ولا يفعّل الجديد قبل التحقق والموافقة.

catalog.json يعرّف الصور وgrip_pivot وcompatible_profiles؛ profiles.json يحدد التوافق. وجود السلاح في الكتالوج لا يثبت اعتمادًا بصريًا. اختبار WPN_HERO_BASIC_SWORD وWPN_IRON_SWORD أثناء الحركة يتطلب نقاط يد مقاسة وترتيب طبقات مناسب والتقاط Godot فعلي.


weapon_stats.json يحدد أنواع الأسلحة والفئات والأسلحة وقواعد التجهيز والمدى؛ والكود في scenes/battle/weapon_system.gd والاختبار tools/verify_weapon_system.gd.
