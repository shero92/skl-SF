# High-quality asset policy — SKL-SF

Read this file before creating, importing, replacing or approving any game texture.

1. Always prefer the best verified visual quality: clean pixel art, correct native resolution, accurate shapes, consistent palette, no visible crop artifacts or baked-in labels. A larger image alone is not necessarily better.
2. Store each part as an individual PNG at `map_factory/parts/<category>/<ID>_<Name>.png`. Reuse stable IDs in every map.
3. All objects need transparent RGBA backgrounds and clean edges; floor textures must tile seamlessly. Verify sprite anchors, collision footprints, shadows and pixel scale in Godot.
4. When a new texture is demonstrably superior, replace the old PNG at the same stable path, then update `map_factory/metadata/asset_index.json` and `production_queue.csv`. Git history preserves the old revision.
5. When unsure whether a replacement is better, stage it in `map_factory/candidates/` and review visually before overwriting. Never silently downgrade a production-ready file.
6. Metadata must honestly reflect `planned` (missing), `needs_cleanup` (draft/unreviewed) or `ready` (reviewed and usable). No empty placeholder records may count as completed art.
7. Keep shadows independently editable when appropriate, including light direction, opacity and offsets.
8. Inspect the current repository, this policy, the metadata catalog and source image on every future request involving assets; do not assume an old screenshot or chat describes the latest repo.
9. Report accurate counts and what was really uploaded. Clearly distinguish generated concept-sheet crops from finished game-ready sprites.
10. Use the ZIP-import process in `map_factory/incoming/` for larger packs, preserving file paths, IDs and unreviewed quality flags.

## Quality-check order
Artwork and native detail → transparency/cropping → consistency of art direction → tile seams → anchor and collision → shadows → usability in Godot → replace or stage candidate.

**Goal:** Reusable, high-detail 2D Pixel Art for Godot 4, not a collage disguised as ready-to-use sprites.

## Required high-fidelity graphics gate (owner direction, October 26 2026)

**Target quality reference:** `.agents/graphics/chatgpt_drafts/2026-10-26/source_reference_crops/` and the original owner-uploaded `061782c7-9e23-43a8-8c8a-fdd0a7c7ba6d.png`. These original detailed pieces show the intended densely painted golden limestone masonry, deeply shaded foliage with separate white flowers, sculpted blue-and-gold nautical symbols and consistent overhead-three-quarter perspective. Their reference-source provenance must remain distinct from art authored independently. They are **style references**, not automatically placeable sprites.

**Owner visual rejection:** all 22 sprites in `draft_specialist/` are visually rejected as low quality; filenames, correct alpha headers, pixel dimensions and SHA-256 are never artistic certification. Never place them into `map_factory/parts/`, mark them ready, use them in a level, or promote them with an automated script. Preserve them only for provenance/history. A new specialist must create genuinely better separate files from the real high-detail reference; do not upscale old low-detail sprites.

**Native art naming/identity:** preserve the catalog's actual production convention `res://map_factory/parts/<category>/<ID>_<Title_Case_Name>.png`. `ID` uniquely links `asset_index.json`, real file, dimensions, source hash and all maps. Never rename existing `P001` to a fictional `W` or `D` ID or infer an asset's collision/footprint from a filename. A four-facing upright object uses **four distinct catalog IDs** referenced via `direction_asset_ids: {north, east, south, west}`, not four aliases to a rotated or mirrored bitmap. Staging `ART-####/hero_*.png` names are request filenames, **not production catalog names**; review and allocate unique IDs before importing.

**Minimum independently reviewed quality evidence** for each sprite:
- True standalone uncut RGBA, no captions, borders, baked neighbor fragments, alpha halo, white/black backing, distorted silhouette or color fringe; no fake transparency by sampling out a dark contact sheet.
- Original hand-authored visual structure, high-frequency natural material detail and readable outlines at native Godot camera scale; no blur, upscale-only replacement, uniform procedural coloring or flat gradient standing in for painted stone/flowers/fabric.
- Exact 3/4 projection consistency, true facing-specific view geometry, calibrated native footprint and scene contact point; connected stone edges have compatible seams and thickness.
- Unified upper-left daylight and lower-right cast shadows, independent shadows when called for; cobalt blues, warm limestone/gold, bright white flowers and deep natural greens sampled against the verified real reference.
- Real asset pixel_size/origin and measured ground-cell footprint in `placement_contract`; permissible supporting floor tile IDs/tags, mounted hosts, collision footprint, lighting and visual sorting verified independently.
- A reviewer-signed before/after native-size Godot screenshot, measured PNG SHA-256, technical PNG QA and recorded reference provenance. A user approval is required before changing `status` to `ready`.

**Production agents:** only ChatGPT graphics chats or explicitly delegated specialist graphics models may create/repair/render art. Codex and Claude Code are coding/integration agents; no procedural sprites, image edits or art creation. They may verify metadata and insert **only independently reviewed** sprites without transforming their original pixels. Unreviewed artwork must stay in a staging folder.

**Fail-closed acceptance:** if the exact ref, original high-detail contact, four real views, tile occupancy, correct name/catalog metadata or a visual QA record is missing, the file stays `needs_cleanup`/staged; no automatic acceptance, global overwrite or claim that the library is regenerated. A catalog can contain 229 assets while zero have artistic final approval.
