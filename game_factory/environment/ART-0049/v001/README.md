# ART-0049 — مصادر وبيانات القطع

Agent: codex. Tool: built-in image_gen. Model, tokens and cost: unknown.

المسارات التالية نسبة إلى جذر نسخة عمل المهمة `H:/shining force/skl-SF/.worktrees/art-bed-sea-stacks/`؛ لا يعتمد التسليم على cache أداة التوليد. الفرع `codex/art-0048-0049-bed-stacks`، ولا توجد ملفات جديدة في نسخة المالك الرئيسية.

الموافقة البصرية تلقائية وفق قرار المالك؛ `production_active=false`، والتكامل داخل الغرفة ومعايرة الحجب والتصادم لم ينفذا.

| القطعة | المسار | SHA-256 | الحالة |
| --- | --- | --- | --- |
| hero_sea_stack_arch_island | `assets_hd/background/sea_stack_islands/v001/hero_sea_stack_arch_island.png` | `89450e80606e40492d83530bacb3f989d52204c016bd4c96a316135343689bcf` | needs_map_calibration |
| hero_sea_stack_cluster | `assets_hd/background/sea_stack_islands/v001/rejected/hero_sea_stack_cluster_attempt_01.png` | `8bc8f4d93b6477c8816d86583b74ac28ee17447d9f944f1bef06b29f0d83a577` | needs_regeneration |
| hero_sea_stack_arch_island_attempt_01 | `assets_hd/background/sea_stack_islands/v001/rejected/hero_sea_stack_arch_island_attempt_01.png` | `78d9a01060a58b14bfcd56036814aae57f5c12c6f2b231b7d0906ab74b0057b4` | not_selected |

القياسات والشفافية والارتكاز ومعاينات PNG في `manifest.json`، ومصدر كل أمر توليد في `requests/`. origin مقاس عند منتصف أسفل حدود alpha128؛ `native_origin` لنسخة المعاينة. لا تستنتج footprint أو collision من أبعاد الصورة. القيم غير المقاسة null.

معاينة اللعبة من المصدر الكامل دون قص: تصغير موحد بنسبة واحدة، Nearest Neighbor، ثم حشو شفاف للوصول إلى Canvas المطلوب؛ لا تكبير للمصدر ولا عكس/تدوير. مصادر PNG تحفظ كما أنتجتها الأداة. مؤثرات RGB المخفية تحت alpha0 ليست إطارًا مرئيًا؛ لقطة Godot تعرض المزج الحقيقي.

المعاينة الفعلية `godot_native_review.png`، وإثبات المحرك وبصمات المصدر/السكريبت/اللقطة `godot_review_receipt.json`. أداة التحقق `game_factory/environment/bed_stacks_20261111/verify_delivery.py` من جذر نسخة العمل، وليست تكاملًا في خريطة الغرفة.

الفهرسة: `map_factory/metadata/source_art_index.json` و`docs/SOURCE_ART_CATALOG.md`؛ ابحث بمعرّف ART. الفهرس يجمع سياق فروع التسليم السابقة أيضًا؛ هذه السياقات ليست ملفات منتجة ضمن هذه المهمة ولا تدخل commit. الوكيل المستهلك يحتاج دمج/جلب فروع السياق لإعادة بناء الفهرس الكامل من clone مستقل.

تسليم جزئي فقط: القوس1717×916 صالح لمعاينة300×160؛ حدود alpha128 داخل Canvas، لكن الهامش الأيمن7px أضيق من الهامش التقريبي3%. فتحة النفق شفافة، ومواقع عينات الشفافية موثقة.

المحاولة الأولى للقوس1774×887 غير مختارة بسبب فراغ علوي كبير وجرف منخفض في المعاينة. احتفظنا بها ولم تُقص أو تُستخدم كأصل نهائي.

مجموعة الأعمدة الستة2117×743، المطلوب2104×760 لمعاينة526×190. ارتفاعها ينقص17px؛ مصدرها في rejected، ولا يوجد ملف نهائي بالاسم المطلوب. لا تقبل هذه المحاولة كجاهزة تقنيًا رغم موافقة المالك البصرية. لا تكبير أو padding لإيهام اجتياز4x. لا تتكرر المحاولة بنفس قيود الأداة قبل توفر مسار توليد يحقق الأبعاد دون تكبير أو تعديل مالك صريح للمواصفة.
