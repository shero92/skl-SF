---
id: TASK-0111
status: review
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: TASK-0109
issue: none
art_request: none
touches: scenes/map_factory_viewer.gd,scenes/map_factory_viewer.tscn,tools/verify_map_factory_viewer.gd,tools/tests/test_map_factory_viewer.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_map_factory_viewer.py
done_when: The viewer scene loads a map version, reloads when the JSON file changes and toggles background, ground, walls, decor, shadows and light independently; verified headlessly.
estimate_minutes: 60
---
# Map Factory: live viewer with layer toggles

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_map_factory_viewer.py pass. Keys 1-6 toggle levels, R reloads, P switches shadow style.
Next step: review and merge the PR, then use the tools on a new room version (v0015).
