---
id: TASK-0120
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0119
issue: none
art_request: none
touches: tools/art_delivery.py,tools/tests/test_art_delivery.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: الأصول الناقصة أو غير المعتمدة أو ذات البصمة الخاطئة ترفض، والمصادر محفوظة، ولا تتغير active manifests تلقائيًا.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# تجهيز إدخال رسوم Codex المعتمدة

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-reviewed-art-intake

## المشكلة المثبتة
ART-0032..0035 مطلوبة؛ أول مرشح جدار تحت TASK-0136 لا يعني اكتمال أو اعتماد المجموعة.

## التنفيذ
استخدم مسار إدخال الرسوم الحالي؛ أضف فقط النواقص المثبتة للتحقق من RGBA والبصمة والمصدر والاتجاه وأبعاد master ونقطة القدم وfootprint والموافقات. حقول غير مقاسة تبقى null/needs_annotation. يمكن اختبار الأداة بfixtures قبل وصول الرسم؛ تسجيل أصول الإنتاج وتفعيلها يتطلب مراجعة مستقلة واعتماد المالك.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0119.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] الأصول الناقصة أو غير المعتمدة أو ذات البصمة الخاطئة ترفض، والمصادر محفوظة، ولا تتغير active manifests تلقائيًا.
- [ ] python -m unittest discover -s tools/tests -p test_art_delivery.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
