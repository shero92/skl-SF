# Hero Room asset upgrade — verified status

Last reviewed: 2026-10-23

## Asset inventory
- 218 catalog records, 218 independently indexed PNG files, 0 missing.
- All 218 are still marked `needs_cleanup`; **0 artist-approved final textures**.
- No claim of 100% visual identity with the user-provided Hero Room reference is justified yet.

## Improvements committed during this pass
- **F003–F005, F007–F009, F011–F013**: warmer, shaded, stone-textured 64px starter tiles; still subject to visual review.
- **F014–F022**: coherent nine-tile gold-and-sapphire nautical compass inlay, now placed as a 3×3 floor mosaic in the room JSON.
- **F001 F002 F006 F010**: earlier high-detail source images intentionally preserved/restored because they were superior to a low-resolution procedural alternative.
- **UI001 UI004 UI005 UI011 UI012**: stronger navy-gold ornamental dialogue frame, portrait border, next arrow and top-left room title. Runtime UI uses nine-patch scaling to preserve corner details.
- **D008 D009**: high-detail wall lanterns cut apart from neighboring, unrelated atlas objects; metadata updated.
- **P011 P014 P015 O001 W001**: neighboring fragments and printed crop-bar remnants removed without repainting the surviving high-detail pixels.
- **E010–E014**: 512×512 cobalt/cyan sea material and four separately animated white-foam textures. Hero Room now displays native-size tiled waves.
- **Hero Room layout**: bed, bookshelves, writing desk, NPCs and player repositioned to better correspond to the reference composition.
- **Quality guard**: GitHub Actions detects missing images, metadata size mismatches, and unreviewed substantial loss of native source resolution.

## Remaining blockers to final-quality claims
The entire library still needs in-game artistic approval. Most important outstanding work:
1. Repaint 12 first-pass character sprite strips at a richer native detail level, preserving frame alignment and consistent facing.
2. Replace simplistic procedural UI portraits with artwork matching the reference's detailed anime pixel portrait.
3. Review every source atlas cutout for baked-in neighbor fragments, opacity halos, crop damage and correct lighting.
4. Compare furniture, architectural edges and plant motifs at actual Godot scene scale.
5. Check the tiled ocean for visible pattern repetition and smooth looping transitions.
6. Produce a visual Godot screenshot and compare composition, lighting, y-sorting, contact shadows and color against the supplied reference.

**Replacement principle:** only overwrite a previously good image with a demonstrably better reviewed image, not an upscaled lower-detail approximation. Preserve stable IDs, edit metadata when size/pivot changes and keep a Git history of replacements.

## Evidence and scripts
- Floor composite: `docs/previews/compass_mosaic_review.png`
- Ocean seam check: `docs/previews/ocean_seam_review.png`
- UI proof: `docs/previews/ornate_dialogue_ui_review.png`
- Cleanup comparisons: `docs/previews/verified_cutout_cleanup.png`
- Machine audit: `map_factory/metadata/asset_audit.json`
- Policy: `docs/ASSET_QUALITY_POLICY.md`

## Do not overwrite genuine high-detail art with flat procedural samples
The floor pass initially revealed such a potential regression and restored F001/F002/F006/F010 before concluding the art update. Any future agent must use the current repository sprites for comparison, not rely on dimensions alone.
