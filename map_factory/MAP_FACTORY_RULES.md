# Mandatory Map Factory Rules — Image to Reusable Playable Environment (v1)

This is the standing rulebook for ALL future map/room work. It is a production target, not a claim that fully automatic screenshot decomposition or flying gameplay exists today.

## Scope is environment only
Work on tiles, blocks, terrain, rooms, buildings, trees, water, stairs, roofs, doors, furniture, decorations, lighting, shadows, collision, navigation data, and map-to-map connections. NEVER modify character images, actor movement, gameplay abilities, portraits, NPC data or dialogue UI. Map metadata may describe accessible regions, but actors decide their own abilities elsewhere.

## Mandatory order for every new AI-created map image

1. PRESERVE: save the supplied reference picture under map_factory/references with a SHA-256 hash, size, pixel-art style, viewpoint and world/grid scale. If the image only appears in chat, do not claim it has been uploaded to the repository.
2. LATEST: read map_factory/maps/index.json, the intended map's latest.json, blocks/latest.json, and the global asset_index.json. Always patch the current last revision; to make another room, clone the latest related map or start from an explicit template.
3. SEMANTIC ANALYSIS: identify terrain, roofs, floors, stairs, walls, objects, furniture, plants, water, distant scenery and effects; estimate bounds, layering and ground contact. Mark occluded or unclear details as inferred/review needed.
4. REUSE FIRST: match each discovered object with the current reusable ID and do not generate duplicate art for another placement. One texture may be referenced by many instance_ids.
5. CREATE ONLY MISSING ART: generate true independent detailed PNG sprites and tiles with transparent RGBA where appropriate, including any hidden part necessary for reuse. Do not pretend a whole screenshot is already individually segmented; do not count blurry upscaling as quality improvement. Store uncertain same-ID replacements as candidates rather than overwriting.
6. ASSET METADATA: record stable ID, clear filename, category/subtype, actual native pixel_size, anchor/pivot, tileability/variant, collision footprint, shadow opacity/offset/direction, brightness/light, transparency, provenance/hash, and QA status. Keep a single shared asset catalog across maps.
7. MAP METADATA: store floor cells, all instance IDs, asset IDs, world x/y, size/scale, rotation, z/y-sort and front/back/background layers, environment effects, optional per-instance shadow/collision overrides, and connections. Publish immutable versions and resolved per-block metadata. Never flatten the finished room into a single background image to simulate construction.
8. NAVIGATION: describe walkable/swimmable/flyable cells and regions, surface elevation, ceiling clearance, physical obstacles with altitude bands, doors and stairs links. Default UNKNOWN traversal to blocked. The environment says what is possible; character/gameplay logic decides what individual actors are capable of.
9. COMPARE: build the map-only preview inside Godot and visually compare an equal-scale rendered screenshot against the original reference. Inspect composition, perspective, edges, palette, pixel density, seams, layering/occlusion, shadows and light, collision bounds, stairs and flight clearance. Fix discrepancies.
10. COMMIT: store original image provenance, independent new PNGs, asset metadata, map metadata, movement annotations, QA and remaining concerns. Only replace proven weaker sprites and only claim exact/high-fidelity match after recorded visual approval.

## Hard separation: map art vs map data

Output A: detailed individually reusable environmental image parts, never game characters.

Output B: a deterministic layered and versioned JSON room/map with the IDs of those parts, metadata, material, collisions, navigation and environment behavior. The runtime must assemble sprites and tiles, not display the original image as an interactive illusion.

## Map-side traversal contract

Navigation metadata is optional for old maps, but REQUIRED before labeling a NEW map gameplay-ready. The map factory currently validates navigation metadata when present; a future gameplay system must consume it to implement actual pathfinding/flight and character abilities.

All navigation coordinates use cells, while map objects use world pixels. Navigation explicitly specifies origin, cell_size and grid_size. Movement modes in this contract are walk, fly, swim. Unknown cells default to false for all modes. Regions are evaluated in order; later regions override earlier ones. A region may explicitly use an empty allow list to designate a solid/forbidden zone. Each region carries a surface, rectangle, permitted modes, optional per-mode required abilities, floor_height, ceiling_height (nullable) and review status. Physical obstacles reference existing placed instance_ids and describe altitude bands and blocked modes. Stair/door links connect cells and specify permitted modes/requirements.

Flight is NOT simply disabling ground collisions. A flyer still respects ceiling clearance, solid walls extending above its flight altitude, world bounds, and other obstacles. Z-index is drawing order and is NOT physical height.

Character specials (can_fly, can_swim, water_walk, unlock_door, etc.) are queries supplied to a future movement system. The map should not grant special abilities, select a character, or modify gameplay code.

Shape example: map_factory/metadata/navigation_example.json. Navigation validity checks are enforced by tools/map_factory_cli.py when present. Neither pathfinding nor altitude-aware collision is integrated into the game yet.

## Quality assurance and approval

Follow docs/ASSET_QUALITY_POLICY.md and docs/REFERENCE_ART_DIRECTION.md. Keep correct top-down three-quarter perspective, crisp rich true pixel-art detail, sunlight direction, warm limestone, cobalt/gold ornament, layered ivy and contact shadows. Do not equate image size with quality.

New assets remain needs_cleanup until visual QA. Set visual_qa.status = needs_review for new maps. visual_qa.status = approved requires reference_sha256, Godot preview_path and reviewer. Unknown movement zones must be checked or remain blocked. Do not make a 100% fidelity claim based solely on an automatic test.

## Versioning and provenance

- Latest map snapshot and its hash are authoritative; base_version and preferably base_sha256 prevent stale AI overwrites.
- Old versions are immutable, with versions/v000N.json, blocks/v000N.json and changes/v000N.json.
- Reuse existing assets rather than renaming them, and retain independent PNG files for genuinely new components.
- New map images are references only, not premade in-game scenery used instead of blocks.
- Record inferred/hidden sprite geometry as inference, not directly seen evidence.

## Accurate capability boundaries

CURRENT: catalog indexing and individual PNG intake, reusable map block placement, layered Godot preview, versioned JSON, collision/shadow configuration, and optional navigation metadata validation.

NOT YET IMPLEMENTED: foolproof image-to-perfect-sprite decomposition, automatic artist-level detail reconstruction and final image QA, baked navigation graphs/pathfinding, altitude-aware flying collision, and actual character ability enforcement. These must never be falsely reported as completed.

## Strictly protected

Never modify map_factory/parts/characters, map_factory/parts/ui, any character/UI asset records, scenes/player.gd, actor/NPC/companion scripts, or dialogue/HUD. The Map Factory workflow owns environment files only.
