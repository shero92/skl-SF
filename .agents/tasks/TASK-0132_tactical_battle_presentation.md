---
id: TASK-0132
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0131
issue: none
art_request: none
touches: scenes/battle/modular_actor_adapter.gd,scenes/battle/hit_timing_bridge.gd,scenes/battle/tactical_presentation.gd,tools/verify_tactical_presentation.gd,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_battle_hit_timing.py
done_when: نفس الضرر عند معدلات إطارات مختلفة، وإيقاف/إلغاء/إعادة لا يكرر الضربة؛ مشهد المنتج يستخدم أصولًا حقيقية.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# ربط القتال التكتيكي بالعرض الحقيقي

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-tactical-battle-presentation

## المشكلة المثبتة
TASK-0085 موجود؛ preview ما زال StubActor. حركتا Hero موثقتان في TASK-0086/0087 ولا ينبغي تكرارهما.

## التنفيذ
أعد استخدام controller وadapter وcamera وVFX. أمر attack يثبت هوية التنفيذ وأهدافه؛ حدث impact ذو event_id يطبق الضرر مرة، وpreview/seek بلا آثار جانبية. تبديل WPN_HERO_BASIC_SWORD وWPN_IRON_SWORD لا يغير جسم Hero. duration/events تأتي من التعريف المعتمد لا من أرقام قديمة. لا إكمال إنتاجي قبل اعتماد رسوم الطرفين.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0131.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] نفس الضرر عند معدلات إطارات مختلفة، وإيقاف/إلغاء/إعادة لا يكرر الضربة؛ مشهد المنتج يستخدم أصولًا حقيقية.
- [ ] python -m unittest discover -s tools/tests -p test_battle_hit_timing.py
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
