---
id: TASK-0133
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0130,TASK-0132
issue: none
art_request: none
touches: scenes/battle/training_ui.gd,scenes/battle/training.tscn,tools/verify_training_ui.gd,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: لا يقبل زرًا غير قانوني أو إدخال الاستكشاف أثناء القتال؛ يستطيع اللاعب إكمال تدريب ثم العودة للغرفة.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# واجهة التدريب والتفاعل مع حلقة اللعب

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-training-player-ui

## المشكلة المثبتة
واجهة battle_preview تشخيصية وليست واجهة اختيار حركة ووحدة ونتيجة تكتيكية.

## التنفيذ
استخدم Controls والرسوم الموجودة لعرض الوحدات وHP والفريق والدور وخلايا الحركة والهجوم والدفاع والانتظار والنتيجة والعودة. أضف دخول التدريب من الغرفة عبر تفاعل واضح. لا تنتج UI art ولا تعدل عمل المالك الجاري في dialogue_ui.gd. إن لزم وصل main حدّث touches قبل التنفيذ.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0130, TASK-0132.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] لا يقبل زرًا غير قانوني أو إدخال الاستكشاف أثناء القتال؛ يستطيع اللاعب إكمال تدريب ثم العودة للغرفة.
- [ ] python tools/run_tests.py --changed
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
