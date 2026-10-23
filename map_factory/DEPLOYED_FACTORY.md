# Map Factory — deployed reusable workflow

This factory builds **environment-only maps in Godot 4** from a reusable PNG asset catalog and explicit room/map metadata. It is prepared to accept new AI-generated room images for *AI-assisted* analysis, not fully automatic image segmentation.

## What already works

- Create an independent map from one of five presets: `indoor_room`, `courtyard`, `dungeon`, `coast`, `sky_island`.
- Clone an existing map at its *latest* revision, or edit the latest map with a guarded patch.
- Reuse IDs from `map_factory/metadata/asset_index.json`, or import a genuinely new, independent environmental PNG with complete metadata.
- Assemble arbitrary valid JSON map layers, repeating floors, architecture, furniture, vegetation and optional water/effects in Godot.
- Preserve immutable snapshots and a per-instance block index for each map.
- Validate map-side collision/shadows, walk/fly/swim regions, elevation and clearance annotations. The character controller is intentionally not part of this subsystem.
- Build/test **every** registered map in headless Godot CI. Choose an individual map in the environment-only preview.
- Refuse incomplete reference-image drafts, unknown IDs, forbidden character/UI assets, stale base revisions and silently overwritten sprites.

## Creating a new map from an image

Install Pillow locally if needed: `python -m pip install "Pillow>=10,<13"`.

**1. Register the image and create an analysis job:**
```bash
python tools/prepare_map_reference.py \
  --image "/path/to/my_room.png" \
  --map-id my_room_01 \
  --mode create \
  --preset indoor_room
```

For an update to an existing map:
```bash
python tools/prepare_map_reference.py \
  --image "/path/to/my_new_room_version.png" \
  --map-id my_room_01 \
  --mode patch
```

To create a different room based on the latest version of an older map, use `--mode clone --from-map hero_room_01` with a **new** `--map-id`.

The preparer copies your image to `map_factory/references/`, hashes it and writes a **draft** under `map_factory/intake/drafts/`. It records the latest base version/hash when applicable; it does NOT fake an assembled room.

**2. Give the image and draft to AI for block-level analysis.** AI should compare the reference to existing reusable assets, identify pieces, choose existing IDs where possible, generate clean independent environmental PNG files only for missing IDs, and enter the correct layers, world coordinates, scale, rotation, shadows, collisions and optional navigation. Add new files to `map_factory/intake/assets/` and describe them in the draft `assets` array. Check screenshot occlusion and missing back sides; do not call uncertain art approved.

**3. Review the manifest**, including environment and art quality. Mark `analysis_status` as `reviewed`, retain `visual_qa: {"status":"needs_review"}` until a Godot screenshot has been checked, and move the manifest into `map_factory/intake/pending/` with a unique filename.

**4. Push the manifest, source image, and any new PNG files.** GitHub Actions processes pending manifests once, verifies the reference hash, records a receipt and publishes versioned map JSON + per-block metadata. The workflow explicitly rejects image-only jobs still marked `pending_review`.

**5. Preview the room in Godot 4:** open `scenes/map_factory_preview.tscn`, set the `map_id` export in the Inspector and run F6. Alternatively, run headless:
```bash
godot --headless --path . --editor --quit
godot --headless --path . res://scenes/map_factory_preview.tscn --quit-after 30 -- --map-id=my_room_01
```

**6. Compare with the reference image**, fix the layer/order/detail/shadow/lighting problems, and submit another patch from the latest version. The map is only `visual_qa=approved` with a recorded reviewer, source hash and verified preview.

## Existing maps to test

- `hero_room_01`: existing initial seaside room, v0001.
- `courtyard_demo_01`: independent courtyard preset built from shared pieces via the same manifest intake; v0002.

Map registry: `map_factory/maps/index.json`. Latest build: `map_factory/maps/<map_id>/latest.json`. Resolved parts: `map_factory/maps/<map_id>/blocks/latest.json`.

## Required commands for developers

```bash
python tools/map_factory_cli.py new --map-id town_square_01 --preset courtyard
python tools/map_factory_cli.py clone --map-id guest_room_01 --from-map hero_room_01
python tools/map_factory_cli.py validate
python -m unittest discover -s tools/tests -p 'test_map*.py' -v
python tools/verify_map_assets.py
```

New standalone map creation is **not tied to Hero Room geometry or ocean**. Each future map can override canvas size, tile grid, ground origin, environmental layers and effects in its JSON manifest.

## Known boundaries, not falsely marked complete

The factory cannot independently turn arbitrary scene pixels into correct unobstructed sprites without an AI/artist producing and reviewing them. It cannot prove 100% visual fidelity through CI alone. The navigation JSON is structurally validated but **physical flight, swimming and actor-specific abilities require a separate gameplay system**. No characters, dialogue or UI assets are modified by map factory tasks.

Mandatory rules: [MAP_FACTORY_RULES.md](MAP_FACTORY_RULES.md).
