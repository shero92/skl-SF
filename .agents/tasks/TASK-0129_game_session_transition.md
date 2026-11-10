---
id: TASK-0129
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0128
issue: none
art_request: none
touches: scenes/game_session.gd,scenes/main.gd,tools/verify_game_session.gd,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: دخول وخروج وإلغاء متكررة دون تكرار عقد أو فقد بيانات أو إدخال نشط في المشهد المخفي.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# حالة جلسة مشتركة وانتقال التدريب

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-game-session-transition

## المشكلة المثبتة
توجد context محلية داخل demo، لكن لا جلسة موحدة للغرفة والفريق والمعركة التدريبية.

## التنفيذ
أضف GameSession ببيانات character_id وteam وhp وequipment وposition وfacing وmap_id/version وtraining_completed. اجعل الانتقال exploration -> training -> results -> exploration صريحًا؛ جمّد إدخال الاستكشاف واستعد الموقع والاتجاه والحالة عند العودة أو الإلغاء، ولا تنسخ الضرر عبر مصدرين.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0128.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] دخول وخروج وإلغاء متكررة دون تكرار عقد أو فقد بيانات أو إدخال نشط في المشهد المخفي.
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
