---
id: TASK-0125
status: blocked
owner: unassigned
agent: claude
priority: high
branch: none
depends_on: TASK-0124
issue: none
art_request: none
touches: scenes/main.gd,scenes/game_factory_demo.gd,tools/verify_room_gameplay.gd,tools/test_map.json
test: python tools/run_tests.py --only godot_map_smoke --only game_factory
done_when: المعاينة واللعب يعرضان نفس النسخة؛ لا قص عند 1536x1024 و1280x720، وحجب الشخصية يتبع العمق.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 assigns all implementation code to Claude Code; Codex produces graphics; room-first six-character 3v3 demo.
---
# توحيد الخريطة ومشهد اللعب والكاميرا

**الهدف:** GOAL-0002. ابدأ بـ docs/CLAUDE_ROOM_GAME_HANDOFF_20261109.md وهذه المهمة وAGENTS.md.

**Source:** goal:GOAL-0002:owner-20261109-unified-playable-room

## المشكلة المثبتة
main يقرأ أحدث غرفة، بينما Game Factory demo يقرأ game_factory/environment/room.json؛ viewport الافتراضي 1536x864 مقابل مرجع 1536x1024.

## التنفيذ
وحّد تحميل البيئة من registry عبر RoomFactory؛ أبق مشاهد المعاينة والتشخيص متاحة. اضبط fit/letterbox متجاوبًا دون قص تكوين الغرفة. ضع اللاعبين ضمن WorldDepthSort إن كان مستخدمًا بدل Entities ذي z ثابت. احتفظ بتوافق بيانات التفاعل القديمة حتى ترحيلها صراحة.

## الحدود والاعتماديات
- Claude Code ينفذ الكود والاختبارات والتكامل فقط. الرسوم بواسطة Codex وimage_gen؛ لا توليد PNG أو قصاصات إنتاجية أو اعتماد فني ذاتي.
- تبدأ بعد دمج واعتماد: TASK-0124.
- تفعيل ART يتطلب تسليمًا ومراجعة واعتماد المالك، حتى إن اجتاز كود الأدوات اختبارات fixtures.
- touches حدود المهمة. تحقق من المسارات عبر INDEX ووسّعها موثقًا قبل التنفيذ إذا ثبتت الحاجة؛ لا تغييرات عشوائية أو مساس بعمل المالك.
- فرع/worktree مستقل ومهمة واحدة نشطة؛ سجل الأداة والنموذج الحقيقيين. لا تشغيل Aider أو تعديل الأتمتة.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## القبول والاختبار
- [ ] المعاينة واللعب يعرضان نفس النسخة؛ لا قص عند 1536x1024 و1280x720، وحجب الشخصية يتبع العمق.
- [ ] python tools/run_tests.py --only godot_map_smoke --only game_factory
- [ ] python tools/run_tests.py --changed، مع عدد اختبارات غير صفري وGodot smoke مناسب.
- [ ] PR وإيصال استهلاك حقيقي؛ unknown عند غياب القياس. لا push إلى main أو اعتماد صور تلقائي.

## حدود الجلسة
سياق محدود و1–3 ملفات مصدر أولًا. 30000 tokens هدف إرشادي وليس ضمان تكلفة أو سقف إنفاق جديد؛ عند التوسع افصل عملًا قابلًا للمراجعة.

## الأدلة والتسليم
- الملفات المتغيرة: لا شيء بعد.
- الاختبارات: لم تنفذ؛ هذا سجل تخطيط لا إنجاز.
- PR: none.
- التالي: التحقق من الاعتماديات ثم حجز المهمة عند جاهزيتها.
