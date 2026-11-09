---
id: TASK-0106
status: review
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: none
issue: none
art_request: none
touches: tools/map_reference_compare.py,tools/tests/test_map_factory_tools.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_map_factory_tools.py
done_when: map_reference_compare.py splits render and target into the 11 review zones, reports colour and edge differences per zone and writes a side-by-side image plus JSON; it never sets visual_approval.
estimate_minutes: 60
---
# Map Factory: automatic region comparison against the target image

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_map_factory_tools.py pass. Zone hints are heuristic; visual_approval stays false.
Next step: review and merge the PR, then use the tools on a new room version (v0015).
