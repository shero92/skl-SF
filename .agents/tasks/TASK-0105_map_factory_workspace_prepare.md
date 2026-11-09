---
id: TASK-0105
status: review
owner: claude
agent: claude
priority: high
branch: claude/map-factory-upgrade
depends_on: TASK-0104
issue: none
art_request: none
touches: tools/prepare_map_workspace.py,tools/tests/test_prepare_map_workspace.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_prepare_map_workspace.py
done_when: prepare_map_workspace.py reports missing git-ignored PNG sources, optionally copies them from another checkout, and runs the Godot import so a fresh worktree captures without RoomFactory parse errors.
estimate_minutes: 60
---
# Map Factory: one command prepares a fresh workspace and captures reliably

Owner request (2026-11-09): improve Map Factory. Shadows must be a separate level that paints shadows for the objects, not only simple shadow lines.
No art is generated; existing registered PNGs and runtime-painted textures only.

## Result (Claude, 2026-11-09)
Implemented on branch claude/map-factory-upgrade; tests: test_prepare_map_workspace.py pass. Ran on this fresh worktree: copied 229 ignored PNGs, Godot import ok, capture then worked.
Next step: review and merge the PR, then use the tools on a new room version (v0015).
