---
id: TASK-0159
status: blocked
owner: codex
agent: codex
priority: medium
branch: codex/art-0048-0049-bed-stacks
depends_on: TASK-0148
issue: none
art_request: ART-0048
touches: .agents/tasks/TASK-0159_art_double_bed_sea_stacks.md,.agents/graphics/requests/ART-0048_hero_room_double_bed_three_quarter.md,.agents/graphics/requests/ART-0049_hero_room_sea_stack_islands.md,.agents/graphics/deliveries/ART-0048,.agents/graphics/deliveries/ART-0049,assets_hd/furniture/double_bed_south/v001,assets_hd/background/sea_stack_islands/v001,game_factory/environment/ART-0048/v001,game_factory/environment/ART-0049/v001,game_factory/environment/bed_stacks_20261111,map_factory/metadata/source_art_index.json,docs/SOURCE_ART_CATALOG.md
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0048 (double bed, foot to the south) and ART-0049 (arch island and stack cluster) are delivered as independent PNGs that match their reference crops, each with a valid delivery manifest, in a PR whose checks pass.
---
# Codex art: double bed and sea-stack islands

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0048_hero_room_double_bed_three_quarter.md and .agents/graphics/requests/ART-0049_hero_room_sea_stack_islands.md.

## Producer evidence — 2026-11-11

Agent: codex; tool: built-in image_gen; model/tokens/cost unknown. Isolated worktree `.worktrees/art-bed-sea-stacks`, branch `codex/art-0048-0049-bed-stacks`. No owner main files changed.

- ART-0048: independent south double-bed master1178x1335 (minimum1020x1160), exact delivery PNG, native255x290, metadata and real Godot capture. Request delivered, integration pending.
- ART-0049: arch source1717x916 passes1200x640, native300x160; first low-ridge attempt retained. Six-stack candidate2117x743 fails2104x760: missing17source pixels vertically. Candidate retained and indexed; exact cluster delivery absent. Request stays requested, TASK blocked, draft PR evidence only.
- Masters: `assets_hd/furniture/double_bed_south/v001/`, `assets_hd/background/sea_stack_islands/v001/`. Metadata and genuine Godot gallery captures: `game_factory/environment/ART-0048/v001/`, `game_factory/environment/ART-0049/v001/`; prompts/source records and QA scripts: `game_factory/environment/bed_stacks_20261111/`.
- Owner visual approval automatic per 20261111 policy; production_active=false. No scene placement, map/collision/socket editing, character or Golden Cyclone changes. Missing output is not waived, upscaled or replaced with a cropped sheet.
- Source-art index147 records after source audit (previous143 plus4); prior pending branch snapshots are read-only local audit context and excluded from this task commit.
- Actual QA/tests: see shared `test_results.json` and per-ART `verification.json`. `graphics_validation.py --changed` covers runtime production paths, not these HD masters; custom audit measures sources/deliveries/captures.

Next step: generate cluster at genuine source size>=2104x760 when built-in output can meet that contract, or receive an explicit owner specification change; do not relabel current failed candidate as ready. Existing accepted bed/arch can be consumed individually after integration calibration.

النتيجة الفعلية النهائية:89/90 مجموعة فحص نجحت في التشغيل المخول؛ blender_factory تجاوز120ثانية. أعطال الصلاحيات السابقة موثقة، واختبار المعدات نجح عند إعادته. المصادر ومعاينات Godot والبصمات اجتازت فحوصها الخاصة. تبقى المهمة blocked وPR تجريبي بسبب دقة المجموعة وفحص Blender غير المكتمل؛ لا ادعاء نجاح90/90.
