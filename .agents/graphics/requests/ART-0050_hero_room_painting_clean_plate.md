---
id: ART-0050
status: requested
owner: graphics-specialist
task: TASK-0168
dedupe_key: hero_room_painting_clean_plate
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-0050/hero_room_01_painting_clean.png
---
# Hero room painting without the painted hero and companion

**What is wrong today:** The room is now shown as the target painting (photo room, TASK-0168). The painting has a hero and a blue-crested companion painted on the floor, so the game shows them twice: once painted and frozen, once as the real walking characters.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261103.png` (1536x1024), sha256 `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.

**Reference crop (cut from the source image; this is the area to repaint):**
- Target box left=660, top=410, right=860, bottom=570 (200x160 px): `.agents/graphics/requests/reference_crops/ART-0050_painted_characters_target.png` (sha256 `b58a29dcfb50f3eaa5f01e812d7601ea608a99413177cf98c7b76db98a93f1d8`). The two figures stand at about x 700-810, y 440-545 with small shadows under their feet.

**Camera and light (same for every hero-room piece):** three-quarter top-down view, camera south of the room looking north and about 50 degrees down. Warm late-afternoon sun from the upper left; the diagonal light bands on the floor run from upper right to lower left and must continue unbroken through the repainted area.

**Exact specification:**
- One file: the whole painting, 1536x1024, identical to the source everywhere except the box above.
- Inside the box remove both figures and their shadows and continue the stone floor: the same square paving joints (they line up with the joints left and right of the box), the same diagonal light and shade bands, the same pixel grain.
- The top corner of the blue compass inlay (just below the figures, from about y 545) stays exactly as it is.
- Do NOT change anything outside the box: no recolouring, no resizing, no sharpening, no cropping. A pixel difference outside the box is a rejection.
- Do NOT add any new object, character, rug or shadow.

**Output format:** one opaque PNG, exactly 1536x1024, same pixel grid as the source (no 4x master needed: it replaces the backdrop one to one). Manifest records pixel size, SHA-256, and the box that was repainted.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached; reference crop attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [ ] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review in Godot against the reference crop; mark `reviewed`.

## Integration checklist
- [ ] `image` in `map_factory/photo_rooms/hero_room_01.json` points to the clean painting; PR merged; mark `integrated`.
