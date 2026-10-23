# Map Factory — all 218 image slots populated

**218 independent PNG assets** in `parts/` now map to **218 indexed stable IDs** in `metadata/asset_index.json`. All images currently require visual QA; 0 are approved finals.

## Runtime
- `rooms/hero_room.json`: canvas, ground grid, layers, custom lighting, water/sky configuration, NPC positions, dialogue and collision overrides.
- `scripts/asset_catalog.gd`: look up objects by ID and category.
- `scripts/asset_factory.gd`: create sprites with correct origin, optional footprint collider, and transparent shadow.
- `scripts/shadow_factory.gd`: reuse independent shadow textures.
- `scripts/room_factory.gd`: compose the room and produce separately sorted background, floor, overlays, architecture, entities and front foliage.
- `scenes/ocean_background.gd`: repeat E010 as water, animate E011–E014 and display E018 sky cloud backdrop.
- `scenes/room_light_fx.gd`: animate independent candle textures and amber glow.

## Metadata status
- `planned`: no PNG exists.
- `needs_cleanup`: a PNG exists but has not passed human visual QA.
- `ready`: visually reviewed for pixel scale, transparency, tileability where required, collision/origin, lighting and game usage.

All sprites currently have the `needs_cleanup` status (including previously imported concept sheet crops and recent synthesized additions); improve and replace only when evidence supports the upgrade.

See `docs/ASSET_QUALITY_POLICY.md`, `docs/ASSET_AUDIT.md` and `docs/ASSET_GALLERY.md` for review.
