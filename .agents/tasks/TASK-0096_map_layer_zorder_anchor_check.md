---
id: TASK-0096
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0095
issue: none
art_request: none
touches: tools/map_factory_layers.py,tools/tests/test_layer_zorder_anchor.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_layer_zorder_anchor.py
done_when: A verifier fails a map whose layer order, y-sort, anchor or scale violates the five-level rule.
estimate_minutes: 90
---
# Layer, z-order, anchor and scale verifier

## Problem (evidence)
AUDIT: v0012 layer_stack has 12 entries and render order is decided in RoomFactory; there is no automated check that background < ground < walls < furniture/decor < shadows/overlays, that objects respect y-sort by base y, or that anchors and scale (all 1.0) match the registered render_pivot_px.

## Goal
A verifier fails a map whose layer order, y-sort, anchor or scale violates the five-level rule.

## Implementation
Extend tools/map_factory_layers.py with verify_layers(map_json, v2): checks each object's layer belongs to one of background, ground, walls, furniture_decor, shadows_overlays, that within a layer objects are ordered by base y, that anchor equals registry render_pivot_px mapping, that scale is 1.0 unless declared. Test builds a small synthetic map with valid and invalid cases, then runs the verifier over hero_room_01 latest and asserts it runs and reports counts (it must not require zero violations on latest).

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files (scenes/battle/, tools/verify_battle_*). Do NOT call main() of tools/build_hero_room_blueprint.py from tests or code you add: it rewrites committed v0012 patch files; import and call only layout_entries()/resolve_entries()/helper functions. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Router registration: add ONE entry for test_layer_zorder_anchor.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Verifier catches each synthetic violation type
- [ ] No PNG or generated asset changed
- [ ] `python tools/run_tests.py --changed` passes

## Expected result in Godot
Gives a measurable pass/fail for layers before the Godot visual check. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_layer_zorder_anchor.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
