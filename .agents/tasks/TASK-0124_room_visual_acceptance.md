---
id: TASK-0124
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0123
issue: none
art_request: none
touches: tools/hero_room_capture_evidence.py,docs/previews/map_factory_renders/,docs/CLAUDE_ROOM_GAME_STATUS_20261109.md
test: python -m unittest discover -s tools/tests -p test_hero_room_capture_evidence.py
done_when: لقطة بيئة فقط وإيصال قابلان لإعادة الإنتاج دون موارد مفقودة؛ كل فرق موثق؛ الاعتماد لا يتغير إلا بإذن المالك.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# تسليم دليل مطابقة الغرفة

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-room-visual-acceptance

## المشكلة المثبتة
إيصال v0017 مرتبط بشجرة dirty؛ الاختبار الآلي والمقارنة اللونية لا يثبتان التشابه أو الاعتماد.

## التنفيذ
التقط من checkout نظيف ومثبت commit عبر Godot وMap Factory عند 1536x1024، وحقق مرجع الصورة الحالية ونسخة الخريطة وبصمات الموارد. أخرج مقارنة وملاحظات matched/partial/missing للمناطق الإحدى عشرة؛ أرقام اللون والحواف إرشادية فقط. اطلب مراجعة المالك للصورة الناتجة دون تعيين approved ذاتيًا.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0123.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] لقطة بيئة فقط وإيصال قابلان لإعادة الإنتاج دون موارد مفقودة؛ كل فرق موثق؛ الاعتماد لا يتغير إلا بإذن المالك.
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
