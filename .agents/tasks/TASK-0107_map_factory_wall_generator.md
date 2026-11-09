---
id: TASK-0107
status: review
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: none
issue: none
art_request: none
touches: tools/map_wall_generator.py,tools/tests/test_map_factory_tools.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_map_factory_tools.py
done_when: map_wall_generator.py turns a path with height and damage pattern into placements from registered wall pieces with a fixed seed, corners at turns, and no overlapping instances.
estimate_minutes: 60
---
# Map Factory: connected wall runs from a path blueprint

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_map_factory_tools.py pass. Generator only; no map version uses it yet (needs the wall art of ART-0032 to look right).
Next step: review and merge the PR, then use the tools on a new room version (v0015).
