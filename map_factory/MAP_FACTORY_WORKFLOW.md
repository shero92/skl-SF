# AI-powered map factory: map blocks ONLY

Use this area for **landscape, floor, walls, architecture, stairs, furniture, vegetation, props, shadows, lighting, and reusable room composition**.

**Never import, generate, change or place characters, dialogue portraits, NPCs or game UI here.** Those systems are separate.

## Workflow after you create a new AI room image

1. Put the complete image at `map_factory/references/<room>.png` (source-of-truth artwork, not a reusable sprite).
2. Compare the new image with the last map: `map_factory/maps/<map_id>/latest.json`.
3. Identify each visible reusable part by an existing ID in `map_factory/metadata/asset_index.json`. Do **not** create a new PNG for a reused component.
4. If the image contains a genuinely new part, generate a **separate clean RGBA PNG**, upload to `map_factory/intake/assets/`, then give its metadata in the manifest's `assets` array. The factory does not magically segment a scene screenshot.
5. Write the room change manifest to `map_factory/intake/pending/<unique_revision_name>.json`, using `mode: patch` for an existing map (with `base_version` equal to the latest version) or `mode: clone` for a new map based on the **latest** version of an existing map.
6. On push, GitHub Actions validates assets and layout, stages same-ID replacements for review, creates immutable version JSON files and updates the map registry.
7. Godot's map-only preview scene reads `map_factory/maps/index.json` and constructs the current `latest.json` entirely from indexed parts.

### Manifest operations
- `set_tile`: x/y + registered floor ID. Set `id: null` to remove an override.
- `add_block`: layer + block with `id`, unique `instance_id`, x/y, scale; optional shadow, collision, flip_h, rotation_degrees, z_index.
- `update_block`: unique `instance_id`, partial `set` dictionary; can move the block to another layer.
- `remove_block`: unique `instance_id`.
- `set_property`: only approved map properties (ocean, size, floor_ids, effects, canvas_size, description, source_image etc.).

The snapshot has a fully materialized floor grid, placed objects by stable ID, layer and draw order, optional shadows/collision, plus the latest version/hash. Every change creates `versions/v000N.json` and `changes/v000N.json`. Older versions are never modified.

Examples: [patch](examples/update_hero_room.json), [clone](examples/clone_guest_room.json).

### Manual preview/validation
```bash
python tools/map_factory_cli.py list
python tools/map_factory_cli.py validate
python tools/map_factory_cli.py preview --manifest map_factory/intake/examples/update_hero_room.json
python tools/map_factory_cli.py apply --manifest map_factory/intake/examples/update_hero_room.json
python tools/map_factory_cli.py clone --map-id example_room_02 --from-map hero_room_01
```
The `preview` command checks a proposed diff without modifying the repository. **Do not apply the example repeatedly**: its base version is 1.

### New part intake (example)
```json
{
  "id": "P023",
  "name": "Seaside Wooden Chair",
  "category": "furniture",
  "subtype": "chair",
  "file": "map_factory/intake/assets/P023_Seaside_Wooden_Chair.png",
  "origin": [48, 124],
  "tags": ["wood", "chair"],
  "collision": {"enabled": true, "size": [48, 20], "offset": [0, -10]},
  "shadow": {"type": "chair", "opacity": 0.35, "offset_x": 3, "offset_y": 3}
}
```
Put that object under the top-level `assets` array of the same AI room manifest. The importer validates PNG transparency and dimensions and updates global `asset_index.json`; new assets remain `needs_cleanup`. If an existing ID differs, the new PNG goes to `map_factory/candidates/`, never replacing approved source artwork automatically.

### Preview without characters
Open `scenes/map_factory_preview.tscn` in Godot 4 and **Run Current Scene (F6)**. It loads the most recent map via registry. It does not instantiate gameplay actors, dialogue or UI.

### Canonical files
- Global reusable assets and technical metadata: `map_factory/metadata/asset_index.json`.
- Map registry: `map_factory/maps/index.json`.
- Latest map and immutable snapshots: `map_factory/maps/<map_id>/latest.json`, `versions/v000N.json`.
- AI source images: `map_factory/references/`.
- AI layout/asset intake: `map_factory/intake/pending/` and `map_factory/intake/assets/`.
- Map change receipts: `map_factory/intake/processed/`.

**Quality policy:** consult `docs/ASSET_QUALITY_POLICY.md`. Map-only assets must pass visual QA; no PNG is upgraded based on file size alone.
