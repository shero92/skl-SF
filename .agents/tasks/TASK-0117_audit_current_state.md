---
id: TASK-0117
status: todo
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: none
issue: none
art_request: none
touches: map_factory/maps/hero_room_01/recovery_queue_audit.json,docs/CLAUDE_ROOM_GAME_STATUS_20261109.md
test: python -m unittest discover -s tools/tests -p test_agent_workflow.py
done_when: تقرير بأدلة commits لكل حالة وحدود التحقق وخطوة تالية واحدة لكل عائق.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# تدقيق حالة المشروع والمهام الحالية

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-audit-current-state

## المشكلة المثبتة
اللوحات القديمة تتوقف عند TASK-0103 بينما الكود وصل إلى v0017 وTASK-0116؛ توجد بيانات تاريخية غير محدثة.

## التنفيذ
مطابقة commits وPRs لكل TASK-0090..0116، وإثبات الموجود والمختبر وما ينتظر الاعتماد. سجل حالة dirty مستقلة قبل أي تعديل ولا تنقل تغييرات المالك. اقترح تحديث السجلات غير المكتملة دون إعادة تنفيذ الكود.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- جاهزة بعد فحص التعارضات وحجز worktree.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

## القبول والاختبار
- [ ] تقرير بأدلة commits لكل حالة وحدود التحقق وخطوة تالية واحدة لكل عائق.
- [ ] python -m unittest discover -s tools/tests -p test_agent_workflow.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
