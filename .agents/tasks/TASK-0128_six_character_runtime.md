---
id: TASK-0128
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0126,TASK-0127
issue: none
art_request: ART-0027
touches: scenes/game_factory_actor.gd,scenes/game_factory_demo.gd,game_factory/character_manifest.json,tools/verify_six_character_runtime.gd,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_game_factory.py
done_when: كل شخصية قابلة للاختيار وتتحرك وتعرض الحالات المعتمدة دون fallback يخفي النقص؛ تقرير Godot لكل حالة.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# دمج الشخصيات الست من سجل موحد

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-six-character-runtime

## المشكلة المثبتة
الملفات المتاحة لا تساوي مجموعات تحريك معتمدة؛ بقية الشخصيات مرتبطة بطلب ART-0027 والتسليمات السابقة.

## التنفيذ
اربط فقط مجموعات Hero وCely وNeru وReef Friend وOld Father وTemple Archer المعتمدة. حقق idle/walk بالاتجاهات الأربعة وbattle idle/attack/hurt/defend/defeat لكل شخصية مع sockets للمعدات القابلة للتبديل. لا شخصية سابعة ولا توليد صور بواسطة Claude. إذا فُقدت حالة اذكرها كحاجز فني.

## الحدود والاعتماديات
- بوابة الرسوم المطلوبة: ART-0027؛ لا تفعيل ولا ادعاء إكمال قبل اكتمال المراجعة والاعتماد.
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0126, TASK-0127.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] كل شخصية قابلة للاختيار وتتحرك وتعرض الحالات المعتمدة دون fallback يخفي النقص؛ تقرير Godot لكل حالة.
- [ ] python -m unittest discover -s tools/tests -p test_game_factory.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
