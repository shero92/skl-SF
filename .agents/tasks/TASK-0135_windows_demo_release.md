---
id: TASK-0135
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0134,TASK-0086,TASK-0087
issue: none
art_request: none
touches: export_presets.cfg,tools/verify_demo_e2e.gd,docs/DEMO_RELEASE_20261109.md,tools/test_map.json
test: python tools/run_tests.py --all
done_when: بناء Windows يعمل من مسار نظيف بلا موارد مفقودة أو placeholders؛ تقرير نجاح وفشل واقعي وروابط PR/captures.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# التحقق الشامل وبناء Windows قابل للتجربة

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-windows-demo-release

## المشكلة المثبتة
لا دليل حالي على نسخة متكاملة تضم الاستكشاف والشخصيات الست والتدريب والحفظ بعد إعادة التشغيل.

## التنفيذ
أضف preset Windows دون أسرار أو تغييرات آلية في التوزيع. تحقق من clean clone: import، الاختبارات، دخول الغرفة، الشخصيات، تدريب وفوز وخسارة، عودة وحفظ وإعادة تشغيل وتحميل. التقط البيئة فقط واللعب والقتال مع commit ونسخة وبصمات. أرفق مخرجات build وتعليمات التشغيل والقيود. لا إعلان الإصدار مكتملًا إذا حُجبت الرسوم.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0134.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] بناء Windows يعمل من مسار نظيف بلا موارد مفقودة أو placeholders؛ تقرير نجاح وفشل واقعي وروابط PR/captures.
- [ ] python tools/run_tests.py --all
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
