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
touches: .agents/tasks/TASK-0102_owner_room_visual_review_and_release.md,docs/previews/map_factory_renders/task0102_v17_review,.agents/graphics/requests/ART-0033_hero_room_terrace_cliff_edge.md,.agents/graphics/deliveries/ART-0033,assets_hd/background/terrace_cliff/v001,game_factory/environment/ART-0033/v001,.agents/graphics/requests/ART-0032_hero_room_connected_ruin_walls.md,.agents/graphics/deliveries/ART-0032,assets_hd/architecture/connected_ruin_walls/v001,game_factory/environment/ART-0032/v001,.agents/graphics/requests/ART-0034_hero_room_sea_stacks_and_arches.md,.agents/graphics/requests/ART-0035_hero_room_planters_flowers_palms.md,.agents/graphics/deliveries/ART-0034,.agents/graphics/deliveries/ART-0035,assets_hd/background/sea_coast/v001,assets_hd/plants/coastal_garden/v001,game_factory/environment/ART-0034/v001,game_factory/environment/ART-0035/v001,.agents/graphics/requests/ART-0023_hero_room_side_wall_fixture_views.md,.agents/graphics/deliveries/ART-0023,assets_hd/decor/side_banners/v001,assets_hd/lighting/west_wall_lantern/v001,game_factory/environment/ART-0023/v001
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

## متابعة ART-0034 وART-0035

Agent: codex. Branch: codex/art-0034-0035-coast-plants. ثمانية عناصر بحرية وتسعة عناصر نباتية مستقلة لاستكمال الفجوات الموثقة. لا تعديل للخريطة أو المواد المعتمدة؛ الحفظ والطلبات والبصمات ونسخ المراجعة داخل المشروع.

تسليم ART-0034/0035: 17 مصدرًا مستقلًا و17 مشتق مراجعة، ولوحتا Godot فعليتان. الصخرة B الأولى محفوظة كمحاولة مرفوضة. لا تعديل للخريطة أو تفعيل تلقائي. التالي مراجعة الصور ثم معايرة الخلفية والنباتات داخل مشهد منفصل.

فحوص التسليم الجديد: 74/74 مجموعة مشروع نجحت؛ تحقق 17/17 مصدرًا فريدًا و17/17 مشتقًا ولقطتي Godot. نسخ المصدر والبيانات والطلبات محفوظة في جذر المشروع ببصمات مطابقة. موافقة المالك السابقة سُجلت ودمجت لـART-0032/0033؛ ART-0034/0035 الجديدة تبقى needs_review.

## ART-0023 بعد اعتماد ART-0034/0035

Agent: codex. Branch: codex/art-0023-side-fixtures. سُجل اعتماد العناصر البحرية والنباتات ودُمج #136. الطلب التالي أربعة اتجاهات مستقلة للرايات والفانوس؛ لا تكرار للبوصلة الموجودة ولا إعادة رسم لأصول معتمدة.

تسليم ART-0023: أربعة مصادر مستقلة ومشتقات مراجعة، مع قياسات نقاط التعليق ولقطة Godot 1x/2x. محاولتان مرفوضتان محفوظتان. بقيت معايرة المقاس والجدار واعتماد الصور الجديدة منفصلين؛ لا تغيير لخرائط الإصدارات الأحدث التي أضيفت أثناء توقف الجلسة.

- ART-0023 verification: `python -u tools/run_tests.py --changed --base origin/main --timeout 120`: **80/80 passed**, exit 0. Source and Godot receipt hashes verified; scene calibration remains pending.

## Owner automatic source-art approval — 2026-11-11
Owner grants automatic visual approval for all current/future generated images until individually rejected. Recorded in docs/OWNER_AUTOMATIC_ART_APPROVAL_20261111.md and linked from mandatory graphics policy. Existing capture manifests remain immutable; technical failure states remain honest. Source paths and agent handoff documented. This documentation-only follow-up uses branch codex/owner-automatic-art-approval.

