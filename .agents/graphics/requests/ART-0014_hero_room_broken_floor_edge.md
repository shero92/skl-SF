---
id: ART-0014
status: delivered
owner: graphics-specialist
task: TASK-0025
dedupe_key: hero_room_broken_floor_edge
existing_asset_ids: F006,F007,F008,F009,F010,F011,F012,F013
output_paths: .agents/graphics/deliveries/ART-0014/hero_broken_floor_edge_01.png, .agents/graphics/deliveries/ART-0014/hero_broken_floor_edge_02.png, .agents/graphics/deliveries/ART-0014/hero_broken_floor_corner_left.png, .agents/graphics/deliveries/ART-0014/hero_broken_floor_corner_right.png
issue: 20
---
# Irregular broken front floor-edge pieces

**Goal / parent:** GOAL-0001 m8 / TASK-0011. **Coverage:** explicit m8 requirement; metadata match uncertain.
**Why existing parts are not yet a confirmed fit:** The m8 description specifically asks for irregular/broken front edges. The audit maps generic edge/corner IDs, whose names do not establish a broken silhouette.

## Duplicate and reuse evidence
- Catalog: map_factory/metadata/asset_index.json; checked ID/name, native size, tags and orientation metadata only. No image was opened.
- Related entries: F006 Stone Floor Edge N [151, 161]; F007 Stone Floor Edge S [64, 64]; F008 Stone Floor Edge E [64, 64]; F009 Stone Floor Edge W [64, 64]; F010 Stone Floor Corner NW [166, 161]; F011 Stone Floor Corner NE [64, 64]; F012 Stone Floor Corner SW [64, 64]; F013 Stone Floor Corner SE [64, 64]
- Existing request scan: ART-0001 covers the full bed views and remains the reused bed request. This record has independent deliverable paths and a unique dedupe_key.
- Registered needs_cleanup assets remain registered assets. Owner must cancel/narrow this request if an existing part or approved composition fits; do not overwrite or repaint a good registered sprite.

## Authentic reference / readiness
- Committed source path: .agents/planner/goals/GOAL-0001/references/hero_room_reference.png
- Git index blob identity (SHA-1 metadata, NOT an image SHA-256): 8d9a4c951b169458ceb85f9ad61107b99d59a909
- Source SHA-256: unrecorded for this committed file. Owner/reviewer must record and confirm it before changing blocked_reference to requested.
- Provenance mismatch to resolve: goal.md describes 1536x1024, while the legacy reference_gaps.json source describes 1448x1086 and an older hash. That legacy hash is not asserted to identify this file.
- No routine source-image inspection, production work, visual signoff or integration has occurred.

## Native specification / runtime contract
- Proposed native canvas: 64x64 pixels. This is a written-spec/metadata proposal, not an observed or artist-approved output size. Owner must confirm scale before production.
- Written-spec palette: warm sandstone/limestone and ivory, cobalt blue and restrained gold, warm wood/brass, deep green leaves and white/blue flowers. Owner confirms against the genuine reference; no sampled or invented pixel colors.
- Logical render layer: 1. Views / frames: four flat edge/corner pieces.
- Mount, anchor, collision and depth: ground grid, proposed origin (0,0); seam and footprint metadata needed. Actual per-file origins/footprints belong in the specialist manifest; no full-sprite box collider by default.
- Shadows/light: maintain the owner-confirmed daylight direction. Keep long cast shadows independent and owner-linked; no duplicate baked shadow on the color sprite. Non-casting sky/foam/rug/effect parts have no independent physical collider.
- Exact requirement: Two irregular front-edge variations and two joining corner pieces, aligned with the existing floor tile system. Flat pieces may use approved floor rotation; no false perspective transforms on wall art. Owner must first check F007/F012/F013 and cancel covered outputs. Do not replace approved edge tiles or infer walkability from alpha.
- Four-facing upright outputs require independent correctly projected north/east/south/west art where listed. Animation frames and flat pieces are labeled separately and are not mislabeled as four views.

## Exact specialist outputs
- .agents/graphics/deliveries/ART-0014/hero_broken_floor_edge_01.png
- .agents/graphics/deliveries/ART-0014/hero_broken_floor_edge_02.png
- .agents/graphics/deliveries/ART-0014/hero_broken_floor_corner_left.png
- .agents/graphics/deliveries/ART-0014/hero_broken_floor_corner_right.png
- Manifest: .agents/graphics/deliveries/ART-0014/manifest.json with request_id, each actual path and measured SHA-256, pixel_size, origin, facing/frame order, collision footprint, shadow/mount metadata and owner_delivery provenance.
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

## Delivery (Blender, 2026-10-26)
- Built and rendered by Claude Code with tools/blender_factory.py (spec tools/blender/specs/ART-0014.json, Blender 5.2.3 LTS, Cycles); no AI image generation.
- Files (native 64 px/tile top face plus visible slab thickness below; @4x masters and separate *_shadow.png): hero_broken_floor_edge_01.png 142x155 sha256 d5d5a5419667, hero_broken_floor_edge_02.png 142x155 sha256 9c4c58c29c19, hero_broken_floor_corner_left.png 147x160 sha256 49de69b8bb32, hero_broken_floor_corner_right.png 144x158 sha256 45042059ad98.
- tile_top_left anchor per file is in manifest.json (anchors_px), for alignment with the 64 px floor grid and F007/F012/F013.
- Technical QA: no problems; halo 0-0.7% of soft edge pixels. Open warning: edge_01 ~ edge_02 (two intended variants differ only along the broken edge).
- Reference SHA-256 01d91889...3119c (1536x1024), not owner-confirmed. Unapproved: the visual check happens on the final Godot capture.
