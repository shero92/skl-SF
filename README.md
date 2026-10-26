# skl-SF — Seaside Fantasy RPG in Godot 4

A data-driven 2D Pixel Art RPG with a reusable map factory, movement, companion, NPC dialogue, animated lighting and ocean.

## Asset completion
- **218 / 218** registered assets have **separate PNG files** at their catalog paths.
- **0 files missing**, **218 files marked needs_cleanup**, **0 artist-approved final assets**.
- Files are organized by ID into floors, walls, architecture, stairs, environment, furniture, objects, vegetation, decor, shadows, characters and UI.
- Individual files and metadata: [parts](map_factory/parts/README.md) and [asset_index.json](map_factory/metadata/asset_index.json).
- Quality review: [asset gallery](docs/ASSET_GALLERY.md) and [audit](docs/ASSET_AUDIT.md).
- **Never call these all final high-quality assets merely because the files exist.** Some are procedural art or extracted concept-sheet sprites; validate alpha, anchor, seams, lighting, continuity and visual quality before approving.

## PC / QHD display
- Target output window: **2560x1440** (16:9, 1440p). Godot keeps a **1536x864 logical CanvasItem viewport** and scales its 2D rendering to the real window size, so the existing 64-pixel map grid, saved map coordinates and UI layout are not rewritten.
- The saved room/map canvas dimensions (e.g. 1536x1024) remain unchanged: they describe world content, **not** the PC output resolution. The gameplay camera may crop the top/bottom of that taller world; the separate map-only preview fits the complete room.
- Rendering at 1440p does **not** make low-detail PNG source art high-quality. New assets need individually approved native detail and correct Godot-scale review.
- Four-view Blender candidate exporter, art sizes and manual catalog acceptance: [art pipeline](docs/ART_PIPELINE.md).

## Run game
1. Open `project.godot` in Godot 4.4.1 or compatible 4.x.
2. Press **F5**.
3. Move with **WASD / arrows**; interact with **E** near NPCs, furniture and the room.
4. Continue dialogue with **E**, **Enter**, or **Space**.

The player, companion and two guardian NPCs use initial animated sprite sheets. The Hero Room combines reusable furniture, vegetation, stonework, sea and cloud assets. Four independent transparent ocean-wave frames animate on top of a repeated ocean base. Small lanterns and flames use separate PNGs.

## Map reuse
Every element is addressed by stable IDs and appears in `map_factory/rooms/hero_room.json`. Reuse the IDs in other room JSON layouts. Code lives in `map_factory/scripts/` and `scenes/`.

## Quality and replacement
**Before adding or replacing artwork, read [docs/ASSET_QUALITY_POLICY.md](docs/ASSET_QUALITY_POLICY.md) and [AGENTS.md](AGENTS.md).** Favor verified crisp, higher-fidelity, consistent images; preserve original IDs, update all metadata and do not replace an existing working image with an unverified worse one.
