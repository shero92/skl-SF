# Agent instructions for skl-SF — MAP FACTORY FOCUS

**The present workstream is MAPS AND ROOMS ONLY. Do not generate, regenerate, curate, import, move, or change any character sprites, NPC/gameplay scripts, dialogue portraits, dialogue UI or their metadata.** Previously existing gameplay code may remain, untouched.

## Efficient file navigation (all coding agents)

- Start from `INDEX.md` -> the matching folder's `INDEX.md` -> target files. Each folder's generated `FILES.md` lists exact names; never load all inventories into context.
- For map tasks, read `map_factory/MAP_FACTORY_RULES.md` (MANDATORY). Then open only the relevant additional documentation: workflow for intake, layer schema for rendering, four-facing guide for rotations, art direction/quality policy for visual asset work.
- Use `map_factory/maps/index.json` to confirm latest map versions; read only the relevant map's `latest.json` and targeted entries in `metadata/asset_index.json`. Do not dump the full catalog or historic versions without a concrete reason.
- After adding, deleting or renaming files, run `python tools/generate_project_indexes.py --write` and stage updated `FILES.md` inventories. CI enforces `--check`.
- Share one task per agent branch/worktree and propose a PR; avoid concurrent edits to the same files, avoid direct pushes to main, and do not authorize artwork or reference fidelity without a verified Godot render.
- Use `PROJECT.md` for product context, `PLAN.md` for roadmap, `STATUS.md` for a short handoff only when state materially changes. Report changed paths, commands actually run, results and one next step.

## Before map work

Read the mandatory rules above and use the targeted paths in `INDEX.md`; map-only scope and quality protections below remain in force.

When a new AI room image is provided:
1. Compare it to the **latest** registered map version, not an old room screenshot.
2. Match every reusable stone block, furniture item, plant, effect and backdrop to a registered asset ID.
3. Create independent clean PNGs only for genuinely new environmental parts; do not claim a full AI image is already segmented.
4. Record the source image hash, map change manifest, per-block placement/layer, native pixel_size, anchor, shadow, collision, scale, and provenance.
5. Call the map intake/versioning pipeline. Retain `versions/v000N.json` and update `latest.json` + `blocks/latest.json` automatically.
6. Keep every existing good asset intact; stage same-ID candidate replacements for review. Do not claim unreviewed art is 100% reference quality.
7. Validate registry, map-only rules, PNG catalog and Godot map preview before reporting a successful push.

No change to character category (`characters`), user interface (`ui`), player movement, dialogue UI, or NPC gameplay is authorized by this map-only workflow. Existing game preview remains intact; use `scenes/map_factory_preview.tscn` for map work.

## Mandatory image-to-map production contract

Future agents MUST follow map_factory/MAP_FACTORY_RULES.md before any image/room/map task. Use the user's image as a reference, compare with the latest map, reuse good assets, create individual environmental PNG files only for genuinely missing parts, register per-part metadata, assemble the room with numbered immutable JSON versions, describe walk/fly/swim restrictions and obstacle altitude, render and compare against the source, and commit only reviewed outcomes.

Ability ownership belongs to a separate gameplay system: map permissions and clearance are NOT character abilities. Keep unreviewed navigation blocked; do not claim visual equality, working pathfinding or flying physics unless verified in Godot. No character or UI edits.

Future user-supplied room/map photos should start with `tools/prepare_map_reference.py` to preserve the original and pin the last map version. Follow `map_factory/DEPLOYED_FACTORY.md`. Draft images must NOT be auto-published as finished maps: provide independent PNGs for missing parts, reviewed block placements, and set analysis_status=reviewed before moving a manifest into pending. Map work remains strictly environment-only.

## Mandatory five-layer map rendering convention

When authoring a room or map, follow map_factory/LAYER_SCHEMA.md. The compiled layer_stack and per-map layers/latest.json must specify **background, ground, walls, decorations, shadows** with correct owner and mount metadata. Wall ornaments must use mount_on plus mount_offset if they depend on wall placement. Every new map revision rebuilds derived layer indices; never alter old immutable snapshots. Shadows form the fifth *data* pass but draw below wall and decoration sprites at z20 for correct compositing. Check map_factory/metadata/room_block_quality.json: all environmental PNG files must exist, but needs_cleanup is not artistic approval. Do not touch characters/UI.

## Cardinal block orientation and scene fidelity

All future map work must follow map_factory/FOUR_DIRECTION_BLOCKS.md. The renderer supports north/east/south/west facings, turntable 90-degree rotation for flat props and four DISTINCT real perspective image variants for 3/4 objects. If art variants are absent, do not claim the 360-degree asset looks correct. Wall-mounted decor rotates offset with its parent. Opt-in world_y_sort can fix nearer-wall occlusion when bottom pivots are correct. Keep characters, actor control and dialogue out of scope. Read docs/MAP_FACTORY_REFERENCE_DIAGNOSIS.md before changing Hero Room. Save a reference image in the repo and visually QA a Godot render before approving any map.
