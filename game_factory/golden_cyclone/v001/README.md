# Golden Cyclone — مصادر مستقلة قيد الإنتاج

السياسة الملزمة: [GRAPHICS_PRODUCTION_POLICY.md](../../../docs/GRAPHICS_PRODUCTION_POLICY.md). طلب المالك الأصلي محفوظ حرفيًا في owner_request.txt.

## مواقع الملفات

- الجسم: assets/characters/hero/battle/golden_cyclone/v001/source_frames/hero_golden_cyclone_NNN.png؛ كل ملف طلب توليد مستقل كامل الجودة، بلا تقطيع ورقة أو تكبير قصاصة.
- المرشحات المرفوضة: assets/characters/hero/battle/golden_cyclone/v001/rejected_sources/؛ تحفظ أسباب الرفض في manifest.json ولا تحذف.
- النسخة الدائمة: H:/shining force/pixel-art/TASK-0074/ART-0029/v001/.
- الطلبات الفعلية: requests/؛ بيانات الملفات الفعلية: manifest.json؛ تخطيط الوضعيات والتوقيت: motion_spec.json؛ إصلاح Phantom Dash: regeneration_queue.json.
- نتيجة فحوص المشروع وحدودها: qa/verification_summary.md. يثبت generated_frame_count عدد الملفات التي حُفظت وفُحصت، ولا يعني اعتمادها.

## حدود الاستخدام

الحالة needs_review وليست جاهزية للعبة. source_frames ملفات المصدر الأصلية؛ لم تنتج game_frames بتصغير آلي غير مراجع. قيم weapon sockets وground anchors تبقى null حتى القياس والتجربة؛ لا يستخدم هذا الـmanifest كبديل لسجل الأصول النشطة.

لا يفعّل Golden Cyclone في main أو game_factory/character_manifest.json قبل اكتمال الجودة وموافقة المالك. واجهة golden_cyclone المقترحة في motion_spec.json ليست إعلانًا عن وجود مشغّل لها. لا يوجد GIF أو Sprite Sheet أو Godot preview جديد حتى تنشأ الملفات فعليًا وتوثق.

لا تُنسب فحوص المشروع الحالية أو إيصال تبديل السيفين لـTASK-0070 إلى الحركة الجديدة. Codex أنتج الرسوم والسياسات والتدقيق فقط؛ لا كود أو سكربت أو اختبار أو إعداد أتمتة جديد في هذه المهمة.
