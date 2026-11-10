# ART-0033 — حافة الشرفة والجرف v001

Agent: codex. Task: TASK-0102. إنتاج 2026-11-10 عبر builtin_image_gen؛ نموذج الصورة غير مكشوف من الأداة.

ثمانية masters مستقلة، بحالة needs_review. لا تنشيط في سجل الأصول أو تعديل للخريطة. اعتماد التسليمات السابقة لا يعتمد هذه الصور الجديدة تلقائيًا.

## الملفات من جذر H:/shining force/skl-SF

- المصادر الأصلية: assets_hd/background/terrace_cliff/v001/<asset_name>.png.
- manifest.json المجاور: الاسم، المسار، أبعاد الأصل، RGBA، alpha، حدود silhouette عند alpha128، SHA-256، الاتجاه، الارتكاز الهندسي، البصمة والطلب.
- requests/: طلب مستقل لكل مصدر.
- native_review/: ثمانية مشتقات Nearest Neighbor مستقلة للمراجعة؛ ليست runtime assets معتمدة.
- godot_native_review.png وgodot_review_receipt.json: لقطة viewport فعلية 1024×1024 وبصمة manifest والمحرك.
- نسخ توافق طلب التسليم داخل فرع المهمة: .agents/graphics/deliveries/ART-0033/.
- المصدر الدائم في المشروع، وليس .codex/generated_images؛ لا اعتماد تشغيلي على مجلد الأداة.

## العناصر الثمانية

terrace_edge_straight: انتقال علوي ضحل على حافة الشرفة.
terrace_edge_corner_left / terrace_edge_corner_right: زاويتان مستقلتان للحافة.
cliff_face_front_a / cliff_face_front_b / cliff_face_front_c: واجهات صخرية عميقة مختلفة التفاصيل.
cliff_rubble_cluster: مجموعة ركام مستقلة، ذات فراغات شفافة بين الأحجار.
foam_at_cliff_base: زبد أبيض/سماوي مستقل، بلا صخور أو مستطيل بحر مدمج؛ صورة واحدة ثابتة وليست حلقة حركة.

## الاستخدام والمعايرة

كل PNG ناتج توليد مستقل؛ لا قص من ورقة ولا mirroring لاشتقاق الاتجاه. المصادر لم تصغّر في مكانها أو يُعاد رسمها برمجيًا. كل مشتق مراجعة منفصل ويحفظ نسبة الأصل. توجد أجزاء قصيرة وعميقة؛ لا تفترض ارتفاعًا ثابتًا أو توافق النهايات دون معايرة.

pixel_size وorigin.pixels بوحدة بكسل المصدر ومن أعلى اليسار. origin هو منتصف أسفل حدود alpha128، ارتكاز هندسي للفحص فقط. footprint_proposed_px مقترح على شبكة 64px؛ ليس footprint مصادقًا عليه. runtime_scale وconnection_sockets يظلان null حتى القياس داخل المشهد. تُسند catalog IDs بعد المراجعة، ولا تعاد كتابة الخرائط التاريخية.

لا ظل أرضي أو خلفية بحر أو مشهد غرفة مدمج في الأصل. الزبد طبقة مستقلة عند قاعدة الجرف. يلزم اختبار الوصل البصري مع الجدران والدرج وكتلة الشرفة، وتصادمات الخريطة؛ لم تنفذ هذه الاختبارات في تسليم الصور.

## إعادة معاينة Godot

Godot --path . --rendering-method gl_compatibility --script res://game_factory/environment/ART-0033/v001/review.gd

السكربت محلي للمراجعة ويلتقط اللوحة ثم يغلق؛ لا يغير الخريطة. gdignore يمنع استيراد مصادر QA تلقائيًا، والتحميل صريح عبر Image.load_from_file. لا يعد المشهد جاهزًا لتصدير اللعبة.

فحص الشفافية والبصمات لا يعوض اعتماد المالك. بعض المصادر أقصى alpha فيها 254؛ حُفظت دون تعديل. القيم المالية والاستهلاك غير المقاس unknown وليست صفرًا. تفاصيل الفحص في qa/verification.json وqa/verification.md.
