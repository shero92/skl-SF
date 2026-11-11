# ART-0041 — أرضية ومؤشرات ساحة المناوشة

ستة أصول مستقلة: بلاطتا عشب/تراب متوافقتان في التكرار، صخرة حجر جيري لخانة معيقة، إطار حركة أزرق، إطار هدف أحمر، وحلقة دور نشط ذهبية. كل موضوع بطلب image_gen مستقل؛ سبع مكالمات مع تصحيح الحلقة مرة واحدة وحفظ المحاولة السابقة. الموافقة البصرية تلقائية؛ الحالة delivered / needs_runtime_integration، دون تفعيل في مشهد الإنتاج.

| الأصل | المصدر / الأبعاد | SHA-256 |
| --- | --- | --- |
| field_grass_a | assets_hd/floor/skirmish_field/v001/field_grass_a.png / [1254, 1254] | 7742a517c424a3d5775d18a687599a019d8859202ce6bc0c3937ba8fd5dacbcf |
| field_grass_b | assets_hd/floor/skirmish_field/v001/field_grass_b.png / [1254, 1254] | 7833ccc5e8155eae144d829fec3e9ba089c3585e14324ea54483a98132f56dd1 |
| field_rock_block | assets_hd/props/skirmish_rock/v001/field_rock_block.png / [1024, 1536] | 509903867a4f24a8ed89368fa40ba685ef33d8e164989e0f9de6d849b15aac24 |
| marker_move | assets_hd/decor/skirmish_markers/v001/marker_move.png / [1254, 1254] | 423170ff3fb038b1d0e6acdcf5b35a74688a328819509fc71e71a1429c4c8935 |
| marker_target | assets_hd/decor/skirmish_markers/v001/marker_target.png / [1254, 1254] | ecd376872d8ab5f869f5d2872e2dd6650846294f007cd153002ff381ec22a205 |
| marker_active | assets_hd/decor/skirmish_markers/v001/marker_active.png / [1254, 1254] | 0ef8ea6b7678ceb09f5bf93d0dfb8cdeb4eadba41fa7ae42b87df3a53c0348fc |

## الاستخدام والقياسات

البلاطتان floor surfaces معتمتان بملء64×64، بخلاف قصاصات الصخور والمؤشرات الشفافة. ملفات RGB الأصلية محفوظة في generation_sources؛ صادرات RGBA تضيف Alpha255 فقط، وثبت تطابق بايتات RGB لكل بكسل. لا تكبير أو تغيير للرسوم الأصلية. جميع المصادر تتجاوز الحدود512×512 أو512×768 و4x دقة العرض.

عرض الأرضية والمؤشرات64×64 عند أعلى يسار الخانة. الصخرة Canvas64×96، draw_offset[0,-32] ليرتكز أسفلها على نهاية الخانة؛ مساحة الإعاقة من بيانات Session وليس Collider جديدًا. لا تعديل للملاحة أو الضرر أو الأسلحة.

المؤشرات تُعرض بكامل Canvas دون ملاءمة bbox منفصلة، مع opacity0.75 وNearest. سمك النواة عند المنتصف2بكسل في الجهات الأربع؛ زوايا الدائرة تتدرج كبكسلات طبيعية. مركز كل مؤشر Alpha0. الحلقة الذهبية تستعمل إزاحة شبكة أخذ عينات بمقدار2بكسل مصدر (نحو0.1بكسل معاينة): الحافتان المزالَتان شفافيتان تمامًا مع حشو شفاف مقابل؛ لا بكسل مرئي قُص أو مصدر عُدّل. في المصدر هامش فعلي يقارب9بكسلات معاينة حول الإطار، وليس2؛ رقم2 هو سمك الخط.

الاستيراد المقترح: lossless، mipmaps=false، texture_filter=Nearest. تغيير Filter/Repeat في Godot4 على CanvasItem وليس خيارًا في استيراد الصورة. لا حاجة لاستيراد masters العالية الدقة في التشغيل؛ اشتق نسخ اللعبة من البيانات المؤرخة.

## ما فُحص فعليًا

godot_asset_review.png: لوحة viewport فعلية فيها checker4×4 ونسخ المؤشرات فوق البلاطتين والصخرة. لا فواصل حادة ظاهرة عند التكرار بالحجم المقترح؛ فروق حواف A/A وA/B وB/A وB/B أقل من متوسط التغير داخل البلاطات، والقيم في technical_qa.json؛ الأرقام وحدها ليست دليلًا بصريًا.

godot_skirmish_review.png: تحميل tactical_battle.tscn نفسه مع تبديل سكربت الرسم إلى subclass خاص بالمعاينة في الذاكرة. Session مجمدة ولا إدخال؛ الشخصيات بقيت بأشكال الدوائر الموجودة. مؤشر أحمر على عدو للتوضيح البصري فقط وليس قاعدة مدى هجوم. لا تعديل لأي ملف إنتاجي للمشهد أو قواعده أو تفعيل دائم للأصول. لا ادعاء اختبار حركة/هجوم حيّ باستخدام الرسوم الجديدة.

إعادة القياس: python game_factory/environment/ART-0041/v001/prepare_review.py
الالتقاط: Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0041/v001/review.gd
التحقق: python game_factory/environment/ART-0041/v001/verify_delivery.py

المصادر والتسليم والبيانات داخل H:/shining force/skl-SF/.worktrees/art-skirmish-field في الفرع codex/art-0041-skirmish-tiles؛ وفق TASK-0162 لم تُنسخ أصول غير ملتزمة إلى main. الطلبات والبصمات وnative_source_region وorigin وgrid_anchor_native موثقة لكل قطعة. المحاولة الذهبية السابقة في rejected/ لم تُحذف، والتصحيح ومحاذاة التصدير موثقان.

أدوات إعادة الفحص تتطلب Python مع Pillow وNumPy وGodot المحدد في إعدادات المشروع. فهرس المصادر مجمع عبر فروع الإنتاج؛ استُخدمت نسخ محلية من PR179/182/185 للتدقيق فقط ولم تُعد مرحلتها. سجلات المصدر غير الموجودة على main تحمل محدد فرعها؛ يجب إحضار ذلك الفرع عند فحص الكتالوج الكامل. مرشحات PR185 تبقى غير مؤهلة ولا يغيّرها هذا التسليم.
