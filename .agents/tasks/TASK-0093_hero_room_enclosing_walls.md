---
id: TASK-0093
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0092
issue: none
art_request: none
touches: tools/build_hero_room_blueprint.py,tools/map_factory_placement.py,tools/tests/test_enclosing_walls.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_enclosing_walls.py
done_when: A wall run follows the floor_footprint perimeter on top, left, right and bottom, with a gap at the rear arch and at the front stairs, using corner, cap, end and arch-adjacent blocks.
estimate_minutes: 90
---
# Enclosing walls, corners, caps and arch-adjacent blocks

## Problem (evidence)
AUDIT: v0012 back_objects contain only 4 W01 blocks along the top (y=289) and 9 W10 low segments at the bottom; there are no wall blocks along the left (x about 226) or right (x about 1314) edges, no wall caps, no inner/outer corners, no wall ends and no arch-adjacent blocks beside the rear arch. The reference room is enclosed by ruined ivy walls on three sides.

## Goal
A wall run follows the floor_footprint perimeter on top, left, right and bottom, with a gap at the rear arch and at the front stairs, using corner, cap, end and arch-adjacent blocks.

## Implementation
In tools/build_hero_room_blueprint.py generate wall placements from floor_footprint perimeter cells: W01-W04 body variants (deterministic mix, weathered ones sparsely), W05/W06 ivy and flower variants occasionally, W07 caps on top edges, W08 inner and W09 outer corners, W11/W12 wall ends at gaps, W13/W14 beside the rear arch. Left and right runs use the existing front-facing wall blocks (no side-facing wall art exists; do not rotate sprites). Use tools/map_factory_placement.py only for anchor math if needed. Test asserts: every perimeter cell outside the two gaps has a wall block, gaps are exactly the arch and stair cells, no two wall blocks overlap beyond their registered footprint, all ids in v2.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files. Never call the blueprint script main() from tests or code you add (it rewrites committed patch files); import and call only pure helper functions. Reply ONLY with edits to the files listed in touches; do not mention, request or ask to add any other file. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Use plain ASCII characters only in every reply, comment, string and file you write (no arrows, typographic quotes or dashes): the Windows console used by the worker crashes on other characters before your edits are applied.

Do not write the path or file name of any file that is not in `touches` anywhere in your reply or in the files you edit (not in prose, not in the `paths` list of the tools/test_map.json entry, not in comments): Aider treats such a mention as a request to add the file, discards your edits and asks again. In the test_map.json entry list in `paths` only files from `touches`; read other data files at runtime inside the test by constructing the path from parts.

Router registration: add ONE entry for test_enclosing_walls.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; leave every other entry untouched.

## Acceptance criteria
- [ ] Perimeter fully walled except two gaps; corner and cap ids used; no illegal overlap
- [ ] No PNG or generated asset changed
- [ ] The task test passes with at least one test collected

## Expected result in Godot
Room is enclosed by walls on three sides with a rear arch and front stairs, like the reference. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_enclosing_walls.py` (the worker also runs the project router). The test file must define a unittest.TestCase subclass with test_* methods so at least one test is collected.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
