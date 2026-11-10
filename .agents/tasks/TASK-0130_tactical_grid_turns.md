---
id: TASK-0130
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0129
issue: none
art_request: none
touches: scenes/battle/tactical_state.gd,scenes/battle/tactical_grid.gd,tools/verify_tactical_turns.gd,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: اختبارات حتمية للحركة والمدى والاحتلال وإلغاء الاختيار وإتمام الجولة ومنع التصرف المزدوج.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# الشبكة التكتيكية والحركة والأدوار

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-tactical-grid-turns

## المشكلة المثبتة
الموجود محرك عرض حركات ومعاينة؛ لم توجد وحدة شبكة وأدوار تكتيكية في الفحص.

## التنفيذ
نفذ encounter تدريب من ست وحدات على شبكة 8x6، بلا عوائق ثابتة أولية؛ الخلايا المشغولة تمنع المرور. فريق Hero/Cely/Neru في x=1 وy=1,2,3؛ الآخر في x=6 ونفس الصفوف. حركة متعامدة حتى 4 خلايا ببحث BFS؛ حركة واحدة ثم attack/defend/wait تنهي دور الوحدة. يتناوب الفريقان بعد اكتمال أفعال وحداتهما، وترتيب الاختيار ضمن الفريق حر. الوحدات ذات hp=0 لا تتحرك أو تشغل خلية.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0129.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] اختبارات حتمية للحركة والمدى والاحتلال وإلغاء الاختيار وإتمام الجولة ومنع التصرف المزدوج.
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
