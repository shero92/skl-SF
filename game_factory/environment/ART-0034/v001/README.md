# ART-0034 — صخور البحر والأقواس والضباب v001

Agent: codex. Task: TASK-0102. Branch: codex/art-0034-0035-coast-plants. إنتاج 2026-11-10.

المصادر: assets_hd/background/sea_coast/v001/.
العناصر الثمانية: sea_stack_tall_a/b/c، rock_arch_far_left/right، horizon_haze_strip، foam_patch_a/b.

قُيّدت فتحات القوسين كمساحة شفافة فعليًا، مع probes موثقة في manifest وفحص بصري داخل Godot. الضباب overlay شبه شفاف، وتعرضه المعاينة عند review_opacity=0.25؛ هذه قيمة للمراجعة تحتاج ضبطًا مع ألوان الأفق، وليست قاعدة إضاءة جديدة. تصل أطرافه الخارجية إلى alpha=1 فقط؛ الحدود الأساسية alpha128 داخل canvas، والمصدر لم يعدّل.

الصخرة B الأولى ظهرت كجزيرة عريضة قصيرة؛ حُفظت في rejected/sea_stack_tall_b_attempt_01.png، والنسخة المختارة الجديدة برج طويل مستقل. qa/before_stack_b_correction يحفظ manifest ولقطة المعاينة والreceipt قبل التصحيح. لا تستخدم أرشيف الرفض في المشهد.

الزبد صورتان ثابتتان مستقلتان، وليس animation loop. لا بحر أو سماء أو ظل أرضي مدمج بالصخور، ويظل أساس الماء الموجود دون استبدال. التوزيع في الخلفية ودرجات البعد والأحجام العالمية لم تعاير بعد.

## طريقة الاستخدام

كل master ناتج builtin_image_gen مستقل؛ لم تُقتطع الأصول من ورقة ولم يُستخدم قلب صورة لاشتقاق اتجاه. المصادر الأصلية محفوظة بلا تعديل. نسخ native_review مشتقات Nearest Neighbor مستقلة للمراجعة، وليست runtime assets معتمدة.

جميع المسارات نسبية لجذر H:/shining force/skl-SF. ملف manifest.json يربط الاسم والمسار والأبعاد وRGBA وalpha وSHA-256 والاتجاه والطلب ونسخة المراجعة. origin.pixels بالبكسل من أعلى يسار المصدر؛ هو ارتكاز هندسي للمراجعة ولا يمثل نقطة تركيب مقاسة في الخريطة. footprint وruntime_scale وplacement المجهولة null صراحة، وتحتاج معايرة قبل الإدراج.

requests/ يحفظ نص كل طلب. godot_native_review.png لقطة viewport فعلية 1024×1024؛ godot_review_receipt.json يثبت بصمة manifest والصورة والمحرك والعدد. الأداة المحلية review.gd تعرض المشتقات وتلتقط اللوحة ثم تغلق:
Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0034/v001/review.gd

لا اعتماد على .codex/generated_images؛ نسخ التسليم النهائية محفوظة داخل المشروع. نسخ توافق طلب التسليم في .agents/graphics/deliveries/ART-0034 داخل فرع المهمة. ملفات gdignore تستبعد مصادر QA من الاستيراد الآلي؛ التحميل صريح عبر Image.load_from_file، وأداة المراجعة ليست مشهد تصدير للعبة.

الحالة needs_review، owner_approved=false، production_active=false. موافقة المالك على ART-0032/0033 لا تعتمد هذه الصور الأحدث تلقائيًا. لا تعديل لخريطة أو سجل إنتاج أو أصل معتمد. catalog IDs والتصادمات ومواضع العمق والقياس مرحلة منفصلة بعد المراجعة.

نموذج الصور غير مكشوف من الأداة؛ التكلفة والاستهلاك غير المقاسين unknown وليسا صفرًا. الفحص التقني لا يعوض اعتماد المالك. تفاصيل الفحص والقيود في qa/verification.md وqa/verification.json.

## اعتماد المالك 2026-11-10

اعتمد المالك جميع الصور المختارة المسلمة وطلب الدمج. owner_approved=true في manifest. المصدر المرفوض B لا يشمله الاعتماد. حُفظت لقطة وmanifest وreceipt السابقة في qa/before_owner_approval؛ المعايرة والتركيب منفصلان. أوصاف needs_review السابقة تسجل مرحلة التسليم.
