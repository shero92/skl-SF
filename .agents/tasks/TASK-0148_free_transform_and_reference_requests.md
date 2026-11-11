---
id: TASK-0148
status: review
owner: claude
agent: claude
priority: high
branch: claude/free-transform
depends_on: TASK-0146
issue: none
art_request: ART-0042
touches: tools/room_design.py,tools/art_reference_crop.py,tools/build_v0026_patch.py,tools/map_factory_cli.py,tools/map_factory_placement.py,map_factory/scripts/room_factory.gd,map_factory/LAYER_SCHEMA.md,.agents/workflows/GRAPHICS.md,tools/tests/test_room_design.py,tools/test_map.json,map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/blocks/latest.json,map_factory/maps/hero_room_01/layers/latest.json,map_factory/maps/index.json,docs/previews/map_factory_renders/t0148_v0026/hero_room_01_v0026.png
test: python tools/run_tests.py --changed
done_when: Any placed part can be turned, resized and drawn at any position with free_transform while grid cells still drive walking; rooms can be designed from code with tools/room_design.py; hero_room_01 v0026 proves it in a real Godot capture; the missing target pieces each have an art request with a reference crop, a target-vs-game comparison and an exact single-piece specification.
estimate_minutes: 120
---
# Free transform, code room design and reference-crop art requests

Owner request (2026-11-11): keep the Map Factory, but let parts be turned, resized and placed anywhere; plants and decoration are independent pieces; walking stays on squares; room design moves into code; every art request carries an exact description and a crop of the original picture.

- `free_transform: true` on a block: any angle for any piece; a grid-placed part may also be resized and drawn off its cell anchor while its cells keep reserving the walking grid.
- `tools/room_design.py`: `Design(map).place / transform / remove / write_patch`.
- `tools/art_reference_crop.py`: reference crop plus target-vs-game comparison for a request; rule recorded in `.agents/workflows/GRAPHICS.md`.
- hero_room_01 v0026 (`tools/build_v0026_patch.py`): bed rug enlarged under the bed, two off-grid turned flower pieces at the arch bases.
- ART-0042 to ART-0049: rear-left wall with window, rear-right wall with arched door niche, west and east curved side walls, front curved parapet pair, round cliff base, double bed, sea-stack islands.

## Evidence / handoff
- Real Godot capture: docs/previews/map_factory_renders/t0148_v0026/ (visual_approval stays false).
- The Godot builder applies the extra angle for grid-facing parts only through the flag; the v0026 capture exercises resize and free position of a grid part and rotation of off-grid parts, not rotation of a grid-facing part.
- Curved walls will need per-piece colliders or navigation cells reviewed when the art arrives.
