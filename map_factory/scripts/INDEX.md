# Godot map factory scripts

- [room_factory.gd](room_factory.gd): constructs the environment-only map from registered JSON snapshots; layering, draw order, placement and occlusion.
- [asset_catalog.gd](asset_catalog.gd): loads and resolves reusable asset IDs/paths.
- [asset_factory.gd](asset_factory.gd): instantiates individual assets and their metadata.
- [shadow_factory.gd](shadow_factory.gd): shadow sprites and offsets.

For four-way rotations also inspect `tools/map_factory_orientation.py` and [FOUR_DIRECTION_BLOCKS.md](../FOUR_DIRECTION_BLOCKS.md). Preview: `scenes/map_factory_preview.gd`. See [all files](FILES.md).
