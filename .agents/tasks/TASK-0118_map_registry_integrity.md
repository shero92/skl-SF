---
id: TASK-0118
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0117
issue: none
art_request: none
touches: tools/map_factory_cli.py,tools/hero_room_capture_evidence.py,tools/tests/test_hero_room_capture_evidence.py,docs/CLAUDE_ROOM_GAME_STATUS_20261109.md
test: python -m unittest discover -s tools/tests -p test_hero_room_capture_evidence.py
done_when: البصمتان موثقتان ومختبرتان، بلا إصلاح وهمي أو كسر توافق أو تغيير التاريخ.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# توضيح عقد بصمات JSON والملف في الأدلة

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-map-registry-integrity

## المشكلة المثبتة
السجل سليم؛ canonical digest مختلف مشروعًا عن بصمة بايتات الملف. لا عيب فساد مثبت.

## التنفيذ
وثق digest_json مقابل SHA256 لبايتات الملف. أضف اختبار اختلاف التنسيق، وبيّن نوع البصمة في provenance عند الحاجة دون تغيير معنى snapshot_sha256 أو تعديل registry الصحيح.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0117.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] البصمتان موثقتان ومختبرتان، بلا إصلاح وهمي أو كسر توافق أو تغيير التاريخ.
- [ ] python -m unittest discover -s tools/tests -p test_hero_room_capture_evidence.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
