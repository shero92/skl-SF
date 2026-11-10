---
id: TASK-0127
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0119
issue: none
art_request: none
touches: tools/game_factory.py,scenes/game_factory_actor.gd,tools/tests/test_game_factory.py
test: python -m unittest discover -s tools/tests -p test_game_factory.py
done_when: تقرير للشخصيات الست يذكر الأطر المفقودة وغير المعتمدة؛ readiness ترفض الملفات المفقودة والتسلسلات الجزئية والمراجع غير الصالحة.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# توحيد حالة الأصول والتحريكات للشخصيات

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-character-readiness-contract

## المشكلة المثبتة
manifest يسجل تحريكات Hero فقط؛ PosterCharacter يعرض مسارًا آخر من قصاصات ملصقات. complete وحدها لا تثبت اعتماد الأصل.

## التنفيذ
افصل موجود/مقاس/معتمد/قابل للعب. تحقق من كل إطار ومصدره واتجاهه واعتماده؛ لا ترفع قصاصات الملصقات إلى production تلقائيًا. اجعل الحالات الناقصة ترجع خطأ واضحًا بدل إخفاء الشخصية بصمت. حافظ على المصادر الحالية ولا تعطل وضع التشخيص القديم.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0119.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] تقرير للشخصيات الست يذكر الأطر المفقودة وغير المعتمدة؛ readiness ترفض الملفات المفقودة والتسلسلات الجزئية والمراجع غير الصالحة.
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
