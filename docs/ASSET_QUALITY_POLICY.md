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
