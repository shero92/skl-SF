---
id: ART-0055
status: requested
owner: graphics-specialist
task: TASK-0168
dedupe_key: hero_room_waves_breaking_on_rocks
existing_asset_ids: B15,B16,B17,B18
output_paths: .agents/graphics/deliveries/ART-0055/wave_break_sheet.png,.agents/graphics/deliveries/ART-0055/wave_wash_sheet.png
---
# Waves breaking on the rocks of the painted hero room

**What is wrong today:** The owner (2026-11-13): "it must be real waves smashing the rocks". The painted room only has a faint code shimmer on the water; a code-made wave streak was tried and rejected as bad. The existing foam frames B15-B18 were drawn for the tile room and do not match the painting.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crops (cut from the source image; the rocks and painted foam the waves must fit):**
- Left cliff base, box left=0, top=820, right=330, bottom=1024: `.agents/graphics/requests/reference_crops/ART-0055_cliff_base_left_target.png` (sha256 `d9f526bc433bcb4bb9e5e456fea97fdd16d0dedbca2acb9c1c099be037e4452e`)
- Right cliff base, box left=1180, top=820, right=1536, bottom=1024: `.agents/graphics/requests/reference_crops/ART-0055_cliff_base_right_target.png` (sha256 `2591a15005e0f87642382c3d86206eba5519c0c63c969556d2c887e104e672ec`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down. Warm late-afternoon sun from the upper left. Pixel-art style, palette and outline weight of the painting.

**Exact specification:**
- `wave_break_sheet.png`: one wave hitting a rock and bursting upward. 8 frames in one horizontal row, each frame 128x128 px, rock side at the bottom centre of the frame: swell arrives, crest curls, hits, white spray bursts up about 80 px, spray falls, foam spreads, foam thins, almost gone. White and pale-cyan foam with the painting's blue only in the shaded underside. Loops by fading out in frame 8.
- `wave_wash_sheet.png`: a low foam line washing along a rock base. 6 frames in one horizontal row, each frame 192x48 px: foam line advances about 16 px toward the top of the frame, pauses, then pulls back leaving thin white streaks. Loops cleanly.
- Both are overlays: the game places many copies along the cliff base at different times and flips them left-right.
- Do NOT draw: rocks, sea surface colour as an opaque block, sky, shadows on the cliff.

**Output format:** one RGBA PNG sheet per output path, transparent background, frames on an exact grid. Master at least 4x, native sheets at the sizes above. Manifest records frame size, frame count, suggested fps (break 10, wash 6) and SHA-256 per file.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached; reference crop attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review in Godot over the painted room; mark `reviewed`.

## Integration checklist
- [ ] Played over the painted room by `scenes/photo_room_life.gd`; PR merged; mark `integrated`.
