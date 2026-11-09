---
id: TASK-0123
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0122
issue: none
art_request: ART-0034
touches: scenes/ocean_background.gd,map_factory/scripts/shadow_painter.gd,tools/tests/test_map_factory_tools.py
test: python -m unittest discover -s tools/tests -p test_map_factory_tools.py
done_when: خلفية متصلة بلا حدود قطع واضحة، وظلال منفصلة لا تتكرر ولا تطمس الأرض، مع لقطة مقارنة حقيقية.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# معايرة البحر والإضاءة والظلال

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-sea-light-shadow-calibration

## المشكلة المثبتة
أفق البحر متكرر وحاد، وخطوط الضوء والظلال في v0017 قوية ومتكررة. أدوات الظلال ومسابح الضوء موجودة.

## التنفيذ
عاير إعدادات الخريطة أولًا؛ عدّل renderer فقط لعيب مثبت. استخدم ART-0034 للصخور والأقواس البعيدة، واحتفظ بالماء الحالي ما لم يثبت نقصه. اضبط عمق الخلفية والضوء الدافئ من أعلى اليسار وظلال التلامس والظلال التابعة لأصحابها وتوهج الفوانيس. وسّع touches إلى بيانات النسخة الجديدة فقط عند الحاجة.

## الحدود والاعتماديات
- بوابة الرسوم المطلوبة: ART-0034؛ لا تفعيل ولا ادعاء إكمال قبل اكتمال المراجعة والاعتماد.
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0122.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] خلفية متصلة بلا حدود قطع واضحة، وظلال منفصلة لا تتكرر ولا تطمس الأرض، مع لقطة مقارنة حقيقية.
- [ ] python -m unittest discover -s tools/tests -p test_map_factory_tools.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
