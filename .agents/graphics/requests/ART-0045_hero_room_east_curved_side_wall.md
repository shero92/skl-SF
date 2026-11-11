---
id: ART-0045
status: requested
owner: codex
task: TASK-0148
dedupe_key: hero_room_east_curved_side_wall
existing_asset_ids: W09
output_paths: .agents/graphics/deliveries/ART-0045/hero_east_curved_side_wall.png
---
# East curved side wall

**What is wrong today:** Same problem as the west side, mirrored: the game has a straight edge-on wall, the target a wall that bends around the terrace.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_east_curved_side_wall.png`: target box left=1300, top=230, right=1536, bottom=770 (236x540 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0045_target.png` (sha256 `565468c5cafba3e7a95302d1fbc780243077bc7ef1b3db9a3ba4f732f89325b1`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0045_compare.png` (sha256 `6eb857d600d3f3bf7bde8fe8f07c93269d4e553d1542b0cdf31ff2e1a7851695`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- One connected wall piece, about 236 px wide and 540 px tall on canvas.
- Plan shape: an arc bulging out to the **east**: from the rear-right corner (top left of the crop) around to the front-right (bottom left of the crop).
- Facing: the visible face is the inner face, looking west and south-west into the room; top course visible from above.
- Draw it as its own view with the sun from the upper left (this inner face is the lit one). Never a mirrored copy of ART-0044.
- Height about 5 courses at the rear, stepping down to 3 at the front; crenellated top.
- Do NOT draw: banners, lanterns, ivy, flowers, planter, floor or cast shadow.

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

## Production claim — 2026-11-11
TASK-0157; agent codex; branch codex/art-0044-0045-side-walls. One independent built-in image_gen source at this facing, no bitmap mirror or rotation. Owner automatic visual approval applies, technical density/geometry checks remain separate.

## Candidate evidence — TASK-0157 / 2026-11-11
Independent built-in image_gen outputs preserved under assets_hd/architecture/curved_east_side_wall/v001/rejected. Actual sizes do not satisfy requested4x density. source_count0, items[], files[], production_active=false; no qualified requested PNG. Metadata and real Godot candidate capture: game_factory/environment/ART-0045/v001. Keep request requested / needs_regeneration, not delivered. Automatic visual approval does not waive this technical gate. No upscale/mirror/rotation or silent native-size reduction.
