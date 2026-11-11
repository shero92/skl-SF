---
id: TASK-0014
status: review
owner: codex
branch: codex/hero-room-cliff-foam
agent: codex
touches: .agents/graphics/deliveries/ART-0003/,assets_hd/background/cliff_foam_loop/v001,game_factory/environment/ART-0003/v001,docs/SOURCE_ART_CATALOG.md,map_factory/metadata/source_art_index.json,tools/source_art_catalog.py,tools/tests/test_source_art_catalog.py,.agents/graphics/requests/ART-0003_hero_room_cliff_foam_loop.md
test: python tools/run_tests.py --changed
done_when: Owner-approved specialist delivery for ART-0003 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0003
---
# Specialist delivery: Four-frame cliff-base foam loop

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0003

## Blocker / acceptance
- Request: ../graphics/requests/ART-0003_hero_room_cliff_foam_loop.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

## Codex production claim — 2026-11-11
Reference gate superseded by docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md and committed target SHA256 4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323. Four independently generated foam phases; native review 96x48 provisional, cadence 4 fps from current map ocean animation. No map integration or character/UI edits. Sources assets_hd/background/cliff_foam_loop/v001; metadata/captures game_factory/environment/ART-0003/v001; exact delivery .agents/graphics/deliveries/ART-0003. Owner automatic art approval applies. Each source, prompt, measured alpha/anchor and actual Godot playback evidence required. No claim of seamless animation until visual inspection.

## Delivery evidence
Four unique independently generated1774x887 RGBA source frames, no rejected attempts. Authoring and provenance in game_factory/environment/ART-0003/v001; masters assets_hd/background/cliff_foam_loop/v001; exact .agents/graphics/deliveries/ART-0003 paths populated. Genuine Godot playback4fps/12captures/3cycles; static1x/2x and animated6x inspection, GIF from viewport captures. Fixed whole-canvas normalization, no framewise crop/translation; measured white crest spread1sourcepx =0.054nativepx. All source/native/delivery and actual capture hashes verified. Owner visual approval automatic; room placement/terrain occlusion/map activation remain untested. Next: integrate at cliff base with calibrated fixed contact anchor and capture latest room as a new map revision.

Validation: python -u tools/run_tests.py --changed --timeout 120: 88/88 groups passed, exit0. Godot editor import and actual GL/ANGLE viewport capture exited0; sandbox user:// log/shader-cache warnings only. python tools/graphics_validation.py --changed: exit0, zero errors/warnings, 0 production PNGs covered because HD masters are outside that tool scope. Dedicated prepare/finish source audits verified4 unique1774x887RGBA frames, alpha0, safe bounds, fixed registration, >4x native density, matching source/native/delivery hashes; all12 Godot capture hashes verified. Source catalog check:126records,23HDgroups, zero unindexed PNGs, linked paths verified. Delivery receipt checked44files in both branch and owner root. tools/run_tests.py --check-index --sources-only and staged diff whitespace checks passed. Agent: codex; tool built-in image_gen; model/cost unknown. Branch evidence: https://github.com/shero92/skl-SF/tree/codex/hero-room-cliff-foam.
