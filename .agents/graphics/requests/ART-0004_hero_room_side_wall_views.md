---
id: ART-0004
status: delivered
owner: graphics-specialist
task: TASK-0015
dedupe_key: hero_room_side_wall_views
existing_asset_ids: W001,W006,W007,W008,W009,W019,W020
output_paths: .agents/graphics/deliveries/ART-0004/hero_wall_run_north.png, .agents/graphics/deliveries/ART-0004/hero_wall_run_east.png, .agents/graphics/deliveries/ART-0004/hero_wall_run_south.png, .agents/graphics/deliveries/ART-0004/hero_wall_run_west.png
issue: 20
---
# Four-perspective side-wall run blocks

**Goal / parent:** GOAL-0001 m8 / TASK-0011. **Coverage:** audited gap: left/right side wall faces (3/4 view).
**Why existing parts are not yet a confirmed fit:** No assets named as east/west-facing side wall runs; W001 appears front-facing only.

## Duplicate and reuse evidence
- Catalog: map_factory/metadata/asset_index.json; checked ID/name, native size, tags and orientation metadata only. No image was opened.
- Related entries: W001 Stone Wall Straight [179, 239]; W006 Stone Wall Corner NW [180, 239]; W007 Stone Wall Corner NE [157, 250]; W008 Stone Wall Corner SW [180, 239]; W009 Stone Wall Corner SE [157, 250]; W019 Deep Limestone Parapet Corner [246, 238]; W020 Deep Limestone Corner Without Sea [246, 238]
- Existing request scan: ART-0001 covers the full bed views and remains the reused bed request. This record has independent deliverable paths and a unique dedupe_key.
- Registered needs_cleanup assets remain registered assets. Owner must cancel/narrow this request if an existing part or approved composition fits; do not overwrite or repaint a good registered sprite.

## Authentic reference / readiness
- Committed source path: .agents/planner/goals/GOAL-0001/references/hero_room_reference.png
- Git index blob identity (SHA-1 metadata, NOT an image SHA-256): 8d9a4c951b169458ceb85f9ad61107b99d59a909
- Source SHA-256: unrecorded for this committed file. Owner/reviewer must record and confirm it before changing blocked_reference to requested.
- Provenance mismatch to resolve: goal.md describes 1536x1024, while the legacy reference_gaps.json source describes 1448x1086 and an older hash. That legacy hash is not asserted to identify this file.
- No routine source-image inspection, production work, visual signoff or integration has occurred.

## Native specification / runtime contract
- Proposed native canvas: 48x144 pixels. This is a written-spec/metadata proposal, not an observed or artist-approved output size. Owner must confirm scale before production.
- Written-spec palette: warm sandstone/limestone and ivory, cobalt blue and restrained gold, warm wood/brass, deep green leaves and white/blue flowers. Owner confirms against the genuine reference; no sampled or invented pixel colors.
- Logical render layer: 2. Views / frames: north/east/south/west.
- Mount, anchor, collision and depth: ground foot of wall; supply per-view base footprint and wall-local attachment anchors. Actual per-file origins/footprints belong in the specialist manifest; no full-sprite box collider by default.
- Shadows/light: maintain the owner-confirmed daylight direction. Keep long cast shadows independent and owner-linked; no duplicate baked shadow on the color sprite. Non-casting sky/foam/rug/effect parts have no independent physical collider.
- Exact requirement: Four upright three-quarter views of the same sandstone wall run. East and west must expose the correct side masonry, wall thickness and top surface; north joins the back wall and south supports reuse. Seam interfaces must align with W006-W009 corner metadata. Do not rotate or mirror an upright PNG to invent a facing.
- Four-facing upright outputs require independent correctly projected north/east/south/west art where listed. Animation frames and flat pieces are labeled separately and are not mislabeled as four views.

## Exact specialist outputs
- .agents/graphics/deliveries/ART-0004/hero_wall_run_north.png
- .agents/graphics/deliveries/ART-0004/hero_wall_run_east.png
- .agents/graphics/deliveries/ART-0004/hero_wall_run_south.png
- .agents/graphics/deliveries/ART-0004/hero_wall_run_west.png
- Manifest: .agents/graphics/deliveries/ART-0004/manifest.json with request_id, each actual path and measured SHA-256, pixel_size, origin, facing/frame order, collision footprint, shadow/mount metadata and owner_delivery provenance.
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
- Newly registered HD candidates to review before any duplicate production: W021,W022. Style approval alone is not calibrated production approval.

## Delivery (Blender, 2026-10-26)
- Built and rendered by Claude Code with tools/blender_factory.py (spec tools/blender/specs/ART-0004.json, Blender 5.2.3 LTS, Cycles); no AI image generation.
- Owner decision 2026-10-26: orthographic projection; east/west side walls show only top and end, so their near-identical look is expected.
- Files (native 64 px/tile, plus @4x masters and separate *_shadow.png): hero_wall_run_north.png 142x256 sha256 c45ea1a67d23, hero_wall_run_east.png 115x286 sha256 f068f8073d1c, hero_wall_run_south.png 142x257 sha256 524d96c4cfcf, hero_wall_run_west.png 115x286 sha256 08891dc8ce26.
- Technical QA: no problems; expected: east~west; open warning: north~south look nearly identical (symmetric wall seen from the back).
- Reference SHA-256 01d91889...3119c (1536x1024), not owner-confirmed. Status stays unapproved: visual check happens on the final Godot capture.

## Delivery v2 (Blender, 2026-10-26, TASK-0048)
- Re-rendered with warmer, darker limestone and a lower sun; ivy and white flowers on the inner face; east/west side walls lean outward (lean +/-0.45) so their inner face shows (owner request, replacing the top-only decision); still status delivered and unapproved.
- Files: hero_wall_run_north.png 142x256 sha256 02efdffd65e3, hero_wall_run_east.png 175x334 sha256 b3eee5198846, hero_wall_run_south.png 142x262 sha256 ff12ba453924, hero_wall_run_west.png 175x294 sha256 d82b080605ed.
- QA: problems none; warnings: hero_wall_run_north.png vs hero_wall_run_south.png.

## Verified original reference
- Active source: map_factory/references/hero_room_01_original.png (1448x1086).
- SHA256: 42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7.
- Identity/provenance: map_factory/references/hero_room_01_original.reference.json; prior 1536x1024 goal image is preserved historical material.
- Source identity gate is resolved by owner-provided bytes. Native output measurements, reuse review and artistic approval remain separate requirements; this amendment does not change production/review status.
