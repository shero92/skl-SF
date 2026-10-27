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

**Reference provenance blocker (TASK-0011 metadata update):** the genuine goal reference is now tracked at `.agents/planner/goals/GOAL-0001/references/hero_room_reference.png` (Git blob SHA-1 metadata `8d9a4c951b169458ceb85f9ad61107b99d59a909`). Its image SHA-256/native dimensions are not verified in the current request metadata, and legacy dimension/hash descriptions disagree. Do not invent matching details; owner/reviewer must confirm the source and record its SHA-256 before specialist production. Consult `docs/REFERENCE_ART_DIRECTION.md`, existing P001 and its `pixel_size/origin` in `asset_index.json`.

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

**Current status:** BLOCKED pending confirmed source provenance/SHA-256 and scale. A reference file is tracked; no PNG pixels were opened by this task and no delivered bed views are claimed.

## Owner-approved recovery amendment
- Composition reference: authentic original 1448x1086 scene; target factory canvas 1536x1024. Older contradictory dimension wording is superseded, but source identity/hash still requires owner confirmation.
- Deliver visible authored facings first; retain remaining named views as deferred, never claim incomplete sets support four-way reuse.
- All proposed native sizes remain provisional until specialist calibration; provide measured native display size, ground footprint, origin, seam/mount interfaces and separate collision/shadow metadata.
- Reuse existing approved-quality candidates first. Keep blocked_reference until authenticated reference and calibrated specifications are reviewed. No production art or readiness approval is created by this amendment.
- Newly registered HD candidates to review before any duplicate production: P024,P025. Style approval alone is not calibrated production approval.

## Verified original reference
- Active source: map_factory/references/hero_room_01_original.png (1448x1086).
- SHA256: 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7.
- Identity/provenance: map_factory/references/hero_room_01_original.reference.json; prior 1536x1024 goal image is preserved historical material.
- Source identity gate is resolved by owner-provided bytes. Native output measurements, reuse review and artistic approval remain separate requirements; this amendment does not change production/review status.
