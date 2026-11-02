---
id: ART-0026
status: delivered
owner: codex
task: TASK-0069
dedupe_key: builtin_factory_g04_naturally_textured_sandstone_test
existing_asset_ids: none
output_paths: assets_generated/floor/G04__default/80377a4dfcbb44c293a01b006ff31822/G04__floor__naturally_textured_sandstone_floor_tile__default__1x1__64x64.png
---
# Built-in image_gen G04 standalone floor test

Owner explicitly requests imagegen skill + built-in tool only, one asset per call,
no characters and no external APIs. This supersedes the earlier provider request.
Duplicate scan: ART-0001..0025 describe bed, architecture, floor edges and compass;
none delivers this G04 production-plan variant. G01/G02/G03 already present under
references/approved are reused byte-for-byte, not regenerated. Published F-series
floor sprites remain unchanged; G04 stays in the separate candidate library.

Original room: map_factory/references/hero_room_01_original.png, SHA256
42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7.
Exact approved floor reference hashes and executed prompt are in request.json and
the asset's same-basename metadata JSON.

Output: 64x64 opaque PNG, 1x1 footprint, default facing, anchor (0,0), ground layer.
Built-in tool output ID: exec-d87d8b8a-ade8-4559-9324-e887ff416f71.
Native SHA256: a10ea4f41aa5e3dcb9263486ab9f6149bb3afd56a8ff7de92546b638da7abd02.
Source 1254x1254 preserved; NEAREST normalization recorded explicitly.

Actual Godot RoomFactory test replaced 147 floor cells and produced room.png and
source_vs_godot.png under the output attempt's godot_qa folder. Agent comparison
found and corrected inherited texture-scale gaps in the QA harness. Final floor is
continuous; it is more uniform than the room reference. Existing room composition
and historic catalog differences remain visible. This is not full-room fidelity
approval. Owner visual approval is still pending.

Canonical external copy: H:/shining force/pixel-art/TASK-0069/ART-0026/v002/.
Manifest records paths and hashes. No accepted HD sprites or published maps changed.
