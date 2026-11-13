---
id: ART-0054
status: requested
owner: graphics-specialist
task: TASK-0168
dedupe_key: hero_map_sprite_shining_force_style
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0054/hero_map_sf_down_idle_01.png
---
# Hero map sprite in classic Shining Force proportions (first frame only)

**What is wrong today:** The owner (2026-11-13, three times): "the hero must be more like Shining Force". The current map frames (`assets/characters/hero/map/*/sources/`, 1254 px) show a detailed figure about three heads tall with a long feather cloak. Shown in the painted room it reads as an illustration, not as a tactical-RPG map sprite. Reducing it to chunky pixels in code was tried and lost the face and the cloak detail.

**Source image and SHA-256 (the character design to keep):** `map_factory/references/characters/hero.png.png` (1122x1402), sha256 `80293cac049d7aed31bdb5cf638adee920e3e22e47771fbc7facba487013016f`. The "MAP SPRITES" block at the top right of that sheet shows the intended proportions.

**Room it stands in (style and scale):** `map_factory/references/hero_room_01_target_20261103.png`, sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`. One floor tile is about 64 px wide. The painting's own small hero (box left=700, top=440, right=760, bottom=540) is the look to match: `.agents/graphics/requests/reference_crops/ART-0050_painted_characters_target.png`.

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south looking north and about 50 degrees down. Warm late-afternoon sun from the upper left.

**Exact specification (ONE frame, one direction, so the style can be approved before the other 39 frames):**
- Facing down (toward the camera), standing idle, sword held low at the right hand side.
- Classic Shining Force / 16-bit tactical RPG map proportions: about 2 to 2.5 heads tall, large head, big readable eyes, short body, small hands and feet.
- Bold dark outline around the whole figure (1 px at native size), flat clear colour areas with two or three shades each, no fine feather texture: the cloak reads as a few large blue, white and orange feather shapes.
- Same design as the reference: spiky brown hair, blue eyes, teal scarf, feather cloak, rope belt, sandals.
- Native size: figure 80 px tall inside a 96x96 px frame, feet centred at x=48, y=90.
- Do NOT draw: floor, shadow, background, motion lines, text.

**Output format:** one RGBA PNG, transparent background, the figure only. Master at least 4x (384x384), native 96x96 as a clean reduction on the same pixel grid. Manifest records pixel size, anchor [48, 90] and SHA-256.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Reference paths and hashes attached; reference crop attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Owner looks at the frame inside the painted room and approves the style before more frames are requested; mark `reviewed`.

## Integration checklist
- [ ] Shown in the painted room; PR merged; mark `integrated`.
