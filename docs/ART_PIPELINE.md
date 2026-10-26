# Art pipeline

## PC / QHD production contract (2026-10-26)

- **Output window:** 2560x1440 (16:9, QHD / 1440p). Godot's *logical* 2D viewport is 1536x864 with `canvas_items` stretch to render at the actual window resolution. Resizable lower-resolution windows remain possible.
- **Map grid:** keep `tile_size: 64` (logical map units). Do not change committed `canvas_size`, world positions, immutable map revisions or the shared 64-unit navigation cell size just to target 1440p.
- **Artwork:** source PNG size is independent of the logical 64-unit tile. Budget candidates by on-screen footprint and zoom, e.g. ~256px floor textures, 256x512px wall sections, 512px furniture, up to 512x1024px tall plants where useful. These are **starting guidelines**, not enforced dimensions or proof of quality. Avoid oversized atlases without a measured need.
- **Art direction:** preserve `docs/REFERENCE_ART_DIRECTION.md` and the original detailed reference; consistent three-quarter overhead camera, colors, sharp material details, soft top-left light and lower-right shadows. Large blurry upscales are not improvements.
- **Blender:** author clean separate meshes and an orthographic camera; use the same fixed camera, lighting, framing and transparent RGBA render across all four turns. Flat floor tiles may rotate in Godot; upright furniture/walls require **four independently rendered perspective sprites** (north/east/south/west), not a rotated 2D PNG.
- **Runtime:** maintain the existing five Map Factory passes (background, ground, walls, decorations and independent shadows). Test layering, collision, pivots, occlusion and full scene quality in an actual Godot render, including at 2560x1440.

## Blender four-view candidate exporter

This script uses the scene's existing orthographic camera, lighting, engine and material setup. Put **one asset** into a dedicated Blender collection (including its mesh/empty parents, excluding camera and lights). Position the camera to accommodate the asset through all turns. The script rotates the 3D collection around its XY center on the world Z axis; the camera stays fixed:

```bash
blender --background path/to/asset.blend --python tools/blender_export_four_views.py -- \
  --collection GameAsset --prefix hero_bed \
  --output map_factory/candidates/blender_exports/hero_bed \
  --width 512 --height 512
```

The four candidate PNGs are `hero_bed_north.png`, `hero_bed_east.png`, `hero_bed_south.png`, `hero_bed_west.png`, plus `hero_bed_manifest.json`. The script stages files but **does not import them into the asset catalog** and does not claim that any render matches the reference.

Manual QA then checks framing, all four perspectives, alpha edges, Godot sprite scale, floor alignment, independent shadow suitability, pivot, collision and lighting. Allocate **four distinct catalog asset IDs in the same environmental category**, record their real `pixel_size`, `origin`, collision metadata and paths in `map_factory/metadata/asset_index.json`, and select them through `orientation_mode: variants` and `direction_asset_ids` described by `map_factory/FOUR_DIRECTION_BLOCKS.md`. Only promote to `map_factory/parts/` after successful visual and Godot preview review. Never mark automatically generated candidates `ready`.

## Existing asset policy

1. Generate one clean, uncropped asset PNG per catalog ID, using the reference for style only.
2. Remove backgrounds and embedded labels; verify true alpha transparency.
3. Inspect outline and pixel scale; repair seams for tileable floors.
4. Record true pixel_size, origin, collision footprint and shadow metadata.
5. Set status to `ready` only after import, visual approval and scene test in Godot.
6. Reuse IDs in room JSON layouts across maps.

Existing project art is **not** automatically approved by this display/export configuration.
