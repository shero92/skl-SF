# ART-0048 — مصادر وبيانات القطع

Agent: codex. Tool: built-in image_gen. Model, tokens and cost: unknown.

المسارات التالية نسبة إلى جذر نسخة عمل المهمة `H:/shining force/skl-SF/.worktrees/art-bed-sea-stacks/`؛ لا يعتمد التسليم على cache أداة التوليد. الفرع `codex/art-0048-0049-bed-stacks`، ولا توجد ملفات جديدة في نسخة المالك الرئيسية.

الموافقة البصرية تلقائية وفق قرار المالك؛ `production_active=false`، والتكامل داخل الغرفة ومعايرة الحجب والتصادم لم ينفذا.

| القطعة | المسار | SHA-256 | الحالة |
| --- | --- | --- | --- |
| hero_double_bed_south | `assets_hd/furniture/double_bed_south/v001/hero_double_bed_south.png` | `1bd929fef9e2d9cbd84bb7fc2376bd0b53a7ea4704e27ba654869fb76d0da3ba` | needs_map_calibration |

القياسات والشفافية والارتكاز ومعاينات PNG في `manifest.json`، ومصدر كل أمر توليد في `requests/`. origin مقاس عند منتصف أسفل حدود alpha128؛ `native_origin` لنسخة المعاينة. لا تستنتج footprint أو collision من أبعاد الصورة. القيم غير المقاسة null.

معاينة اللعبة من المصدر الكامل دون قص: تصغير موحد بنسبة واحدة، Nearest Neighbor، ثم حشو شفاف للوصول إلى Canvas المطلوب؛ لا تكبير للمصدر ولا عكس/تدوير. مصادر PNG تحفظ كما أنتجتها الأداة. مؤثرات RGB المخفية تحت alpha0 ليست إطارًا مرئيًا؛ لقطة Godot تعرض المزج الحقيقي.

المعاينة الفعلية `godot_native_review.png`، وإثبات المحرك وبصمات المصدر/السكريبت/اللقطة `godot_review_receipt.json`. أداة التحقق `game_factory/environment/bed_stacks_20261111/verify_delivery.py` من جذر نسخة العمل، وليست تكاملًا في خريطة الغرفة.

الفهرسة: `map_factory/metadata/source_art_index.json` و`docs/SOURCE_ART_CATALOG.md`؛ ابحث بمعرّف ART. الفهرس يجمع سياق فروع التسليم السابقة أيضًا؛ هذه السياقات ليست ملفات منتجة ضمن هذه المهمة ولا تدخل commit. الوكيل المستهلك يحتاج دمج/جلب فروع السياق لإعادة بناء الفهرس الكامل من clone مستقل.

السرير جنوبًا: الوسائد عند رأسه شمالًا، والقدم باتجاه الكاميرا. المصدر1178×1335 يتجاوز1020×1160؛ المعاينة255×290. أربعة أعمدة، وسادتان بيضاوان، وسادة زرقاء، لحاف بوصلة. لا أثاث مجاور أو ظل أرضي.
