---
id: TASK-0095
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0094
issue: none
art_request: none
touches: tools/build_hero_room_blueprint.py,tools/map_factory_orientation.py,tools/tests/test_directional_furniture.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_directional_furniture.py
done_when: Every furniture object declares facing and direction_asset_ids for the four directions and the chosen image matches its facing; sprites are never rotated.
estimate_minutes: 90
---
# Directional furniture and block orientation

## Problem (evidence)
AUDIT: the registry has 36 directional furniture images (9 items x 4 directions) but v0012 declares direction_asset_ids only for F01, F05 and F09; F06, F07, F08 and the crates carry no facing data, and map ids use legacy aliases like F05_north.

## Goal
Every furniture object declares facing and direction_asset_ids for the four directions and the chosen image matches its facing; sprites are never rotated.

## Implementation
In tools/build_hero_room_blueprint.py and tools/map_factory_orientation.py make every furniture object (bed, bedside table, bookcases, dining table, benches, crates) carry facing and direction_asset_ids using v2 keys (X@dir) via legacy_aliases from TASK-0090; the resolver picks the facing image and rejects a facing with no image. Place the bench pair horizontal/vertical correctly and the right bookcase facing west. Test asserts each furniture object resolves to a distinct existing image per facing and footprints (3x4 vs 4x3) are consistent with facing.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files. Never call the blueprint script main() from tests or code you add (it rewrites committed patch files); import and call only pure helper functions. Reply ONLY with edits to the files listed in touches; do not mention, request or ask to add any other file. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Use plain ASCII characters only in every reply, comment, string and file you write (no arrows, typographic quotes or dashes): the Windows console used by the worker crashes on other characters before your edits are applied.

Do not write the path or file name of any file that is not in `touches` anywhere in your reply or in the files you edit (not in prose, not in the `paths` list of the tools/test_map.json entry, not in comments): Aider treats such a mention as a request to add the file, discards your edits and asks again. In the test_map.json entry list in `paths` only files from `touches`; read other data files at runtime inside the test by constructing the path from parts.

Router registration: add ONE entry for test_directional_furniture.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; leave every other entry untouched.

## Acceptance criteria
- [ ] All furniture resolves facing to the right image; four directions covered by test
- [ ] No PNG or generated asset changed
- [ ] The task test passes with at least one test collected

## Expected result in Godot
Furniture faces the room correctly; changing facing in a test shows the matching image. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_directional_furniture.py` (the worker also runs the project router). The test file must define a unittest.TestCase subclass with test_* methods so at least one test is collected.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
