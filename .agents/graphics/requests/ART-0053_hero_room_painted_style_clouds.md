---
id: ART-0053
status: requested
owner: graphics-specialist
task: TASK-0168
dedupe_key: hero_room_painted_style_clouds
existing_asset_ids: B12,B13,B14
output_paths: .agents/graphics/deliveries/ART-0053/cloud_large.png,.agents/graphics/deliveries/ART-0053/cloud_medium.png,.agents/graphics/deliveries/ART-0053/cloud_small.png
---
# Drifting clouds in the style of the painted hero room

**What is wrong today:** The owner (2026-11-13) rejected the drifting clouds: the game reused B12-B14, drawn for the tile room, and they do not match the painted sky. They were removed from the painted room.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; the painted sky and its clouds):** box left=0, top=0, right=1536, bottom=70: `.agents/graphics/requests/reference_crops/ART-0053_sky_target.png` (sha256 `7cc30254e80f2c755739b6fc170dcfd377ccb053dd0a08f7854f7953eb0e89b0`).

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down. Warm late-afternoon sun from the upper left. Pixel-art style, palette and outline weight of the painting.

**Exact specification:**
- Three separate cumulus clouds matching the painted ones: bright white tops lit from the upper left, soft warm-grey undersides, crisp pixel edges, no outline.
- `cloud_large.png` about 260x90 px, `cloud_medium.png` about 170x64 px, `cloud_small.png` about 100x40 px on canvas.
- Each cloud is complete on all sides (the game drifts it slowly left to right across the sky strip and behind the arch and sea stacks).
- Do NOT draw: sky colour, horizon, sea, birds, sun.

**Output format:** one RGBA PNG per output path, transparent background, the cloud only. Master at least 4x the on-canvas size; native sprite at the on-canvas size. Manifest records pixel size and SHA-256 per file.

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
