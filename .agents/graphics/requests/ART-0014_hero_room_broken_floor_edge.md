---
id: ART-0014
status: blocked_reference
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
