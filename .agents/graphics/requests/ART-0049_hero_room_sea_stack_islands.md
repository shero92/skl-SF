---
id: ART-0049
status: requested
owner: graphics-specialist
task: TASK-0148
dedupe_key: hero_room_sea_stack_islands
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0049/hero_sea_stack_arch_island.png,.agents/graphics/deliveries/ART-0049/hero_sea_stack_cluster.png
---
# Sea-stack islands for the horizon

**What is wrong today:** The game's horizon has two small grey rocks; the target has tall green-topped sea stacks, one of them a natural rock arch.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the piece to draw):**
- `hero_sea_stack_arch_island.png`: target box left=0, top=20, right=300, bottom=180 (300x160 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0049_arch_target.png` (sha256 `2569c46c78e09bab960f261a73ebda092405b6f316adc13a439e660623cefd49`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0049_arch_compare.png` (sha256 `2e04a3341f0f17c1664c22fc0f5d967490a9ab6aa7a2a7bf82ffc3f589afc024`)
- `hero_sea_stack_cluster.png`: target box left=1010, top=20, right=1536, bottom=210 (526x190 px).
  - Draw exactly this: `.agents/graphics/requests/reference_crops/ART-0049_cluster_target.png` (sha256 `882b46533ea1bf760c4a0ccfd0d676cde977ef7551a7d54279811b406abb091b`)
  - Target (left) against the game today (right): `.agents/graphics/requests/reference_crops/ART-0049_cluster_compare.png` (sha256 `1cb56d3637f7fecd6e03f93a9caddc57c7cbaba1cbd819140cda58fac9aea1e5`)

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down, so horizontal tops and south-facing faces are both visible; no vanishing-point perspective. Warm late-afternoon sun from the upper left; shadows fall to the lower right. Pixel-art style, palette and outline weight of the target crop.

**Exact specification:**
- Two independent background pieces, one per output file.
- Arch island: about 300x160 px on canvas. A long rock ridge with a natural arch hole on its left third (transparent hole), green shrubs on top, vertical tan-grey cliff sides.
- Cluster: about 525x190 px on canvas. Five to seven tall narrow stacks of different heights, the tallest at the right, green shrubs on top.
- Facing: seen from far away, side-on from the south with a slight view of the green tops. Distant, so slightly lower contrast than the room walls.
- Do NOT draw: sea, foam, sky, clouds or reflection. Transparent background down to the waterline.

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
