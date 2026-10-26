---
id: ART-0001
status: blocked_reference
owner: graphics-specialist
task: TASK-0002
dedupe_key: hero_bed_four_perspective_views
existing_asset_ids: P001
output_paths: .agents/graphics/deliveries/ART-0001/hero_bed_north.png, .agents/graphics/deliveries/ART-0001/hero_bed_east.png, .agents/graphics/deliveries/ART-0001/hero_bed_south.png, .agents/graphics/deliveries/ART-0001/hero_bed_west.png
issue: 14
---
# Hero Bed: four real three-quarter perspective views

**Purpose:** produce four distinct upright environmental illustrations of existing `P001_Hero_Bed.png` in north/east/south/west orientations. Current Map Factory supports directional variants but the source art does not provide those different perspectives.

**Duplicate avoidance:** `P001` already exists under `map_factory/parts/furniture/` and MUST NOT be recreated or overwritten. Check current catalog for any newly committed variants and cancel/adjust this request if they already satisfy it. Do not use a flat rotated copy as a "new" view.

**Reference blocker:** the authentic original Hero Room reference from the user's conversation is not yet saved as a file in the repository. Do not invent matching details; wait until `TASK-0001` provides a committed image path and hash, then record them here. Consult `docs/REFERENCE_ART_DIRECTION.md`, existing P001 and its `pixel_size/origin` in `asset_index.json`.

**Exact requested outputs:** 4 separate transparent RGBA PNGs at the output_paths named above. Faces: north/east/south/west, all UPRIGHT and coherent in 3/4 top-down projection. Consistent silhouette, base/ground-contact pivot, original bed materials/colors, shading from upper left, clean alpha, no labels, neighboring objects or pre-baked long shadows. Determine the original native-size scale from the catalog before painting; do not upscale or silently change proportions. Supply a brief per-face dimension/origin suggestion and lighting/shadow note for map integration. New production catalog IDs must be allocated at integration time after checking the latest registry to avoid collision.

**Layer/mount:** furniture decoration over ground; contact shadow kept separate; collisions must represent the foot of the bed rather than the full illustration. No characters, dialogue or UI.

## Request checklist
- [x] Confirmed existing P001 ID and missing registered four-perspective art.
- [x] Defined exact four staging output paths and non-duplication condition.
- [ ] Genuine original image saved in repo; source hash recorded.
- [ ] Ready for graphics-specialist production.

## Graphics specialist checklist
- [ ] Four genuinely different views, independent PNGs with transparency.
- [ ] Match native scale, palette, anchors and separate shadow requirements.
- [ ] Export exactly four required paths and `deliveries/ART-0001/manifest.json` with SHA-256.
- [ ] Mark request `delivered` (not `reviewed`).

## Independent QA checklist
- [ ] Review all four at Godot game scale and against genuine source.
- [ ] Verify PNG alpha, halos, crop, pivot, visual perspective and hashes.
- [ ] Mark `reviewed` only with reviewer/evidence.

## Integration checklist
- [ ] Coding agent registers real art IDs and metadata; preserve P001.
- [ ] Godot four-direction tests and screenshot visual comparison pass.
- [ ] PR merged and update status `integrated`; never regenerate this request.

**Current status:** BLOCKED until authentic reference exists. No PNGs have been delivered.
