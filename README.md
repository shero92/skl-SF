# skl-SF — Godot 4 RPG

Pixel-art RPG with a reusable map factory.

## Artwork quality
**Read [High-quality asset policy](docs/ASSET_QUALITY_POLICY.md) before producing or changing sprites.** Preserve stable IDs. Use the best visually reviewed source, and replace an older sprite when a candidate is demonstrably better.

The [asset catalog](map_factory/metadata/asset_index.json) contains 218 planned slots. The repository currently contains 48 first-pass individual PNG files (22 floors, 16 shadows, 10 UI elements). The extracted 152-file concept pack must be imported and cleaned before it can be considered production-ready.

[Upload an asset ZIP for automatic import](map_factory/incoming/README.md) • [Map Factory](map_factory/README.md) • [Art Pipeline](docs/ART_PIPELINE.md)

## Running
Open `project.godot` in Godot 4. The room factory loads `map_factory/rooms/hero_room.json` and renders available sprites; missing images appear as placeholders.
