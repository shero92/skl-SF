---
id: TASK-0119
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0117
issue: none
art_request: none
touches: map_factory/blueprints/hero_room_01_visual_targets_20261103.json,tools/hero_room_visual_contract.py,tools/tests/test_hero_room_visual_contract.py
test: python -m unittest discover -s tools/tests -p test_hero_room_visual_contract.py
done_when: بصمة المرجع مثبتة، وكل ميزة ممثلة بأصل موثوق أو ART معلوم، مع رفض مراجع خاطئة وعدم إعلان تغطية وهمية.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# اعتماد الصورة الحالية كمرجع وعقد ميزات

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-current-reference-contract

## المشكلة المثبتة
المرجع المرفق الآن بصمته 01d91889…73119c، ويختلف عن مرجع 47a7855c… المستخدم في العقد الحالي. كل required_asset_ids في العقد الحالي فارغة.

## التنفيذ
استخدم النسخة المطابقة الموجودة بالفعل في .agents/planner/goals/GOAL-0001/references/hero_room_reference.png ولا تستبدل المراجع القديمة. حدّث ارتباط المرجع بالمناطق الإحدى عشرة وأضف ربط كل feature بأصل موجود أو ART ناقص. قوائم required_asset_ids الفارغة تبقى نقصًا موثقًا. فرّق image-space عن world-space.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0117.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] بصمة المرجع مثبتة، وكل ميزة ممثلة بأصل موثوق أو ART معلوم، مع رفض مراجع خاطئة وعدم إعلان تغطية وهمية.
- [ ] python -m unittest discover -s tools/tests -p test_hero_room_visual_contract.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
