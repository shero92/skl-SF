---
id: TASK-0126
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0125
issue: none
art_request: none
touches: scenes/game_factory_actor.gd,scenes/room_companion.gd,tools/verify_room_navigation.gd,tools/tests/test_map_navigation.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_map_navigation.py
done_when: لا عبور للجدران أو الطاولة أو السرير ولا خروج للبحر؛ المدخل والممرات قابلة للوصول والمرافق لا يقطع العوائق.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# إكمال الحركة والتصادم والمرافق

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-room-navigation-collision

## المشكلة المثبتة
بيانات التنقل في v0017 needs_review وتشمل ستة عوائق فقط، ومسارا الحركة الحاليان لا يضمنان تطبيق obstacles والlinks معًا.

## التنفيذ
استخدم بيانات الخريطة الحالية للمشي والعوائق وstair link وحدود الشرفة؛ لا تنفيذ طيران أو سباحة في هذه النسخة. اختبر القدم الكاملة والتصادم أثناء الحركة القطرية. امنع قطع Neru عبر الأثاث باختيار مسار مسموح. افحص مواضع spawn والتفاعل عند تغيير التكوين؛ تحديث بيانات الخريطة عبر نسخة جديدة فقط.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0125.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] لا عبور للجدران أو الطاولة أو السرير ولا خروج للبحر؛ المدخل والممرات قابلة للوصول والمرافق لا يقطع العوائق.
- [ ] python -m unittest discover -s tools/tests -p test_map_navigation.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
