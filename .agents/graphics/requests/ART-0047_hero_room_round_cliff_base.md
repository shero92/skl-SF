---
id: ART-0047
status: requested
owner: graphics-specialist
task: TASK-0148
dedupe_key: hero_room_round_cliff_base
existing_asset_ids: B03
output_paths: .agents/graphics/deliveries/ART-0047/hero_round_cliff_base.png
---
# Round cliff base under the terrace

**What is wrong today:** The game's base is separate straight cliff chunks with square corners; the target's terrace stands on one rounded rock mass.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_round_cliff_base.png`: target box left=20, top=770, right=1520, bottom=1024 (1500x254 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0047_target.png` (sha256 `ad8adf0df9b7176db07b0c30447c268cdbc0904d08485eab9e371c73da5c4626`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0047_compare.png` (sha256 `2c7ea2f0b16f0c1ef878b667865bf7e3063eb8f21f87f4171116c6b8c26d8ef5`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- One wide piece, about 1500 px wide and 254 px tall on canvas, with a transparent gap about 150 px wide in the middle for the stairs (x 690 to 840 of the source image).
- Plan shape: the front half of a circle; the rock face curves away to the left and right edges.
- Facing: vertical rock face looking south toward the camera; no top surface (the wall and floor sit on it).
- Blocky sandstone boulders in warm tan with darker cracks, larger blocks at the bottom; the bottom edge may be ragged where it meets the water.
- Do NOT draw: water, foam, plants, vines, walls, stairs or cast shadow.

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
