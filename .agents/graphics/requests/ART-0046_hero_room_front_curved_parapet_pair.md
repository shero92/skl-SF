---
id: ART-0046
status: requested
owner: graphics-specialist
task: TASK-0148
dedupe_key: hero_room_front_curved_parapet_pair
existing_asset_ids: W10
output_paths: .agents/graphics/deliveries/ART-0046/hero_front_curved_parapet_left.png,.agents/graphics/deliveries/ART-0046/hero_front_curved_parapet_right.png
---
# Front curved low wall, left and right of the stairs

**What is wrong today:** The game has straight low wall blocks and planters in a line; the target's front edge is a low wall that curves from each side wall inward to the stair posts.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_front_curved_parapet_left.png`: target box left=130, top=690, right=700, bottom=900 (570x210 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0046_left_target.png` (sha256 `868212c86961c841d057054b4ed184b6b1b2476d2ef4f277c143b6985a654809`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0046_left_compare.png` (sha256 `f26c386c04d3c7974c914adbe094d50ea19985970a7b895ad6b65538bf00ef6e`)
- `hero_front_curved_parapet_right.png`: target box left=840, top=690, right=1420, bottom=900 (580x210 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0046_right_target.png` (sha256 `c1e21801b84f529b9a303983f85e06de79ceb6e8ed634109da685e8581ae2d92`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0046_right_compare.png` (sha256 `700e960cbe6c10672282ae5cfba1dd0a52608717c4967b1ef945d9246359a9dc`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- Two pieces, one per output file: the left half (about 570x210 px on canvas) and the right half (about 580x210 px). Each is ONE connected piece.
- Plan shape: each half is an arc, convex toward the camera, running from the side wall down and inward to the stair opening.
- Facing: the **outer** face looks south, toward the camera; the flat top course is visible from above. The room floor is behind (north of) the wall.
- Height about 3 block courses (roughly 70 px on canvas); crenellated top with gaps.
- Draw each half separately with the same upper-left sun; the right half is not a flipped left half.
- Do NOT draw: vines, ferns, flowers, the stair posts, the stairs, cliff rock, banners or cast shadow.

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
