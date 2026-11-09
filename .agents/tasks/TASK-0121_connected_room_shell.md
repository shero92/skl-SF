---
id: TASK-0121
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0118,TASK-0120
issue: none
art_request: ART-0032
touches: tools/build_hero_room_blueprint.py,tools/room_assembly.py,tools/tests/test_hero_room_reference_relayout.py,map_factory/maps/hero_room_01/
test: python -m unittest discover -s tools/tests -p test_hero_room_reference_relayout.py
done_when: غرفة ذات silhouette متصل وقوس مفتوح ودرج يصل الشرفة بصريًا وفيزيائيًا؛ نسخة جديدة فقط؛ report لكل عائق فني.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# تركيب الجدران والشرفة والجرف والدرج

**الهدف:** GOAL-0001. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0001:owner-20261109-connected-room-shell

## المشكلة المثبتة
لقطة v0017 تظهر قطع جدران منفصلة وأرضية عائمة؛ مولدا map_wall_generator وmap_terrace_edge موجودان.

## التنفيذ
أعد استخدام المولدات الحالية والأصول المعتمدة من ART-0032 وART-0033. صل الجدران بالزوايا والقوس والباب، أضف عمق الجرف والحافة غير المنتظمة ومدخل الدرج المركزي. لا تمدد قطعة أو تقلبها لاختلاق منظور. انشر النسخة التالية من أحدث revision عبر CLI؛ دوّن المسارات المولدة الدقيقة في touches عند التنفيذ.

## الحدود والاعتماديات
- بوابة الرسوم المطلوبة: ART-0032,ART-0033؛ لا تفعيل ولا ادعاء إكمال قبل اكتمال المراجعة والاعتماد.
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0118, TASK-0120.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] غرفة ذات silhouette متصل وقوس مفتوح ودرج يصل الشرفة بصريًا وفيزيائيًا؛ نسخة جديدة فقط؛ report لكل عائق فني.
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
