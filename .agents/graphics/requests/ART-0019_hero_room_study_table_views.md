---
id: ART-0019
status: blocked_reference
owner: graphics-specialist
task: TASK-0030
dedupe_key: hero_room_study_table_views
existing_asset_ids: P009
output_paths: .agents/graphics/deliveries/ART-0019/hero_study_table_north.png, .agents/graphics/deliveries/ART-0019/hero_study_table_east.png, .agents/graphics/deliveries/ART-0019/hero_study_table_south.png, .agents/graphics/deliveries/ART-0019/hero_study_table_west.png
issue: 20
---
# Four-perspective study table

**Goal / parent:** GOAL-0001 m8 / TASK-0011. **Coverage:** explicit m8 requirement; metadata match uncertain.
**Why existing parts are not yet a confirmed fit:** The m8 description requires west-facing right-wall furniture. P009 has no registered orientation/variant metadata, so a west-facing match cannot be confirmed from names.

## Duplicate and reuse evidence
- Catalog: map_factory/metadata/asset_index.json; checked ID/name, native size, tags and orientation metadata only. No image was opened.
- Related entries: P009 Wooden Table Large [393, 275]
- Existing request scan: ART-0001 covers the full bed views and remains the reused bed request. This record has independent deliverable paths and a unique dedupe_key.
- Registered needs_cleanup assets remain registered assets. Owner must cancel/narrow this request if an existing part or approved composition fits; do not overwrite or repaint a good registered sprite.

## Authentic reference / readiness
- Committed source path: .agents/planner/goals/GOAL-0001/references/hero_room_reference.png
- Git index blob identity (SHA-1 metadata, NOT an image SHA-256): 8d9a4c951b169458ceb85f9ad61107b99d59a909
- Source SHA-256: unrecorded for this committed file. Owner/reviewer must record and confirm it before changing blocked_reference to requested.
- Provenance mismatch to resolve: goal.md describes 1536x1024, while the legacy reference_gaps.json source describes 1448x1086 and an older hash. That legacy hash is not asserted to identify this file.
- No routine source-image inspection, production work, visual signoff or integration has occurred.

## Native specification / runtime contract
- Proposed native canvas: 393x275 pixels. This is a written-spec/metadata proposal, not an observed or artist-approved output size. Owner must confirm scale before production.
- Written-spec palette: warm sandstone/limestone and ivory, cobalt blue and restrained gold, warm wood/brass, deep green leaves and white/blue flowers. Owner confirms against the genuine reference; no sampled or invented pixel colors.
- Logical render layer: 3. Views / frames: north/east/south/west.
- Mount, anchor, collision and depth: ground contact base; record per-face footprint and item/mount anchors. Actual per-file origins/footprints belong in the specialist manifest; no full-sprite box collider by default.
- Shadows/light: maintain the owner-confirmed daylight direction. Keep long cast shadows independent and owner-linked; no duplicate baked shadow on the color sprite. Non-casting sky/foam/rug/effect parts have no independent physical collider.
- Exact requirement: Four distinct upright views of the registered study table family, with west-facing placement supported. Preserve the existing base asset and its proportions. Native size is the existing catalog canvas as an initial constraint; owner supplies measured per-face dimensions/origins. Check for registered/reviewed facings before painting and cancel covered outputs. No bitmap rotations or mirrored upright views.
- Four-facing upright outputs require independent correctly projected north/east/south/west art where listed. Animation frames and flat pieces are labeled separately and are not mislabeled as four views.

## Exact specialist outputs
- .agents/graphics/deliveries/ART-0019/hero_study_table_north.png
- .agents/graphics/deliveries/ART-0019/hero_study_table_east.png
- .agents/graphics/deliveries/ART-0019/hero_study_table_south.png
- .agents/graphics/deliveries/ART-0019/hero_study_table_west.png
- Manifest: .agents/graphics/deliveries/ART-0019/manifest.json with request_id, each actual path and measured SHA-256, pixel_size, origin, facing/frame order, collision footprint, shadow/mount metadata and owner_delivery provenance.
- Production catalog IDs are allocated only when reviewed delivered files are integrated; do not invent registered IDs in this request.

## Acceptance and state gates
- [x] Name/metadata catalog and active request duplicate scan completed; linked blocked_on_art task exists.
- [ ] Owner confirms source identity, records source SHA-256, resolves native scale and accepts/cancels covered outputs; then mark requested.
- [ ] Graphics specialist alone supplies independent clean RGBA PNGs, exact filenames and measured manifest; then mark delivered.
- [ ] Independent reviewer compares with the genuine source at native Godot scale; verifies projection, alpha/halos, seams/loop, anchors, palette, mounts, collision and shadows; record reviewer/evidence before reviewed.
- [ ] Coding agent integrates only reviewed deliveries with provenance, validates metadata and a new map revision/Godot preview, obtains owner approval and records the PR before integrated.

**Handoff:** blocked on verified reference provenance/native-scale review and specialist art. No production graphics have been created, replaced or approved.

## Owner-approved recovery amendment
- Composition reference: authentic original 1448x1086 scene; target factory canvas 1536x1024. Older contradictory dimension wording is superseded, but source identity/hash still requires owner confirmation.
- Deliver visible authored facings first; retain remaining named views as deferred, never claim incomplete sets support four-way reuse.
- All proposed native sizes remain provisional until specialist calibration; provide measured native display size, ground footprint, origin, seam/mount interfaces and separate collision/shadow metadata.
- Reuse existing approved-quality candidates first. Keep blocked_reference until authenticated reference and calibrated specifications are reviewed. No production art or readiness approval is created by this amendment.
- Newly registered HD candidates to review before any duplicate production: P026. Style approval alone is not calibrated production approval.

## Verified original reference
- Active source: map_factory/references/hero_room_01_original.png (1448x1086).
- SHA256: 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7.
- Identity/provenance: map_factory/references/hero_room_01_original.reference.json; prior 1536x1024 goal image is preserved historical material.
- Source identity gate is resolved by owner-provided bytes. Native output measurements, reuse review and artistic approval remain separate requirements; this amendment does not change production/review status.

## Calibrated measurements (TASK-0038, 2026-10-27)
- Source: docs/HERO_ROOM_CALIBRATION.md (reference SHA-256 verified; native = source px x 0.971; ground depth per D1).
- Defer candidate: accepted HD P026 (with stool) fits the south view at s0.35, contact (1155,588).
