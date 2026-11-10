---
id: TASK-0112
status: done
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: none
issue: none
art_request: none
touches: tools/map_audit.py,tools/map_data.py,tools/tests/test_map_factory_tools.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_map_factory_tools.py
done_when: map_audit.py reports unregistered or missing textures, unused registered assets, duplicate instance ids, objects without anchors, footprint overlaps and per-asset instance counts as JSON and text.
estimate_minutes: 60
---
# Map Factory: map audit report

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_map_factory_tools.py pass. Read only.
Next step: review and merge the PR, then use the tools on a new room version (v0015).

## Closure (Claude, 2026-11-09)
Merged in PR #111.
