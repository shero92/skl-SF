# TASK-0159 — السرير المزدوج والجزر الصخرية

المجلد الفعلي: `H:/shining force/skl-SF/.worktrees/art-bed-sea-stacks/`.
الفرع: `codex/art-0048-0049-bed-stacks`؛ العمل معزول، ونسخة المالك الرئيسية لم تُكتب. Agent: codex. Tool: built-in image_gen. Model/tokens/cost: unknown. لا API خارجي أو Aider أو توليد إجرائي بديل.

- ART-0048: مصدر سرير1178×1335، معاينة255×290، ملفات التسليم والبيانات كاملة. الحالة delivered، دون تكامل داخل الغرفة.
- ART-0049: مصدر قوس1717×916 ومعاينة300×160 صالحان تقنيًا. المحاولة الأولى1774×887 محفوظة بسبب فراغ علوي كبير وجرف منخفض عند التصغير.
- ART-0049: مجموعة الأعمدة الستة2117×743 أقل من شرط2104×760؛ احتفظنا بها في rejected ومعاينة منفصلة، ولم ننشئ الملف النهائي المطلوب. الطلب requested والمهمة blocked حتى يحل شرط الدقة. لا تكبير/حشو للمصدر أو تعديل صامت للحجم المطلوب.

الموافقة البصرية تلقائية بقرار المالك، أما نجاح شروط المصادر وتكامل الخريطة فحالات مستقلة. `production_active=false` لجميع ملفات هذه الحزمة. لا تعديل للأصول السابقة أو أجزاء الخريطة أو ملفات Golden Cyclone. هامش القوس الأيمن alpha128 يبلغ7px فقط؛ أضيق من3% الإرشادية، دون قص مرئي، ومذكور في بياناته.

## العثور على القطع واستعمالها

- `game_factory/environment/ART-0048/v001/README.md` و`manifest.json`: السرير، مسار master ونسخة التسليم وSHA-256 وأبعاد PNG وalpha والارتكاز والمقياس وأمر التوليد.
- `game_factory/environment/ART-0049/v001/README.md` و`manifest.json`: القوس والمجموعة المتعطلة والمحاولة غير المختارة، بأسبابها وبصماتها.
- `generation_records.json`: أربع استدعاءات مستقلة، مصدر كل نتيجة داخل المشروع وتطابق بايتاته مع خرج الأداة؛ مسارات cache للتوثيق فقط وليست اعتمادًا للتسليم.
- `map_factory/metadata/source_art_index.json` و`docs/SOURCE_ART_CATALOG.md`:147 سجلًا، بلا PNG غير مفهرس ضمن مجموعات المصادر المدققة. هذا فهرس مصادر، ولا يمنح runtime ID أو ينشئ placement. الحزمة تضيف4سجلات (مصدران صالحان ومحاولتان غير مختارتين).
- سياق فروع PR179/182/185/188 السابقة نُسخ محليًا للقراءة والتدقيق فقط، بعد فحص إيصالات SHA؛ لا يدخل ضمن ملفات المهمة أو إيصالها. عند إعادة بناء الفهرس من clone مستقل يلزم تجميع تلك الفروع إن لم تكن دُمجت بعد؛ publication يحدد مكان كل manifest.

حجم Canvas ليس footprint. مواضع origin وnative_origin مقاسة في نظام إحداثيات كل صورة، ولا يُعاد استخدام source origin مباشرة مع نسخة اللعبة. التصادم وحجب الشخصيات ومواضع تثبيت الغرفة null/غير معايرة. ينبغي للمكامل إنشاء sprite/runtime ID جديد ومعايرة موضعه دون إعادة كتابة تاريخ الخرائط.

## إعادة التحقق

نفذ من جذر نسخة عمل المهمة:

```powershell
python game_factory/environment/bed_stacks_20261111/prepare_review.py
# Godot configured executable:
# --path . --rendering-method gl_compatibility --script res://game_factory/environment/bed_stacks_20261111/review.gd
python game_factory/environment/bed_stacks_20261111/verify_delivery.py
python tools/source_art_catalog.py --root . --check
python tools/graphics_validation.py --changed
python tools/run_tests.py --changed --timeout 120
python tools/run_tests.py --check-index --sources-only
python game_factory/environment/bed_stacks_20261111/finish_delivery.py
```

الـ PNG باسم godot_native_review التُقط من viewport حقيقي لمحرك Godot4.7.2، مع native1x و2x ومرجع مستقل؛ ليس تركيبًا ببايثون أو إثبات تكامل بالغرفة. تحذير Image.load_from_file يخص تحميل صور المراجعة خارج مسار export، ولا ندعي أنها runtime export جاهز. إيصال المحرك يربط manifest والسكريبت واللقطة ببصماتها.

النتائج الفعلية محفوظة في `test_results.json`. graphics_validation يفحص مسارات الإنتاج فقط وأعاد png_checked=0 لهذه المصادر HD؛ فحص الصور الجديدة نفذته أداتا prepare_review وverify_delivery، مع مراجعة لقطتي Godot. فشل بوابة ارتفاع المجموعة يظل مسجلًا حتى لو نجحت اختبارات الكود جميعها. `delivery_receipt.json` يسرد ملفات هذه المهمة فقط وبصماتها، ولا يسرد نفسه أو إيصال التكلفة الآلي.
