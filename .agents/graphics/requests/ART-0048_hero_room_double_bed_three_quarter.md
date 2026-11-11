---
id: ART-0048
status: requested
owner: graphics-specialist
task: TASK-0148
dedupe_key: hero_room_double_bed_three_quarter
existing_asset_ids: F01
output_paths: .agents/graphics/deliveries/ART-0048/hero_double_bed_south.png
---
# Wide double bed in three-quarter view

**What is wrong today:** The game's bed is a narrow single bed seen almost from above; the target has a wide double bed seen from the front at three-quarter height.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_double_bed_south.png`: target box left=265, top=325, right=520, bottom=615 (255x290 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0048_target.png` (sha256 `7824995b0e8baa7a97e0655f5ac04a7f30b2fda65ff22dcca44214b3d005940d`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0048_compare.png` (sha256 `59a6ff53f0c2bc396c3981603ba6060b972c189f2289d83afb084be79b1718bc`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- One piece, about 255 px wide and 290 px tall on canvas.
- Facing: the foot of the bed points **south** toward the camera, the headboard is at the north end. The top of the mattress and the front of the foot board are both visible.
- Dark carved wood frame with four short posts; tall headboard partly hidden behind two white pillows and one small blue cushion with a gold compass.
- Blue quilt with a large gold compass in the middle and a gold border, white sheet folded over at the pillow end, white sheet edge visible at the foot.
- Do NOT draw: rug, bedside chests, shelf behind the bed, plants, shell, floor or cast shadow.

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
