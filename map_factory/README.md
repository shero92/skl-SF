# Map Factory — Godot 4

Data-driven room composer with stable IDs, shadows, colliders, multi-layer sprite rendering and interaction locations.

## Important folders
- `parts/<category>/`: individual PNG assets; 161 exist currently, 57 remain missing.
- `metadata/asset_index.json`: 218 entries, all re-usable; distinguishes missing, draft and reviewed.
- `metadata/asset_audit.json`: automatic PNG integrity and metadata report.
- `metadata/production_queue.csv`: production inventory by ID.
- `rooms/hero_room.json`: sample composition with bed, columns, arch, banners, desk, plants, cliff details, NPC interaction locations.
- `scripts/room_factory.gd`: loads layout and creates floor + objects.
- `scripts/asset_factory.gd`: creates texture, optional collision, shadow and visual prototype for missing image.
- `scripts/shadow_factory.gd`: uses separate alpha shadow PNGs.

## Layout conventions
All pixel coordinates are in the room's canvas coordinate system.

- `canvas_size`: overall design canvas.
- `tile_size`, `size`, `ground_offset`, `floor_ids`, `tile_overrides`: repeatable floor cells.
- `background_objects`: cliffs and other distant objects rendered before flooring.
- `ground_overlays`: rugs, compass mark, floor decals, before characters.
- `back_objects`: back wall, arch, distant banners.
- `objects`: Y-sorted furniture/columns/interactables.
- `front_objects`: foreground foliage or other occlusion.
- `player_spawn`, `npcs`, `interactions`: gameplay location and dialogue data.

Example object:
```json
{
  "id": "P001", "instance_id": "HeroBed",
  "x": 423, "y": 674, "scale": 0.87,
  "collision": {"enabled": true, "size": [184,58], "offset": [0,-31]},
  "shadow": {"type": "bed", "offset_x": 0, "offset_y": -5, "opacity": 0.5}
}
```

## Art QA
All 161 existing textures are first-pass drafts pending artistic approval; do not automatically promote them to `ready`. The 57 missing records must remain planned until independent PNGs exist. Read `docs/ASSET_QUALITY_POLICY.md`.

## Current game controls
WASD / arrows = movement. E near bed, desk, chest, arch, or temporary guardian actor = dialogue. E / Enter / Space = continue dialogue.

This setup is a starting point, not finished art or production-complete gameplay.
