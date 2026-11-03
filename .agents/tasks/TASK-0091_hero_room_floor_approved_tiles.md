---
id: TASK-0091
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0090
issue: none
art_request: none
touches: tools/build_hero_room_blueprint.py,tools/tests/test_hero_room_floor.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_hero_room_floor.py
done_when: Floor cells use only approved G01-G12 tiles, deterministically varied, over the existing floor_footprint (17x10 cells, same row spans).
estimate_minutes: 90
---
# Hero Room floor from approved G01-G12 tiles

## Problem (evidence)
AUDIT: v0012 floor_ids use F001/F002 and floor_tile_style.tile_ids are F001/F002, legacy tiles with status needs_cleanup and no qa_approval. The 12 approved sandstone tiles G01-G12 in environment_assets_v2.json are not used by the room.

## Goal
Floor cells use only approved G01-G12 tiles, deterministically varied, over the existing floor_footprint (17x10 cells, same row spans).

## Implementation
In tools/build_hero_room_blueprint.py switch floor_ids and floor_tile_style.tile_ids to approved G01-G12 (clean G01/G02 majority, cracked or worn tiles sparsely, deterministic pattern, no random). Keep floor_footprint unchanged. Test imports the layout functions and asserts: only G ids, every id exists in v2, every footprint cell is covered, result is deterministic across two calls.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files. Never call the blueprint script main() from tests or code you add (it rewrites committed patch files); import and call only pure helper functions. Reply ONLY with edits to the files listed in touches; do not mention, request or ask to add any other file. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Use plain ASCII characters only in every reply, comment, string and file you write (no arrows, typographic quotes or dashes): the Windows console used by the worker crashes on other characters before your edits are applied.

Router registration: add ONE entry for test_hero_room_floor.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; leave every other entry untouched.

## Acceptance criteria
- [ ] Floor uses G01-G12 only, full footprint coverage, deterministic
- [ ] No PNG or generated asset changed
- [ ] The task test passes with at least one test collected

## Expected result in Godot
Floor looks like the reference sandstone with subtle tile variation and no legacy tiles. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_hero_room_floor.py` (the worker also runs the project router). The test file must define a unittest.TestCase subclass with test_* methods so at least one test is collected.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
