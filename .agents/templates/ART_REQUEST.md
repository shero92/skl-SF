---
id: ART-XXXX
status: blocked_reference
owner: graphics-specialist
task: TASK-XXXX
dedupe_key: distinct_asset_need_unique_across_requests
existing_asset_ids: none
output_paths: .agents/graphics/deliveries/ART-XXXX/example.png
---
# Exact graphical requirement

**Why:** which in-game map part is missing/inadequate after checking asset registry and other ART requests?

**Source image and SHA-256:** must be a committed original, otherwise keep `blocked_reference`.

**Outputs:** one independent RGBA PNG per listed path; type, direction, desired on-screen/native size, pivot, tileability, palette, shadows, collisions, layer, art-quality rules; do not replace good existing assets.

## Request checklist
- [ ] Duplicate scan against asset IDs, active requests and previous deliveries.
- [ ] Original reference path and hash attached.
- [ ] Specifications reviewed; mark `requested`.

## Graphics specialist checklist
- [ ] All required clean PNGs produced (ONLY graphics specialist).
- [ ] SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale; mark `reviewed`.

## Integration checklist
- [ ] Registered assets and map tested; PR merged; mark `integrated`.
