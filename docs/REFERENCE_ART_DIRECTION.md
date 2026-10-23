# Hero Room — Visual Fidelity Standard

This is the reference art direction for the provided 1448×1086 Hero Room screenshot. It is the standard against which candidate replacement sprites should be reviewed, not an automatic approval checklist.

## Original reference appearance

- **Viewpoint:** three-quarter top-down fantasy JRPG, not strict isometric; room geometry follows a rectangular floor grid.
- **Stonework:** detailed sunlit amber/limestone sandstone, visible blocks and soft occlusion, crisp engraved cuts, weathered edges. Use warm highlights over a coherent mid-brown shadow value.
- **Sea and distance:** vivid high-saturation cobalt/cyan ocean with bright foam, receding rocky islands, deep blue distance and luminous sky clouds. Layer as separate moving water, static islands, and distant sky.
- **Greenery:** strongly saturated yet readable green ivy, small white/yellow flowers, orange accent blooms, layered vines attached to architecture. Never bake neighboring objects into vegetation sprite crops.
- **Wood/furniture:** textured brown/gold wood with tightly organized blue/gold cloth, small compass medallion details and readable silhouette in a tiny top-down game.
- **Hero/companions:** the reference hero is much more detailed than the current procedural 72×96-native prototypes: layered auburn hair, gold/cobalt outfit, soft shaded face, cape and sword; the companion has a detailed crystal ridge and expressive face.
- **UI:** nearly black navy with deep sapphire gradient, thin gold border and cutout gold corner ornament. Face portrait uses anime pixel-art with detailed hair/blue eyes.
- **Lighting:** strong warm sun arriving from the upper left, small amber lantern/candle pools, coherent shadows cast to the lower-right. Avoid multiplying baked shadows onto independent alpha shadows.
- **Atlas hygiene:** NO screenshot text, source-sheet captions, gold label bars, neighboring sprite slivers, cut-off outlines, solid box backgrounds behind object sprites, or alpha fringes.

## Approximate palette sampled from the provided screenshot

These are *guideline samples*, not rigid global quantization (which would destroy detail).

| Material | Highlights | Midtones | Shadows |
|---|---|---|---|
| Sunlit limestone | #FCE28E | #F1BA6E, #C8A279 | #89654C |
| Maritime textiles | #0960DF | #1248A5 | #031844 |
| Nautical golden trim | #F4E041 | #E6B11D | #B69C36 |
| Deep dialogue panel | #394668 | #031844 | #040A1D |
| Sky/sea | #90C3F9 | #3A9FFB, #0E6DD2 | #2F67AB |
| Ivy | #9FBA62 | #3C5C1D | #141D09 |

## QA acceptance test for every replacement

1. Compare the sprite at **native on-screen Godot scale**, not an enlarged editor preview.
2. Ensure a consistent overhead perspective, shape, proportions and contact point with the supplied screenshot.
3. Save a true **individual transparent PNG** except opaque full-screen environments.
4. Check no visible labels, neighbor fragments, alpha halos or clipping; verify animation frame alignment.
5. Fit position/anchor/collision/shadow metadata to actual sprite, preserve stable ID and room instances.
6. Keep a visible before/after comparison, and do not replace an image merely because its pixel dimensions are larger.
7. Run the Godot CI smoke test before approving. Only then may an artist or reviewer set status to ready.

## Current state

The automated cleanup pass removed unrelated cutout scraps from 23 PNGs, but **all 218 sprites still need artistic review**. The first-pass procedural hero, fairy and sea assets will require high-fidelity replacement artwork to fully match the reference.

Related: [art cleanup findings](ART_QUALITY_REVIEW.md), [visual preview gallery](ASSET_GALLERY.md) and [asset index](../map_factory/metadata/asset_index.json).
