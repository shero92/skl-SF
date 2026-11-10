---
id: TASK-0122
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0121
issue: none
art_request: ART-0035
touches: tools/build_hero_room_blueprint.py,tools/room_assembly.py,tools/tests/test_hero_room_reference_relayout.py
test: python -m unittest discover -s tools/tests -p test_hero_room_reference_relayout.py
done_when: الأثاث مؤرض وذو اتجاه صحيح، الزينة مثبتة على مضيفها، وكل نقص مرئي مرتبط بطلب فني محدد.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# ضبط الأثاث والزينة حسب المرجع

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-room-furniture-dressing

## المشكلة المثبتة
حجم السرير والسجاد واتجاه الطاولة والرفوف والتفاصيل الصغيرة في v0017 لا يطابق التكوين.

## التنفيذ
اضبط مجموعتي النوم يسارًا والعمل يمينًا، نقاط القدم والدعم والمقاييس والسجاد والرفوف والأواني والكتب والخريطة والفوانيس والنباتات. استخدم ART-0035 وما يثبت صلاحيته من المكتبة. أعد استخدام ART-0007..0021 للعناصر الناقصة قبل طلب جديد. احفظ ممر الحركة والبوصلة دون حجب.

## الحدود والاعتماديات
- بوابة الرسوم المطلوبة: ART-0035؛ لا تفعيل ولا ادعاء إكمال قبل اكتمال المراجعة والاعتماد.
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0121.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] الأثاث مؤرض وذو اتجاه صحيح، الزينة مثبتة على مضيفها، وكل نقص مرئي مرتبط بطلب فني محدد.
- [ ] python -m unittest discover -s tools/tests -p test_hero_room_reference_relayout.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
