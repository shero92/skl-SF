---
id: ART-0044
status: requested
owner: codex
task: TASK-0148
dedupe_key: hero_room_west_curved_side_wall
existing_asset_ids: W09
output_paths: .agents/graphics/deliveries/ART-0044/hero_west_curved_side_wall.png
---
# West curved side wall

**What is wrong today:** The game's west side is a straight wall drawn edge-on with cliff rock sticking out; the target's west side is one wall that bends around the round terrace.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_west_curved_side_wall.png`: target box left=20, top=330, right=250, bottom=800 (230x470 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0044_target.png` (sha256 `d9935f2ec241d060f71f4fa3e5a3eafbcdd0e2d1c7482948cae9d9da4fd4eb4c`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0044_compare.png` (sha256 `9918516b1845aea4e471a5d727e6d991fcd79925f8825aea03fb75c26f357ba0`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- One connected wall piece, about 230 px wide and 470 px tall on canvas.
- Plan shape: an arc. It starts at the rear-left corner (top right of the crop), bulges out to the west, and comes back toward the front-left (bottom right of the crop): a quarter-circle seen from above.
- Facing: the visible face is the **inner** face, looking east and south-east into the room; the top course is visible from above along the whole arc.
- Height about 4 block courses at the rear end, stepping down to about 3 courses at the front end; crenellated top (alternating raised blocks).
- Do NOT draw: banners, lanterns, ivy, flowers, wooden posts, cliff rock, floor or cast shadow.

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
Independent built-in image_gen outputs preserved under assets_hd/architecture/curved_west_side_wall/v001/rejected. Actual sizes do not satisfy requested4x density. source_count0, items[], files[], production_active=false; no qualified requested PNG. Metadata and real Godot candidate capture: game_factory/environment/ART-0044/v001. Keep request requested / needs_regeneration, not delivered. Automatic visual approval does not waive this technical gate. No upscale/mirror/rotation or silent native-size reduction.
