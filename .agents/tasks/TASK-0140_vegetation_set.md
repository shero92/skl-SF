---
id: TASK-0140
status: blocked
owner: unassigned
agent: codex
priority: high
branch: none
depends_on: TASK-0136
issue: none
art_request: ART-0035
touches: .agents/graphics/deliveries/ART-0035/,.agents/graphics/requests/ART-0035_hero_room_planters_flowers_palms.md
test: python tools/agent_workflow.py --sources-only
done_when: جميع عناصر الطلب موجودة مع manifest وفحص RGBA وبصمات ومصادر ومراجعة بالحجم الفعلي؛ لا تفعيل دون اعتماد المالك.
started_at: unknown
cost_usd: unknown
scope_approval: Owner 2026-11-09 explicitly assigns graphics to Codex and built-in image_gen.
---
# إنتاج النباتات والأزهار وأحواض الزراعة

Codex ينتج الرسوم؛ Claude يستلم التسجيل والتكامل تحت TASK-0120 وما بعدها. يعاد استخدام ART-0035 دون طلب ART مكرر.

- العناصر: planter_stone_flowers_large,planter_stone_flowers_medium,palm_clump_front_left,palm_clump_front_right,flower_mound_white,flower_mound_blue,ivy_tuft_wall_a,ivy_tuft_wall_b,hanging_vine_long.
- كل عنصر منفصل بخلفية مناسبة؛ الاتجاه المقابل أصل مستقل لا قلب bitmap، ولا توليد مجموعة في صورة واحدة.
- image_gen المدمج فقط؛ طلب واحد لكل عنصر/اتجاه وPNG مستقل مع حفظ المصدر دون تعديل.
- مرجع الحكم .agents/planner/goals/GOAL-0001/references/hero_room_reference.png؛ SHA256 01d918892ae29899f8277e590409588db5371e0019ea2c2e4ebb30f60073119c.
- مرجع الأسلوب assets_hd/architecture/arch/arch_01.png وassets_hd/RULES.md؛ إضاءة أعلى اليسار والمنظور نفسه.
- المصادر H:/shining force/pixel-art/TASK-0140/ART-0035/v001/source/ وتسليم portable داخل touches. استخدم إصدارًا جديدًا إذا سبق وجوده.
- تحقق من الأبعاد وRGBA وalpha وعدم القص والبصمات؛ المجهول null/needs_annotation. عيوب الأسلوب تسجل؛ الاختبار التقني ليس اعتمادًا فنيًا.
- لا تعديل أصول معتمدة أو كود اللعبة ولا ظلال أرضية مدمجة.
- delivered لا توضع حتى اكتمال المجموعة، reviewed للمراجعة المستقلة، integrated بعد اعتماد وتكامل Claude.

**Blocked by:** dependencies (the pulse promotes this task to todo once they are done)

## الأدلة والتسليم
- الملفات: بقية المجموعة لم تنتج بعد.
- PR: none.
- التالي: بعد دمج TASK-0136 وتفرغ عمل Codex الجاري، احجز المهمة في worktree مستقل.
