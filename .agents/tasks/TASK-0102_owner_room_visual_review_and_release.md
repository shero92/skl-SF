---
id: TASK-0102
status: review
owner: codex
agent: codex
priority: high
branch: codex/task-0102-room-review
depends_on: TASK-0101
issue: none
art_request: none
touches: .agents/tasks/TASK-0102_owner_room_visual_review_and_release.md,docs/previews/map_factory_renders/task0102_v17_review,.agents/graphics/requests/ART-0033_hero_room_terrace_cliff_edge.md,.agents/graphics/deliveries/ART-0033,assets_hd/background/terrace_cliff/v001,game_factory/environment/ART-0033/v001,.agents/graphics/requests/ART-0032_hero_room_connected_ruin_walls.md,.agents/graphics/deliveries/ART-0032,assets_hd/architecture/connected_ruin_walls/v001,game_factory/environment/ART-0032/v001
test: python tools/run_tests.py --all
done_when: Claude merges tested Aider results, publishes a new immutable version after v0013, performs a real Godot capture and side-by-side reference review, reports exact remaining visual gaps, and only marks the room visually approved with explicit owner approval.
estimate_minutes: 120
---
# Integrate and review the Hero Room against the new owner's photo

Reference: `docs/HERO_ROOM_20261103_VISUAL_TARGET.md`. Do not overwrite existing v0012/v0013 or cached render paths. The listed v0014 destinations are **expected if v0013 is latest**; inspect current version at execution time, and use the next free version if newer work exists. Update this task's `touches` if paths change before execution.

## Work
1. Review and merge the output PRs from TASK-0090–0101, including runner-dependent tasks in order. Verify each reported `done` commit landed on main; local Aider done alone is insufficient.
2. From a clean `main` checkout, apply versioned map patch from the tested blueprint generator and verify no preexisting revisions were overwritten.
3. Run Godot import and `python tools/run_tests.py --all`. Capture a real 1536×1024 room screenshot using TASK-0101 path; do not generate an imagined scene.
4. Compare target image to rendered room, side by side: ocean, central arch, connected three-sided ruins, bed/rug, study table/rug, compass, walls, stair descent, flowers/vines, lantern light, sea/cliff edges and contact shadows. Record each zone as matched/partial/missing and give actionable next steps.
5. Do **not** insert characters in Map Factory. Optionally create a second gameplay-only screenshot using existing approved Hero/Neru assets and mark as separate composition; no generated characters.
6. If the approved assets cannot reproduce a target feature, create *specific* ART requests for Codex image_gen and mark the feature blocked; do not substitute unrelated sprites.
7. Keep `visual_approval: false` until explicit owner inspection. Final report includes screenshots, number of PNG paths used, placements, PR/commit links, missing art and test results.
8. Keep Aider Worker, worktrees and the $10 cap undisturbed. Do not automatically update its runner during a live task.

## Acceptance
- User can clone `main` and reproduce the room in Godot with all registered assets present.
- Target composition is reviewed visually; passing test hashes or automatic checks is not called visual approval.

## استئناف Codex 2026-11-10

المراجعة على v0017 الموجود؛ لا إعادة نشر v0014 أو تعديل التاريخ. التقاط Godot فعلي 1536×1024 عبر أدوات TASK-0101 نجح وتحقق evidence.json. visual_approval: false. عائق allowlist القديم المذكور في تقرير v0014 لم يتكرر.

التحقق: python -u tools/run_tests.py --all --timeout 120 نجح 66/66. لا تعديل للخرائط أو مصادر الصور. التسليم تقرير مراجعة v0017 والتقاطه وإثباته؛ اعتماد الغرفة ونشر إعادة تكوين جديدة ينتظران معالجة الفجوات والرسوم.

## اعتماد المالك 2026-11-10

وافق المالك صراحة على التسليم والدمج. مراجعة Claude السابقة محفوظة؛ مراجعة Codex لـv0017 في PR #128 تكملها. لا يعني قبول التقرير أن الفجوات المرئية اختفت.

## متابعة رسومية ART-0032 — 2026-11-10

Agent: codex. Branch: codex/art-0032-connected-walls. إنتاج تسع قطع جدران مستقلة لمعالجة فجوة المراجعة، مع حفظ المصادر والبيانات والطلبات داخل المشروع. لا تعديل للخريطة أو الأصول السابقة.

تسليم ART-0032: 9 masters و9 مشتقات مراجعة، و4 محاولات مرفوضة محفوظة. التوليد مستقل لكل صورة، لقطة Godot فعلية مع manifest SHA. معايرة footprint ونقاط الوصل داخل الغرفة واعتماد المالك للرسوم الجديدة لم ينفذا بعد.

فحوص ART-0032: 72/72 مجموعة مشروع نجحت؛ مصادر 9/9 ومشتقات 9/9 وبصمات الالتقاط تحققت. سجل QA: game_factory/environment/ART-0032/v001/qa/verification.json. التالي: مراجعة المالك للصور ثم معايرة نقاط الوصل والحجم بمشهد منفصل.

## متابعة رسومية ART-0033 — 2026-11-10

Agent: codex. Branch: codex/art-0033-terrace-cliff. معالجة فجوة الشرفة والجرف عبر ثمانية أصول مستقلة؛ صور المصدر والطلبات والبصمات ونسخ المراجعة تحفظ داخل المشروع. نطاق الملفات الإضافي: .agents/graphics/requests/ART-0033_hero_room_terrace_cliff_edge.md، .agents/graphics/deliveries/ART-0033، assets_hd/background/terrace_cliff/v001، game_factory/environment/ART-0033/v001. لا تفعيل تلقائي للرسوم الجديدة.

تسليم ART-0033: 8 مصادر مستقلة و8 مشتقات مراجعة، مع فحص PNG/RGBA والشفافية وعدم قص silhouette عند alpha128، ولقطة Godot فعلية موثقة. معايرة النهايات والارتكاز داخل الغرفة واعتماد المالك للصور الجديدة ما زالا معلقين.

فحوص ART-0033: 73/73 مجموعة مشروع نجحت؛ تحقق 8/8 مصادر و8/8 مشتقات وبصمات لقطة Godot. التفاصيل game_factory/environment/ART-0033/v001/qa/verification.json. التالي مراجعة الصور ثم معايرة نقاط الوصل داخل المشهد.

## اعتماد ART-0032 وART-0033 — 2026-11-10

وافق المالك صراحة على جميع المخرجات المسلمة وطلب دفعها ودمجها ثم متابعة الرسوم المطلوبة. الاعتماد يشمل 9 مصادر جدران و8 مصادر شرفة/جرف، ولا يشمل المحاولات المرفوضة أو صورًا مستقبلية لم تعرض بعد. معايرة الخريطة منفصلة.

فحص جمع التسليمات بعد اعتماد المالك: 74/74 مجموعة نجحت. أُعيد التقاط لوحتي Godot بحالة owner_approved=true، مع حفظ اللقطات وmanifest السابقة للموافقة. المصادر لم تتغير.
