---
id: TASK-0026
status: review
owner: codex
branch: codex/hero-room-b4-rugs
agent: codex
touches: .agents/tasks/TASK-0026_hero_room_study_blue_rug.md,.agents/graphics/requests/ART-0015_hero_room_study_blue_rug.md,.agents/graphics/deliveries/ART-0015,assets_hd/decor/hero_room_rugs/v001,game_factory/environment/ART-0015/v001
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: Owner-approved specialist delivery for ART-0015 is independently reviewed and safely integrated with provenance, tests and PR evidence.
started_at: unknown
cost_usd: unknown
depends_on: TASK-0011
issue: 20
art_request: ART-0015
---
# Specialist delivery: Second blue rug for the study zone

**Goal:** GOAL-0001. **Parent request-record task:** TASK-0011.
**Source:** art:ART-0015

## Blocker / acceptance
- Request: ../graphics/requests/ART-0015_hero_room_study_blue_rug.md
- Blocked on owner-confirmed source SHA-256 and native scale, then genuine specialist output. This is a specialist handoff, not an additional automatic coding-planner milestone.
- [ ] Exact independent PNGs and measured manifest delivered by a graphics specialist.
- [ ] Independent visual QA reviewer/evidence recorded; no automated approval.
- [ ] Reviewed files integrated and verified in Godot, owner approval and merge evidence recorded.

## Evidence / handoff
- Changed images: none.
- Delivery / visual QA / integration: not performed.
- Next: owner reviews the linked request, confirms reference provenance/scale and supplies specialist art.

## Owner next graphics assignment
Two independently generated oblique floor rug candidates, study and bedroom, per authenticated current target. Prior square/portrait HD rugs inspected and preserved; this request supplies authored foreshortened projections, never transformed source bitmaps. Proposed QA canvases311x160 and304x225 remain subject to scene calibration. Built-in image_gen only, no integration or visual approval.

## Actual delivery evidence
- Two independent oblique floor rug PNG sources and exact delivery copies, four prior attempts retained. Metadata, prompts, source/reference SHA and actual Godot1x/2x capture supplied.
- Native proposals311x160/304x225 and D1-a311x126/304x178 recorded; measured source aspect2.529/1.668 is closer to D1-a. No artificial stretching, map/camera change or visual approval.
- `python tools/graphics_validation.py --changed`: exit0, png_checked0 (candidate masters outside scope); independent technical QA2/2.
- `python tools/run_tests.py --changed --timeout120`: **85/85 passed**, exit0.
- Sources and metadata copied to project root with SHA receipt; generation cache not required.
- Next: owner reviews candidates; Claude resolves floor depth/projection, annotates logical footprint and places accepted assets.

- Review PR: https://github.com/shero92/skl-SF/pull/168 (draft; owner review and scene calibration pending).
