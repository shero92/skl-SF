---
id: TASK-0137
status: blocked
owner: unassigned
agent: codex
priority: high
branch: none
depends_on: TASK-0136
issue: none
art_request: ART-0032
touches: .agents/graphics/deliveries/ART-0032/,.agents/graphics/requests/ART-0032_hero_room_connected_ruin_walls.md
test: python tools/agent_workflow.py --sources-only
done_when: جميع عناصر الطلب موجودة مع manifest وفحص RGBA وبصمات ومصادر ومراجعة بالحجم الفعلي؛ لا تفعيل دون اعتماد المالك.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 explicitly assigns graphics to Codex and built-in image_gen.
---
# إنتاج بقية مجموعة الجدران المتصلة

Codex ينتج الرسوم؛ Claude يستلم التسجيل والتكامل تحت TASK-0120 وما بعدها. يعاد استخدام ART-0032 دون طلب ART مكرر.

- العناصر: wall_straight_long_b,wall_corner_outer_left,wall_corner_outer_right,wall_corner_inner_left,wall_corner_inner_right,wall_side_left_run,wall_side_right_run,parapet_cap_run.
- أول wall_straight_long_a موجود كمرشح تحت TASK-0136؛ لا تعِد إنتاجه دون سبب مراجعة. بقية المجموعة مستقلة، واتجاهاتها مرسومة لا معكوسة.
- image_gen المدمج فقط؛ طلب واحد لكل عنصر/اتجاه وPNG مستقل مع حفظ المصدر دون تعديل.
- مرجع الحكم .agents/planner/goals/GOAL-0001/references/hero_room_reference.png؛ SHA256 01d918892ae29899f8277e590409588db5371e0019ea2c2e4ebb30f60073119c.
- مرجع الأسلوب assets_hd/architecture/arch/arch_01.png وassets_hd/RULES.md؛ إضاءة أعلى اليسار والمنظور نفسه.
- المصادر H:/shining force/pixel-art/TASK-0137/ART-0032/v001/source/ وتسليم portable داخل touches. استخدم إصدارًا جديدًا إذا سبق وجوده.
- تحقق من الأبعاد وRGBA وalpha وعدم القص والبصمات؛ المجهول null/needs_annotation. عيوب الأسلوب تسجل؛ الاختبار التقني ليس اعتمادًا فنيًا.
- لا تعديل أصول معتمدة أو كود اللعبة ولا ظلال أرضية مدمجة.
- delivered لا توضع حتى اكتمال المجموعة، reviewed للمراجعة المستقلة، integrated بعد اعتماد وتكامل Claude.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## الأدلة والتسليم
- الملفات: بقية المجموعة لم تنتج بعد.
- PR: none.
- التالي: بعد دمج TASK-0136 وتفرغ عمل Codex الجاري، احجز المهمة في worktree مستقل.
