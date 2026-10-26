---
id: ART-0005
status: blocked_reference
owner: graphics-specialist
task: TASK-0016
dedupe_key: hero_room_compass_wood_door
existing_asset_ids: A015,A016,W016
output_paths: .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_north.png, .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_east.png, .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_south.png, .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_west.png
issue: 20
---
# Closed arched wooden compass-emblem door

**Goal / parent:** GOAL-0001 m8 / TASK-0011. **Coverage:** audited gap: closed arched wooden door with compass emblem.
**Why existing parts are not yet a confirmed fit:** A015/A016 are named Stone Door; no wooden door with compass emblem registered.

## Duplicate and reuse evidence
- Catalog: map_factory/metadata/asset_index.json; checked ID/name, native size, tags and orientation metadata only. No image was opened.
- Related entries: A015 Stone Door Arched [196, 233]; A016 Stone Door Decorated [117, 204]; W016 Stone Wall Doorway [201, 235]
- Existing request scan: ART-0001 covers the full bed views and remains the reused bed request. This record has independent deliverable paths and a unique dedupe_key.
- Registered needs_cleanup assets remain registered assets. Owner must cancel/narrow this request if an existing part or approved composition fits; do not overwrite or repaint a good registered sprite.

## Authentic reference / readiness
- Committed source path: .agents/planner/goals/GOAL-0001/references/hero_room_reference.png
- Git index blob identity (SHA-1 metadata, NOT an image SHA-256): 8d9a4c951b169458ceb85f9ad61107b99d59a909
- Source SHA-256: unrecorded for this committed file. Owner/reviewer must record and confirm it before changing blocked_reference to requested.
- Provenance mismatch to resolve: goal.md describes 1536x1024, while the legacy reference_gaps.json source describes 1448x1086 and an older hash. That legacy hash is not asserted to identify this file.
- No routine source-image inspection, production work, visual signoff or integration has occurred.

## Native specification / runtime contract
- Proposed native canvas: 96x144 pixels. This is a written-spec/metadata proposal, not an observed or artist-approved output size. Owner must confirm scale before production.
- Written-spec palette: warm sandstone/limestone and ivory, cobalt blue and restrained gold, warm wood/brass, deep green leaves and white/blue flowers. Owner confirms against the genuine reference; no sampled or invented pixel colors.
- Logical render layer: 2. Views / frames: north/east/south/west.
- Mount, anchor, collision and depth: doorway wall mount; threshold origin and wall opening/footprint recorded per face. Actual per-file origins/footprints belong in the specialist manifest; no full-sprite box collider by default.
- Shadows/light: maintain the owner-confirmed daylight direction. Keep long cast shadows independent and owner-linked; no duplicate baked shadow on the color sprite. Non-casting sky/foam/rug/effect parts have no independent physical collider.
- Exact requirement: Closed wooden leaves with arched top, readable compass emblem and restrained blue/gold detailing. Match the W016 doorway opening at approved map scale. Four upright wall-facing views must preserve frame thickness and hinge/threshold coherence. Stone-door assets are related references, not substitutes.
- Four-facing upright outputs require independent correctly projected north/east/south/west art where listed. Animation frames and flat pieces are labeled separately and are not mislabeled as four views.

## Exact specialist outputs
- .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_north.png
- .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_east.png
- .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_south.png
- .agents/graphics/deliveries/ART-0005/hero_compass_wood_door_west.png
- Manifest: .agents/graphics/deliveries/ART-0005/manifest.json with request_id, each actual path and measured SHA-256, pixel_size, origin, facing/frame order, collision footprint, shadow/mount metadata and owner_delivery provenance.
- Production catalog IDs are allocated only when reviewed delivered files are integrated; do not invent registered IDs in this request.

## Acceptance and state gates
- [x] Name/metadata catalog and active request duplicate scan completed; linked blocked_on_art task exists.
- [ ] Owner confirms source identity, records source SHA-256, resolves native scale and accepts/cancels covered outputs; then mark requested.
- [ ] Graphics specialist alone supplies independent clean RGBA PNGs, exact filenames and measured manifest; then mark delivered.
- [ ] Independent reviewer compares with the genuine source at native Godot scale; verifies projection, alpha/halos, seams/loop, anchors, palette, mounts, collision and shadows; record reviewer/evidence before reviewed.
- [ ] Coding agent integrates only reviewed deliveries with provenance, validates metadata and a new map revision/Godot preview, obtains owner approval and records the PR before integrated.

**Handoff:** blocked on verified reference provenance/native-scale review and specialist art. No production graphics have been created, replaced or approved.
