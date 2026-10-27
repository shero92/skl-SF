---
id: ART-0016
status: blocked_reference
owner: graphics-specialist
task: TASK-0027
dedupe_key: hero_room_arch_ground_shadow
existing_asset_ids: S011,S012,S016,S017
output_paths: .agents/graphics/deliveries/ART-0016/hero_arch_column_shadow.png
issue: 20
---
# Large arch and column cast-shadow mask

**Goal / parent:** GOAL-0001 m8 / TASK-0011. **Coverage:** explicit m8 requirement; metadata match uncertain.
**Why existing parts are not yet a confirmed fit:** The m8 description asks for the large arch/column floor shadow; existing IDs describe column or generic diagonal/sun shadows without an explicit complete arch silhouette.

## Duplicate and reuse evidence
- Catalog: map_factory/metadata/asset_index.json; checked ID/name, native size, tags and orientation metadata only. No image was opened.
- Related entries: S011 Shadow Column Short [240, 128]; S012 Shadow Column Long [240, 128]; S016 Shadow Soft Diagonal [240, 128]; S017 Directional Sun Cast Shadow [320, 158]
- Existing request scan: ART-0001 covers the full bed views and remains the reused bed request. This record has independent deliverable paths and a unique dedupe_key.
- Registered needs_cleanup assets remain registered assets. Owner must cancel/narrow this request if an existing part or approved composition fits; do not overwrite or repaint a good registered sprite.

## Authentic reference / readiness
- Committed source path: .agents/planner/goals/GOAL-0001/references/hero_room_reference.png
- Git index blob identity (SHA-1 metadata, NOT an image SHA-256): 8d9a4c951b169458ceb85f9ad61107b99d59a909
- Source SHA-256: unrecorded for this committed file. Owner/reviewer must record and confirm it before changing blocked_reference to requested.
- Provenance mismatch to resolve: goal.md describes 1536x1024, while the legacy reference_gaps.json source describes 1448x1086 and an older hash. That legacy hash is not asserted to identify this file.
- No routine source-image inspection, production work, visual signoff or integration has occurred.

## Native specification / runtime contract
- Proposed native canvas: 320x158 pixels. This is a written-spec/metadata proposal, not an observed or artist-approved output size. Owner must confirm scale before production.
- Written-spec palette: warm sandstone/limestone and ivory, cobalt blue and restrained gold, warm wood/brass, deep green leaves and white/blue flowers. Owner confirms against the genuine reference; no sampled or invented pixel colors.
- Logical render layer: 4. Views / frames: single.
- Mount, anchor, collision and depth: owner-linked arch/column shadow, logical layer 4 rendered below its caster at z20. Actual per-file origins/footprints belong in the specialist manifest; no full-sprite box collider by default.
- Shadows/light: maintain the owner-confirmed daylight direction. Keep long cast shadows independent and owner-linked; no duplicate baked shadow on the color sprite. Non-casting sky/foam/rug/effect parts have no independent physical collider.
- Exact requirement: Owner-aligned transparent mask for the approved central arch and its two columns. Review S011/S012/S017 first; reuse any verified fit. Final extent and origin follow the delivered arch geometry and written daylight direction, not this provisional canvas alone. No scene painting baked into the mask.
- Four-facing upright outputs require independent correctly projected north/east/south/west art where listed. Animation frames and flat pieces are labeled separately and are not mislabeled as four views.

## Exact specialist outputs
- .agents/graphics/deliveries/ART-0016/hero_arch_column_shadow.png
- Manifest: .agents/graphics/deliveries/ART-0016/manifest.json with request_id, each actual path and measured SHA-256, pixel_size, origin, facing/frame order, collision footprint, shadow/mount metadata and owner_delivery provenance.
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

## Verified original reference
- Active source: map_factory/references/hero_room_01_original.png (1448x1086).
- SHA256: 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7.
- Identity/provenance: map_factory/references/hero_room_01_original.reference.json; prior 1536x1024 goal image is preserved historical material.
- Source identity gate is resolved by owner-provided bytes. Native output measurements, reuse review and artistic approval remain separate requirements; this amendment does not change production/review status.
