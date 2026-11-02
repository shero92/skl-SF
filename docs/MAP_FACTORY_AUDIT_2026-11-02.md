# Map Factory audit 2026-11-02 (main ec3fd1b)

Evidence for TASK-0090..0097. Scope: hero_room_01 v0012 vs the original reference.

## Works
- 128 v2 registry entries: all files exist and sha256 match; Godot loads them (game_factory_smoke passed).
- hero_room_01 v0012 renders deterministically (capture run 3 times locally, identical to the sha256 committed on main, febd9f23).
- Bed, tables, bookcases, rugs, rear arch, stairs, compass emblem render with correct anchors.

## Does not work / missing vs reference
- The room mixes two registries: 64 texture paths, 45 in v2, 19 legacy (E015-E017, E023/E024, F001/F002, S0xx) with status needs_cleanup and no qa_approval. 36 resolved ids are absent from v2 (v2 keys directional items `F05@north`, maps use `F05_north`).
- Floor uses legacy F001/F002; the 12 approved G01-G12 tiles are unused.
- Walls: only 4 W01 blocks on top and 9 W10 low segments at y=893, which E023/E024 foundations cover. No left or right wall, no caps, corners, ends or arch-adjacent blocks. This is a layout problem (build_hero_room_blueprint.py layout_entries), not missing art; side-facing wall art does not exist, so side runs use front-facing blocks.
- Lighting: 2 L01 lanterns and 3 glow effects; candles, table lantern and glow overlays unused. 83 of 128 v2 assets are not referenced by the room.
- Directional: 36 directional images (9 items x 4); only F01, F05, F09 declare direction ids; F06-F08 and crates carry none.
- Shadows/diagonal sunlight of the reference are baked into the reference image; no equivalent registered asset.
- `reference_room_layout.json` (132 objects, ModularRoomBuilder) is not what capture_map_previews.gd renders; the capture uses RoomFactory on versions/v0012.json.

## Screenshot SHA256 difference
Not reproducible: three consecutive local captures equal the main sha256. The single differing first capture ran right after a fresh `--import` of new .import files, so a stale import cache is the probable cause (unconfirmed).

## Root cause
Layout (blueprint script) and registry bridging, not the PNG assets and not the render layers.
