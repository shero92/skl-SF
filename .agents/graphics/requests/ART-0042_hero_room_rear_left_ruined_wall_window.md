---
id: ART-0042
status: delivered
owner: codex
task: TASK-0148
dedupe_key: hero_room_rear_left_ruined_wall_window
existing_asset_ids: W09
output_paths: .agents/graphics/deliveries/ART-0042/hero_rear_left_ruined_wall_window.png
---
# Rear-left ruined wall with a window (behind the bed)

**What is wrong today:** The game has a straight low wall with a bookcase pushed against it; the target has a tall broken sandstone wall that steps up from the west corner to the arch column and has one square window opening.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_rear_left_ruined_wall_window.png`: target box left=150, top=130, right=620, bottom=330 (470x200 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0042_target.png` (sha256 `c8d7a4005736fa1748cc78d108cd00291f790059ae812229772353e2d448bdaa`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0042_compare.png` (sha256 `dcf2692382fc9ce2ae53b634138d809e15e760c1e2e8d3d63c50bc5217c50d56`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- One connected wall piece, running west to east, about 470 px wide and up to 200 px tall on the 1536x1024 canvas.
- Facing: the inner (room-side) face looks **south**, toward the camera. The top course of blocks is visible from above.
- Silhouette: lowest at the west end (about 3 block courses), rising in broken steps to about 6 courses at the east end where it meets the left arch column.
- One square window opening about 40x40 px in the western third, fully transparent so the sea shows through.
- Large rectangular sandstone blocks (about 32x24 px each on canvas), warm tan with darker mortar lines, a few chipped corners.
- Do NOT draw: lanterns, ivy, flowers, banners, shelf, bed, vases, floor, sea or cast shadow. Those are separate pieces.

**Output format:** one independent RGBA PNG per output path, transparent background, the piece only. Master at least 4x the on-canvas size; native sprite at the on-canvas size given above. Manifest records pixel size, bottom-centre origin and SHA-256 per file. The Map Factory places it at any position, angle and size (`free_transform`), so do not bake in neighbours, plants or decoration.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached; reference crop and target-vs-game comparison attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review in Godot against the reference crop; mark `reviewed`.

## Integration checklist
- [ ] Registered asset and map tested; PR merged; mark `integrated`.

## Active production — 2026-11-11
Agent: codex; TASK-0156; branch codex/art-0042-0043-rear-walls. Independent built-in image_gen source with full metadata and Godot native review. Automatic owner visual approval recorded per current policy. No existing art or map revision replaced.

## Delivered — TASK-0156 / 2026-11-11
Independent clean RGBA source [1921, 819], master assets_hd/architecture/rear_left_window_wall/v001/hero_rear_left_ruined_wall_window.png, SHA256 a43aa0bbad6d8246083b4e9424f25ad1b9aa3450926f107a8fe3ad3f8ac10667. Exact requested delivery PNG and files-list manifest populated. Native[470, 200] whole-canvas nearest review and real Godot1x/2x capture under game_factory/environment/ART-0042/v001. All source/native/delivery/reference/capture hashes verified. 1 earlier nonselected attempts preserved with reasons. Owner automatic visual approval recorded; request delivered only. Room placement, join sockets, collisions and occlusion remain uncalibrated. Produced in isolated branch codex/art-0042-0043-rear-walls; no writes to owner main checkout.
