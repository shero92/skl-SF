---
id: TASK-0046
status: review
owner: claude
branch: feat/blender-part-factory
agent: claude
touches: tools/blender_factory.py,tools/blender/,tools/art_qa.py,tools/tests/test_blender_factory.py,tools/test_map.json,tools/run_tests.py,.agents/planner/config.json,.agents/planner/requests/REQ-17ad643baa22.json,.agents/tasks/TASK-0046_blender_part_factory_foundation.md
test: py -3 tools/run_tests.py --only blender_factory
done_when: Blender toolkit renders calibrated RGBA pieces (64 px per tile, configurable 3/4 projection, upper-left light, separate shadow pass, four true facings) with manifest, SHA-256 and technical QA; first builders for ART-0004 wall run and ART-0014 broken floor edge; tests pass
started_at: 2026-10-26T21:18:34.946265+00:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Blender part factory foundation

**Source:** request:REQ-17ad643baa22
**Created:** 2026-10-26
**Goal:** GOAL-0001
**Type:** feature
**Priority:** critical
**Suggested agent:** claude (owner assignment: Claude builds the shared foundation)
**File:** tools/blender_factory.py
**Line:** unspecified
**Problem:** Owner decision 2026-10-26: build every environment piece in Blender, assemble the room in Godot, compare only the final Godot capture with the reference and improve the pieces instead of AI-generating graphics.

## Acceptance
- [ ] Blender toolkit renders calibrated RGBA pieces (64 px per tile, configurable 3/4 projection, upper-left light, separate shadow pass, four true facings) with manifest, SHA-256 and technical QA; first builders for ART-0004 wall run and ART-0014 broken floor edge; tests pass
- [x] Test: py -3 tools/run_tests.py --only blender_factory
- [ ] PR and observed test evidence.

## Owner decisions (2026-10-26)
- Final check is the Godot capture of the assembled room, not a Blender scene render.
- The nine accepted HD sprites (W021, W022, A017, A018, D019, P023-P026) stay as they are; Blender builds only missing pieces in a matching style.
- Claude builds the shared Blender toolkit; afterwards Claude and Codex split pieces in separate branches.

## Evidence / handoff
- Changed files: tools/blender/ (projection.json, lib.py, builders.py, render_part.py, specs/ART-0004.json, specs/ART-0014.json, README.md), tools/blender_factory.py, tools/art_qa.py, tools/tests/test_blender_factory.py, tools/test_map.json, .agents/planner/config.json (blender_executable).
- Calibration: a 1x1 floor tile renders exactly 64x64 (supersample 1) and 256x256 (supersample 4) with Blender 5.2.3 LTS.
- Trial renders (Cycles, RTX 3070): ART-0004 four wall facings in 31 s, ART-0014 four floor pieces in 21 s; all clean RGBA, 0.7-1.1% soft-alpha pixels, no backing or clipping.
- Finding for the owner: in the north-looking orthographic projection the inner faces of east/west side walls are edge-on, so north~south and east~west wall views look nearly identical (QA warning). Side-wall presentation needs a projection decision before ART-0004 is delivered.
- Tests: py -3 -m unittest discover -s tools/tests -p test_blender_factory.py 7/7 (incl. 2 real Blender renders); run_tests.py --changed 9/9; --all --kind python 24/24.
- No delivery, ART/TASK status change, map_factory/parts write or visual approval in this task.
- Next: owner decides the side-wall projection, then `deliver ART-0004` / `deliver ART-0014` PRs and Godot assembly + capture comparison.
