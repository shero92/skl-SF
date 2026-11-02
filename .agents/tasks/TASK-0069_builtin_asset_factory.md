---
id: TASK-0069
status: review
owner: codex
branch: codex/pixel-asset-factory
depends_on: none
issue: none
art_request: ART-0026
---
# Built-in image_gen environment asset factory

Goal: implement the owner's standalone environment asset plan with per-request image isolation, immutable attempts, tool-call reservations, review gates and Godot placement QA.

Touches: tools/pixel_asset_factory.py, tools/pixel_factory/**, tools/tests/test_pixel_asset_factory.py, tools/test_map.json, docs/PIXEL_ASSET_FACTORY.md, assets_generated/**, this record and the manual REQ record.

No characters, published catalog changes, historical maps or existing approved art changes. Owner superseded the initial provider request: use imagegen skill and built-in image_gen only; no API keys or external clients.

## Acceptance
- Plan compiles to unique prompts and explicit dimensions/footprints/facings.
- Test privacy, limits, retry accounting, review protection and native PNG QA.
- Real built-in single-asset + Godot QA receipt required before batch; missing prerequisites block it.
- Visual approval always requires an owner review; technical pass is not approval.

## Evidence / handoff
- Tests: 13/13 factory tests; 2/2 LF tests; required changed-path suite 10/10 groups passed before rebase and 9/9 groups passed on the final main-based diff. A first sandboxed all-tests attempt was interrupted after Git fixture permission failures; rerun with authorized test permissions passed.
- Original reference plus owner-designated G01/G02/G03 found in the active workspace and imported with exact hashes. No credentials required.
- Python launcher `py -3` unavailable; use installed `python` (3.13.15).
- Actual tool execution: exec-d87d8b8a-ade8-4559-9324-e887ff416f71. Native G04 SHA256: a10ea4f41aa5e3dcb9263486ab9f6149bb3afd56a8ff7de92546b638da7abd02. Source and NEAREST normalization retained.
- RoomFactory structural test and actual OpenGL room capture passed; 147 floor cells, source comparison retained. A detected QA scale issue was fixed and recaptured. Owner visual approval pending.
- 128 prompts compiled; G01/G02/G03 reused as approved; G04 generated pending review; 124 images remain ungenerated. Built-in production requires an active Codex session, not a Python daemon.
- External canonical assets: H:/shining force/pixel-art/TASK-0069/ART-0026/v002; hashes in assets_generated/external_manifest.json.
- PR: https://github.com/shero92/skl-SF/pull/65 (draft). Rebased task commit alone onto current main; unrelated prior agent-disable commit excluded. Final pushed SHA supplied in chat. No main merge or generated index/dashboard changes.
- Next: owner reviews G04 source-versus-Godot comparison, then Codex processes remaining queue with next/tool/ingest.
