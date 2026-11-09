---
id: TASK-0110
status: review
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: TASK-0109
issue: none
art_request: none
touches: map_factory/scripts/shadow_painter.gd,tools/verify_shadow_painter.gd,tools/tests/test_shadow_painter.py
test: python -m unittest discover -s tools/tests -p test_shadow_painter.py
done_when: Light pools (additive glow on the floor) are generated per lit prop in a separate Level5_Light node and can be toggled independently of shadows.
estimate_minutes: 60
---
# Map Factory: lantern and candle light pools tied to the light level

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_shadow_painter.py pass. Level5_Light is enabled by lighting.light_pools in the map.
Next step: review and merge the PR, then use the tools on a new room version (v0015).
