---
id: TASK-0090
status: todo
owner: aider
agent: aider
priority: normal
branch: none
depends_on: TASK-0075
issue: none
art_request: none
touches: tools/audit_room_assets.py,tools/build_environment_registry_v2.py,map_factory/scripts/asset_catalog.gd,tools/tests/test_registry_verification.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_registry_verification.py
done_when: Every approved environment asset and block is registered in map_factory/metadata/environment_assets_v2.json with a resolvable texture path, size, anchor, kind (ground/wall/furniture/decoration/shadow), layer and direction data; a verifier reports any gap.
estimate_minutes: 90
---
# Asset Registry Verification

## Goal
Every approved environment asset and block is registered in map_factory/metadata/environment_assets_v2.json with a resolvable texture path, size, anchor, kind (ground/wall/furniture/decoration/shadow), layer and direction data; a verifier reports any gap.

## Implementation
Add a read-only verifier (tools/audit_room_assets.py extension) that loads the v2 registry and checks: texture file exists, size matches PNG, anchor present, layer valid, four-direction entries point to distinct existing files when directional. Report missing/duplicate ids. Fix registry metadata and path references only.

Scope: only the files listed in touches. Aider must not generate, edit, move or delete any image (PNG) and must not change assets_generated/ or assets/. Do not touch battle files (scenes/battle/, tools/verify_battle_*).

Router registration: add ONE entry for test_registry_verification.py to tools/test_map.json (id, kind python, covers, command, paths) so test_router passes. Edit only that entry; do not touch other entries or tools/tests/INDEX.md.

## Acceptance criteria
- [ ] Registry has no missing texture, bad layer, or incomplete direction set; verifier test passes
- [ ] No PNG changed
- [ ] python tools/run_tests.py --changed passes

## Test
`python -m unittest discover -s tools/tests -p test_registry_verification.py`, then `python tools/run_tests.py --changed`.

## Estimate
90 minutes.

## Provenance
Planned by Claude Code on 2026-11-02 for Map Factory automation. Record the real execution tool and model when run.
