# ART-0035 — الأحواض والنخيل والزهور واللبلاب v001

Agent: codex. Task: TASK-0102. Branch: codex/art-0034-0035-coast-plants. إنتاج 2026-11-10.

المصادر: assets_hd/plants/coastal_garden/v001/.
العناصر التسعة: planter_stone_flowers_large/medium، palm_clump_front_left/right، flower_mound_white/blue، ivy_tuft_wall_a/b، hanging_vine_long.

الأحواض عناصر متكاملة مع أزهارها. تضم كتل النخيل بعض الأزهار الصغيرة؛ لا تصفها كطبقة نخيل خالية من الأزهار. كتل الزهور واللبلاب مستقلة بلا جدار أو أرضية مدمجة.

origin أعلى حدود alpha128 للّبلاب والعِرق المعلّق، وأسفل الحدود للأحواض والكتل الأرضية؛ هذه مراكز حدود هندسية وليست نقاط تعليق أو تصادم نهائية. المعاينة تصطف في لوحة فقط ولا تختبر تثبيت النباتات على الجدران.

نسخة hanging_vine_long الصغيرة تزيل الهامش الخارجي حتى حدود alpha غير الصفرية من هذا المصدر الفردي ثم تلائم canvas مراجعة 160×256 بـNearest Neighbor؛ حفظت native_review_source_region والتحويل في manifest. لم يقص جزء من النبات، ولم يعدل master أو يعاد استخدام صورة متعددة الوضعيات.

## طريقة الاستخدام

كل master ناتج builtin_image_gen مستقل؛ لم تُقتطع الأصول من ورقة ولم يُستخدم قلب صورة لاشتقاق اتجاه. المصادر الأصلية محفوظة بلا تعديل. نسخ native_review مشتقات Nearest Neighbor مستقلة للمراجعة، وليست runtime assets معتمدة.

جميع المسارات نسبية لجذر H:/shining force/skl-SF. ملف manifest.json يربط الاسم والمسار والأبعاد وRGBA وalpha وSHA-256 والاتجاه والطلب ونسخة المراجعة. origin.pixels بالبكسل من أعلى يسار المصدر؛ هو ارتكاز هندسي للمراجعة ولا يمثل نقطة تركيب مقاسة في الخريطة. footprint وruntime_scale وplacement المجهولة null صراحة، وتحتاج معايرة قبل الإدراج.

requests/ يحفظ نص كل طلب. godot_native_review.png لقطة viewport فعلية 1024×1024؛ godot_review_receipt.json يثبت بصمة manifest والصورة والمحرك والعدد. الأداة المحلية review.gd تعرض المشتقات وتلتقط اللوحة ثم تغلق:
Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0035/v001/review.gd

لا اعتماد على .codex/generated_images؛ نسخ التسليم النهائية محفوظة داخل المشروع. نسخ توافق طلب التسليم في .agents/graphics/deliveries/ART-0035 داخل فرع المهمة. ملفات gdignore تستبعد مصادر QA من الاستيراد الآلي؛ التحميل صريح عبر Image.load_from_file، وأداة المراجعة ليست مشهد تصدير للعبة.

الحالة needs_review، owner_approved=false، production_active=false. موافقة المالك على ART-0032/0033 لا تعتمد هذه الصور الأحدث تلقائيًا. لا تعديل لخريطة أو سجل إنتاج أو أصل معتمد. catalog IDs والتصادمات ومواضع العمق والقياس مرحلة منفصلة بعد المراجعة.

نموذج الصور غير مكشوف من الأداة؛ التكلفة والاستهلاك غير المقاسين unknown وليسا صفرًا. الفحص التقني لا يعوض اعتماد المالك. تفاصيل الفحص والقيود في qa/verification.md وqa/verification.json.

## اعتماد المالك 2026-11-10

اعتمد المالك جميع الصور المختارة المسلمة وطلب الدمج. owner_approved=true في manifest. المصدر المرفوض B لا يشمله الاعتماد. حُفظت لقطة وmanifest وreceipt السابقة في qa/before_owner_approval؛ المعايرة والتركيب منفصلان. أوصاف needs_review السابقة تسجل مرحلة التسليم.
