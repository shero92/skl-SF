---
id: ART-0043
status: requested
owner: graphics-specialist
task: TASK-0148
dedupe_key: hero_room_rear_right_wall_arched_door_niche
existing_asset_ids: A23
output_paths: .agents/graphics/deliveries/ART-0043/hero_rear_right_wall_arched_door_niche.png
---
# Rear-right ruined wall with an arched door niche

**What is wrong today:** The game shows a large free-standing double wooden door on a low wall; the target has a tall ruined wall with a small arched stone niche and a wooden door set inside it.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_rear_right_wall_arched_door_niche.png`: target box left=1030, top=90, right=1340, bottom=340 (310x250 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0043_target.png` (sha256 `1117757e38d75899519e6e62600937c12761fa269543c93d92e69ee323f97d74`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0043_compare.png` (sha256 `4e72cf88b2d4fb8f34966b8b12011b59f92ad04765865196595c0d879a26cebd`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- One connected wall piece, about 310 px wide and 250 px tall on canvas.
- Facing: inner face looks **south**, toward the camera; top of the wall visible from above.
- Silhouette: tallest in the middle (about 7 block courses) with a broken stepped top, lower toward the east end.
- Centre: a round-arched stone door frame about 70 px wide and 110 px tall, recessed, with a plain dark-wood door carrying a small brass compass emblem. Door closed.
- Same sandstone blocks as ART-0042 so both rear walls match.
- Do NOT draw: lanterns, vines, flowers, bookshelf, vases, floor, sea or cast shadow.

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
