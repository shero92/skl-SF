---
id: TASK-0138
status: blocked
owner: unassigned
agent: codex
priority: high
branch: none
depends_on: TASK-0136
issue: none
art_request: ART-0033
touches: .agents/graphics/deliveries/ART-0033/,.agents/graphics/requests/ART-0033_hero_room_terrace_cliff_edge.md
test: python tools/agent_workflow.py --sources-only
done_when: جميع عناصر الطلب موجودة مع manifest وفحص RGBA وبصمات ومصادر ومراجعة بالحجم الفعلي؛ لا تفعيل دون اعتماد المالك.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 explicitly assigns graphics to Codex and built-in image_gen.
---
# إنتاج حافة الشرفة والجرف

Codex ينتج الرسوم؛ Claude يستلم التسجيل والتكامل تحت TASK-0120 وما بعدها. يعاد استخدام ART-0033 دون طلب ART مكرر.

- العناصر: terrace_edge_straight,terrace_edge_corner_left,terrace_edge_corner_right,cliff_face_front_a,cliff_face_front_b,cliff_face_front_c,cliff_rubble_cluster,foam_at_cliff_base.
- طابق عمق الجرف والدرج بالصورة الحالية؛ لا أرضية أو بحر مدمجان في قطع العمارة.
- image_gen المدمج فقط؛ طلب واحد لكل عنصر/اتجاه وPNG مستقل مع حفظ المصدر دون تعديل.
- مرجع الحكم .agents/planner/goals/GOAL-0001/references/hero_room_reference.png؛ SHA256 01d918892ae29899f8277e590409588db5371e0019ea2c2e4ebb30f60073119c.
- مرجع الأسلوب assets_hd/architecture/arch/arch_01.png وassets_hd/RULES.md؛ إضاءة أعلى اليسار والمنظور نفسه.
- المصادر H:/shining force/pixel-art/TASK-0138/ART-0033/v001/source/ وتسليم portable داخل touches. استخدم إصدارًا جديدًا إذا سبق وجوده.
- تحقق من الأبعاد وRGBA وalpha وعدم القص والبصمات؛ المجهول null/needs_annotation. عيوب الأسلوب تسجل؛ الاختبار التقني ليس اعتمادًا فنيًا.
- لا تعديل أصول معتمدة أو كود اللعبة ولا ظلال أرضية مدمجة.
- delivered لا توضع حتى اكتمال المجموعة، reviewed للمراجعة المستقلة، integrated بعد اعتماد وتكامل Claude.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## الأدلة والتسليم
- الملفات: بقية المجموعة لم تنتج بعد.
- PR: none.
- التالي: بعد دمج TASK-0136 وتفرغ عمل Codex الجاري، احجز المهمة في worktree مستقل.
