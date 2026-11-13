---
id: ART-0051
status: requested
owner: graphics-specialist
task: TASK-0168
dedupe_key: hero_room_small_flying_creatures
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0051/seagull_fly_sheet.png,.agents/graphics/deliveries/ART-0051/butterfly_fly_sheet.png
---
# Small flying creatures for the painted hero room

**What is wrong today:** The owner wants small creatures flying around so the room feels alive. The game draws stand-ins by code: gulls are a white five-point line, butterflies are two flat triangles (`scenes/photo_room_life.gd`). They move correctly but are not art.

**Source image and SHA-256 (style reference only):** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`. Nothing in the painting shows these creatures; match its pixel-art style, palette and outline weight.

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down. Warm late-afternoon sun from the upper left.

**Exact specification:**
- `seagull_fly_sheet.png`: one seagull flying to the RIGHT, seen from the side and slightly above. 4 frames in one horizontal row, each frame 32x24 px: wings up, wings level, wings down, wings level. White body, light grey wing tops, dark wing tips, orange beak. The bird is about 26 px wide with wings level. The game flips it for flight to the left.
- `butterfly_fly_sheet.png`: one butterfly seen from above. 4 frames in one horizontal row, each frame 16x16 px: wings fully open, half closed, nearly closed, half closed. Wings pure white to light grey only (the game tints them yellow, blue or pink), thin dark body. About 12 px wide with wings open.
- Do NOT draw: shadows, background, motion trails, more than one creature per frame.

**Output format:** one RGBA PNG sheet per output path, transparent background, frames on an exact grid with the creature centred in each frame. Native size as given (no 4x master needed for sprites this small; if a master is made, the native sheet must be a clean reduction). Manifest records frame size, frame count, suggested fps (gull 8, butterfly 12) and SHA-256 per file.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries (the catalog has no bird, butterfly or other small flyer).
- [x] Style reference path and hash attached; no crop exists because the painting has no such creature.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review in Godot over the painted room; mark `reviewed`.

## Integration checklist
- [ ] `photo_room_life.gd` plays the sheets instead of the code shapes; PR merged; mark `integrated`.