Validation: python -u tools/run_tests.py --changed --timeout 120: 85/86 passed initially; golden_cyclone_assets timed out because the fresh worktree lacked the Godot class cache. After editor import, python -u tools/run_tests.py --only golden_cyclone_assets --timeout 120 passed 1/1. All 86 groups therefore passed across the run and targeted recovery. py -3 is unavailable; used python. No image bytes or historical manifests changed. Next step: apply this approval basis to subsequent art delivery/integration records.

## Source-art catalog follow-up — 2026-11-11
Owner requests per-piece metadata, discovery through image/map indexes and complete local copies under the main project folder. Same isolated branch codex/owner-automatic-art-approval, PR https://github.com/shero92/skl-SF/pull/172. Touches tools/source_art_catalog.py, tools/tests/test_source_art_catalog.py, tools/test_map.json, map_factory/metadata/source_art_index.json, map_factory/metadata/asset_index.json, map_factory/maps/index.json, docs/SOURCE_ART_CATALOG.md and mandatory graphics policy. No master, historical manifest, Golden Cyclone file or map revision is edited. Local missing files copied only after SHA checks; conflicting existing files are never overwritten. Next step: use the catalog for each subsequent delivery.

Catalog validation: 122 unique source records (96 selected, 26 rejected), 22 versioned HD groups with zero unindexed PNGs, all item-linked source/prompt/native/delivery files present and applicable SHA-256 values checked; two latest-map locators, 47 source records with exact path references. Three branch-only manifests retain PR/branch locators (#166/#168/#170). Missing local chest/rug masters and metadata plus nine delivery PNGs were copied into the owner project root from their original worktrees after SHA checks; no existing files replaced. python tools/source_art_catalog.py --root "H:/shining force/skl-SF" --check passed in the actual owner project folder. python tools/graphics_validation.py --changed: 689 PNGs, zero errors/warnings. python -u tools/run_tests.py --changed --timeout 120: 87/87 groups passed; final catalog refinements also passed all six dedicated unit tests. python tools/run_tests.py --check-index --sources-only and git diff --cached --check passed. Local owner-folder catalog/guide/tool/pointers match delivered records. Generated FILES/INDEX/task dashboards unchanged (main-only).

## ART-0040 provenance completion after Claude handoff — 2026-11-11
Agent: codex. Branch codex/art-0040-provenance-review. Claude packaged my byte-identical source during the user-authorized pause and merged PR178 / TASK-0163 / room v0028. Preserve that integration and canonical delivery manifest. Add complete source prompts, alpha diagnosis, manually measured wall origin, independent actual Godot1x/3x/8x QA, reference crop/comparison, source catalog entries and additive codex_source_manifest.json. No new art generation in this continuation, no master/runtime/map edits. The original east-lantern drafting worktree remains preserved. Runtime L07 uses trimmed29x47 BOX pixels and bottom-centre origin; source QA29x53 and source wall pivot require conversion when calibrating the wall mount. Next step: finish metadata delivery and tests; do not re-register L07.

ART-0040 supplement validation: python -u tools/run_tests.py --changed --timeout 120 passed89/89groups, exit0. Actual Godot4.7.2/ANGLE1x/3x/8x source review exited0; own source/native/delivery/earlier-attempt and viewport hashes passed verify_delivery.py. Source catalog check:128records /24HDgroups /zero unindexed PNGs /all linked item paths present. Supplemental receipt33files verified in branch and owner project root; canonical merged delivery manifest unchanged SHA2568cd82faa554d9498296422e058e00bc765ffb16818aa00580049460ab34bec40. Master retained byte-identical SHA2565607125059ca9c72d501f740bf28a87621305c4500a84cb703adab5102f7aef5. graphics_validation.py --changed exited0, zero errors/warnings,0production PNGs covered (masters outside tool scope); dedicated source audit covers this master. Test-index/whitespace checks passed. Godot user:// log/shader cache warnings did not prevent capture. No source/runtime/map/Golden Cyclone/UI files changed. Production usage L07/v0028 is existing PR178, not a new integration performed here. Earlier metadata snapshots preserved; hidden-RGB halo diagnosis corrected. Tool built-in image_gen, two generation calls before handoff; model/cost unknown. Next: use measured source pivot during explicit wall calibration and separately address open ART-0037; no re-generation/re-registration of this accepted lantern.
