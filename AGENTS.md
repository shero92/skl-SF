# Agent instructions for skl-SF — MAP FACTORY FOCUS

**The present workstream is MAPS AND ROOMS ONLY. Do not generate, regenerate, curate, import, move, or change any character sprites, NPC/gameplay scripts, dialogue portraits, dialogue UI or their metadata.** Previously existing gameplay code may remain, untouched.

Before map work, read:
- `map_factory/MAP_FACTORY_WORKFLOW.md`
- `map_factory/maps/index.json` and the relevant `map_factory/maps/<map_id>/latest.json`
- `map_factory/metadata/asset_index.json`
- `docs/ASSET_QUALITY_POLICY.md`, `docs/REFERENCE_ART_DIRECTION.md`

When a new AI room image is provided:
1. Compare it to the **latest** registered map version, not an old room screenshot.
2. Match every reusable stone block, furniture item, plant, effect and backdrop to a registered asset ID.
3. Create independent clean PNGs only for genuinely new environmental parts; do not claim a full AI image is already segmented.
4. Record the source image hash, map change manifest, per-block placement/layer, native pixel_size, anchor, shadow, collision, scale, and provenance.
5. Call the map intake/versioning pipeline. Retain `versions/v000N.json` and update `latest.json` + `blocks/latest.json` automatically.
6. Keep every existing good asset intact; stage same-ID candidate replacements for review. Do not claim unreviewed art is 100% reference quality.
7. Validate registry, map-only rules, PNG catalog and Godot map preview before reporting a successful push.

No change to character category (`characters`), user interface (`ui`), player movement, dialogue UI, or NPC gameplay is authorized by this map-only workflow. Existing game preview remains intact; use `scenes/map_factory_preview.tscn` for map work.
