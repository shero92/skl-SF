---
id: TASK-0104
status: done
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: none
issue: none
art_request: none
touches: tools/hero_room_capture_evidence.py,tools/capture_map_previews.gd,tools/tests/test_hero_room_capture_evidence.py
test: python -m unittest discover -s tools/tests -p test_hero_room_capture_evidence.py
done_when: Evidence allowlist resolves assets_hd runtime textures through assets_hd/hd_map.json, accepts registered map_factory/parts sources and gives runtime-painted textures stable ids; a v0014 capture produces a resolved_assets manifest.
estimate_minutes: 60
---
# Map Factory: evidence gate accepts registered HD and part textures

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_hero_room_capture_evidence.py pass. Real v0014 capture passes the evidence gate: 84 distinct textures, 412 placements, 150 runtime-generated, no missing or unregistered paths (docs/previews/map_factory_renders/t0104_v0014/).
Next step: review and merge the PR, then use the tools on a new room version (v0015).

## Closure (Claude, 2026-11-09)
Merged in PR #111; real v0014 capture passed the evidence gate (84 textures, no missing or unregistered paths).
