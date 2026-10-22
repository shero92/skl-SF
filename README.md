# skl-SF — Fantasy seaside tactical RPG

Godot 4 project with reusable map parts and a data-driven room factory.

## How to run
1. Clone or download this repository.
2. Import `project.godot` with **Godot 4.4.1** (or a compatible Godot 4 release).
3. Run the project (**F5**).
4. Use **WASD / arrow keys** to move the temporary hero actor.
5. Stand near either guardian, bed, table or chest and press **E** to interact. Press **E / Enter / Space** to continue dialogue.

The actors are gameplay placeholders. **There are 12 original first-pass character sprite sheets and two portraits; none are artist-approved yet.** They are intentionally not described as final art. The hero, guardians and follower now use these animation strips.

## Assets and QA
- **218** catalog entries with stable IDs and reuse across rooms.
- **175** independent sprite PNG files currently stored under `map_factory/parts/`.
- **43** remaining PNGs not created.
- **175** available images remain unapproved drafts (`needs_cleanup`) until their native visual quality is reviewed.

Browse the [visual review gallery](docs/ASSET_GALLERY.md), [automatic audit](docs/ASSET_AUDIT.md), and [asset index](map_factory/metadata/asset_index.json).

**Read the mandatory [asset quality and replacement policy](docs/ASSET_QUALITY_POLICY.md) and [AGENTS.md](AGENTS.md) before changing any sprites.** Replace an old file only when the new candidate is verifiably better and technically usable. Stable IDs and metadata must stay consistent.

## Room development
- Room data: `map_factory/rooms/hero_room.json`
- Scene composition: `map_factory/scripts/room_factory.gd`
- Sprite/collision/shadow definitions: `map_factory/scripts/asset_factory.gd` and `shadow_factory.gd`
- Hero movement / dialogue: `scenes/player.gd`, `scenes/dialogue_ui.gd`, `scenes/main.gd`
- Quick headless test: `.github/workflows/godot_validate.yml`
- PNG catalog validator: `tools/audit_assets.py`
- Review gallery builder: `tools/build_asset_previews.py`

## Current visual limitations
The current ocean is a flat-colored backdrop. Some architecture and prop PNGs were extracted from AI concept sheets and may have halo or label fragments, inconsistent dimensions, and non-seamless edges. All must pass human visual QA before their status changes to `ready`. This is a playable scaffold, **not** a production-complete recreation of the reference image.

## Reusing assets in other maps
Create a new JSON under `map_factory/rooms/`. Use the stable asset IDs in `background_objects`, `ground_overlays`, `back_objects`, `objects` and `front_objects`. To load it, pass its resource path to `RoomFactory.build_room(path, self)`.

See [Hero Room notes](map_factory/rooms/HERO_ROOM_NOTES.md) and [Map Factory guide](map_factory/README.md).
