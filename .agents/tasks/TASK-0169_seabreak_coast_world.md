---
id: TASK-0169
status: review
owner: codex
agent: codex
priority: high
branch: codex/seabreak-coast
depends_on: TASK-0168
issue: none
art_request: none
touches: scenes/main.tscn,scenes/world,map_factory/maps/seabreak_coast_01,map_factory/maps/index.json,map_factory/worlds,tools/build_seabreak_coast.py,tools/polish_seabreak_coast.py,tools/refine_seabreak_coast.py,map_factory/metadata/asset_index.json,map_factory/parts/floors/G13_Coastal_Grass_A.png,map_factory/parts/floors/G14_Coastal_Grass_B.png,tools/verify_seabreak_coast.gd,tools/capture_seabreak_coast.gd,tools/tests/test_seabreak_coast.py,tools/test_map.json,docs/previews/seabreak_coast,docs/SEABREAK_COAST.md,.agents/tasks/TASK-0169_seabreak_coast_world.md,.agents/planner/requests/REQ-68f0779d6b24.json
test: python tools/run_tests.py --changed
done_when: Walking down the hero-room stairs enters a large connected coastal world with distinct landmarks, existing hero movement and a following camera; walking back to the sanctuary gate returns safely without a transition loop; traversal, blocked-water and round-trip tests and actual Godot captures are delivered.
---
# العالم الخارجي — ساحل Seabreak

طلب المالك2026-11-12 محفوظ حرفيًا في REQ-68f0779d6b24. منطقة واسعة قابلة للاستكشاف بعد الخروج من الغرفة، تعطي إحساس اكتشاف العالم.

التنفيذ داخل نسخة عمل مستقلة انطلاقًا من TASK-0168 (commit2c0b2ab6)، دون نسخ تعديلات المالك غير الملتزم بها. استعمال أصول البيئة الحالية فقط، ومصدر البطل وحركته الحاليين. لا تعديل لرسوم الشخصيات أو player.gd أو dialogue_ui.gd أو main.gd أو الخرائط التاريخية. لا صورة مسطحة بدل الأجزاء ولا رسوم إجرائية بديلة. الربط بعقدة مستقلة داخل main.tscn.

Agent: codex. Model/tokens/cost unknown. لا تفويض إلى عامل آخر.

## التسليم والتحقق الفعلي — 2026-11-12

- خريطة مستقلة `seabreak_coast_01` بحجم6144×4096؛ الإصداراتv0001..v0003 محفوظة، والأحدثv0003. 2161خانة أرض،2029خانة مشي، وست وجهات متصلة مع حلقة رئيسية ومطل جانبي.
- فرع ومجلد المهمة: `codex/seabreak-coast` / `.worktrees/seabreak-coast`. أساس الفرع هو غرفة TASK-0168 عند2c0b2ab6؛ PR يُبنى فوق `claude/photo-backdrop-test` كي لا يعيد تسليم تغييرات الغرفة. main.gd وplayer.gd وdialogue_ui.gd وتغييرات المالك المحلية لم تمس.
- عقدة `OutdoorExit` الجديدة في main.tscn تربط الدرج بالمشهد الخارجي؛ بوابة العالم تعيد البطل إلى موضع آمن مختلف بحسب عرض الصورة أو Map Factory. الحفظ الحالي للبطل لا يكتب بواسطة هذا الربط، وعلامة العودة مؤقتة تُستهلك مرة واحدة.
- world_travel.gd وroom_exit.gd وseabreak_coast.gd داخل scenes/world؛ حركة ورسوم البطل الحالية أعيد استعمالها. الكاميرا تتبع البطل بحدود الخريطة. الماء والعوائق مغلقة افتراضيًا، وقواعد المقاعد والأعمدة والنباتات وركيزتي القوس موثقة في map_factory/worlds/seabreak_coast_01.json. أزيلت7جدران تقطع المسارات فيv0003.
- تسجيل G13/G14 يعيد استعمال نسختي العشب64×64 من ART-0041/PR188 بايتًا ببايت؛ البصمات ومصدر master1254×1254 وفرعه في seabreak_source_reuse.json. لا استدعاءات توليد صور جديدة ولا تغيير لمصادر قديمة.
- اختبار Godot حرك HeroPlayer الحالي3451خطوة ووصل للوجهات الست، ثم نفذ انتقال الغرفة→العالم→الغرفة فعلًا وتحقق من موضع العودة وعدم التكرار. فُحص موضع العودة في وضعي الغرفة.
- `python -u tools/run_tests.py --changed --timeout 600`:91/91نجحت. إعادة فحوص الملاحة والخريطة والانتقال بعد التنقيح:4/4. `graphics_validation.py --changed`:705PNGدون أخطاء أو تحذيرات. مصدر فهرس الاختبارات صالح؛ تحديث INDEX.md الآلي متروك لـmain.
-8لقطات Godot فعلية وإيصال المحرك/بصمات الخريطة والربط في docs/previews/seabreak_coast. التفاصيل في docs/SEABREAK_COAST.md. cost/model/tokens unknown، والإيصال الآلي يرافق الالتزام.

الخطوة التالية: دمج هذا الفرع بعد دمج أساس غرفة TASK-0168، ثم تجربة المالك للتكوين الخارجي؛ visual_qa يبقى needs_review ولا ادعاء اعتماد بصري للخريطة.
