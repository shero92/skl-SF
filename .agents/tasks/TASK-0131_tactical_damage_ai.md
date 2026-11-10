---
id: TASK-0131
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0130
issue: none
art_request: none
touches: scenes/battle/tactical_state.gd,scenes/battle/training_ai.gd,tools/verify_training_ai.gd,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: نفس الأوامر تنتج نفس الحالة، لا هجوم خارج المدى ولا ضرر مزدوج، والفوز/الخسارة يتحققان مرة واحدة.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# ضرر حتمي وخصم تدريب آلي

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-tactical-damage-ai

## المشكلة المثبتة
بنية hit timing موجودة، لكن العرض لا يساوي قواعد HP أو منطق خصم قابل للعب.

## التنفيذ
ابدأ hp=100 وضرر=20 ومدى Manhattan=1؛ الدفاع يخفض الضرر إلى النصف حتى بداية تفعيل الوحدة التالية. الخصم يستهدف أقرب وحدة حية بمسار BFS ثم character_id لكسر التعادل، ويهاجم إن وصل وإلا يتحرك أو ينتظر. اقرأ القيم من تعريف encounter قابل للضبط. عالج الفوز والخسارة ووحدات hp=0؛ لا RNG أو خبرة أو غنائم.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0130.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] نفس الأوامر تنتج نفس الحالة، لا هجوم خارج المدى ولا ضرر مزدوج، والفوز/الخسارة يتحققان مرة واحدة.
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
