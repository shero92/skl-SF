---
id: TASK-0090
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: none
issue: none
art_request: none
touches: tools/audit_room_assets.py,map_factory/metadata/environment_assets_v2.json,tools/tests/test_registry_verification.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_registry_verification.py
done_when: Every id a map uses has a defined v2 target or an explicit documented legacy status, and tools/audit_room_assets.py reports them.
estimate_minutes: 90
---
# Registry bridge verification (v2 vs legacy ids)

## Problem (evidence)
AUDIT 2026-11-02: hero_room_01 v0012 resolved_assets has 66 ids, 36 of them absent from environment_assets_v2.json (E015-E017, E023-E024, F001, F002, S001..S016, legacy directional aliases such as F05_north and F09_east, and F01-F09 plain keys). The v2 registry keys directional items as F05@north while maps use F05_north. 19 of the 64 texture paths the room uses are outside the 128 approved v2 PNGs (E*, F00x, S0xx are status needs_cleanup without qa_approval in asset_index.json).

## Goal
Every id a map uses has a defined v2 target or an explicit documented legacy status, and tools/audit_room_assets.py reports them.

## Implementation
Extend tools/audit_room_assets.py with a function audit_map_ids(map_json, v2, legacy) returning: ids resolved by v2, ids resolved only by legacy (with legacy status and qa_approval flag), ids resolved by neither. Add a top-level `legacy_aliases` object to environment_assets_v2.json mapping each legacy directional alias (for example F05_north) to its v2 key (F05@north); do not change any existing asset entry, sha256 or path. Also verify all 128 v2 entries: file exists, sha256 matches, PNG size equals sprite_dimensions, directional groups have exactly north/east/south/west.

Scope: only the files in touches. Never create, edit, move or delete any PNG or anything under assets_generated/, assets/ or map_factory/parts/. Do not touch battle files. Never call the blueprint script main() from tests or code you add (it rewrites committed patch files); import and call only pure helper functions. Reply ONLY with edits to the files listed in touches; do not mention, request or ask to add any other file. Do not generate map versions; the operator applies the patch and captures the Godot screenshot after merge.

Router registration: add ONE entry for test_registry_verification.py to tools/test_map.json (id, kind python, covers, command, paths). Edit only that entry; leave every other entry untouched.

## Acceptance criteria
- [ ] For v0012 the report lists the exact legacy-only ids; all 128 v2 entries verify; every alias target exists
- [ ] No PNG or generated asset changed
- [ ] The task test passes with at least one test collected

## Expected result in Godot
Audit output is the reference list the later tasks use; no visual change in Godot. (verified by the operator with a real Godot capture, not by this task's tests).

## Test
`python -m unittest discover -s tools/tests -p test_registry_verification.py` (the worker also runs the project router). The test file must define a unittest.TestCase subclass with test_* methods so at least one test is collected.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 from a repository audit. Record the real execution tool and model when run.
