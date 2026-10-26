> Current baseline (2026-10-26): Hero Room v0011, 84 placements, 38 architecture placements with 2 collision-enabled. The narrative below is historical v0010 evidence, not a current visual review. See HERO_ROOM_RECOVERY_AUDIT.md. TASK-0033 is merged; art calibration and map motion configuration remain.

# Hero Room: why the Factory scene does not match the artwork

Inputs supplied by user in conversation: factory build screenshot 1536 x 1024 and desired artistic reference 1448 x 1086. Neither uploaded screenshot is automatically present in the git repository. The latest Hero Room is v0010. Its visual QA remains needs_review.

## Verified configuration and deficits

- The renderer lays down a square 17 x 10 grid of 64-pixel cells, with a stepped cell footprint. The reference has a strongly three-quarter coastal stone island silhouette with massive cliff thickness. Masking cells does not project a flat grid into a three-quarter perspective.
- There are 78 environment blocks. Of 34 wall/architecture/stair blocks, only 2 have collision enabled in their effective catalog/placement metadata. Never assume this map is walkable by physics rules from render success alone.
- The authoritative map source_image.path and source_image.sha256 are BOTH null. Automated source-versus-render QA cannot be reproduced from the committed project until the actual original image is committed and referenced in the next room revision.
- Earlier fixed global render passes put ALL decoration at z40 and ALL wall sprites at z30, regardless of camera-distance/foot-contact y. Furniture can wrongly overpaint nearer walls. The factory now supports an opt-in unified world_y_sort mode but it has not been reviewed or activated in historic Hero Room v0010.
- Many detailed art pieces were cut or assembled as independent single-view PNGs. Four true artist-painted north/east/south/west views are not registered for furniture and walls. Simply rotating vertical pixel art makes perspective, lighting and object bases wrong.
- The reference's masonry joints, contiguous side elevation, front entrance, skull centerpiece, sea splash, and warm diagonal sunlight are parts of ONE carefully composed environment. The game renders separate sprites with approximate pivots and no geometry-aware perspective placement, which causes visible mismatches despite good PNG detail.
- CI currently checks JSON integrity, asset presence and Godot instantiation, but does not automatically measure whole-scene reference fidelity. Passing CI is not a visual approval.

## Factory fixes implemented now

1. Four cardinal facing values: north 0 degrees, east 90, south 180, west 270. A full 360 turn returns to north.
2. Two rotation methods: raw node+collision rotation (flat sprites) or four distinct registered directional sprite variants (3/4-view art). Perspective views cannot be faked from one PNG.
3. Rotation of floor overrides around tile CENTER (without shifting the floor grid).
4. Parent wall direction turns the offset of any mounted secondary decoration.
5. The new optional occlusion_mode world_y_sort interleaves walls and props according to depth anchors rather than category z-bands.
6. Reference approval validation blocks maps without a saved source image path and hash.
7. Regression tests exercise all four directions, collision shapes, variant selection, floor pivot, old-map compatibility and world sort.

## Still needed before claiming the Hero Room is a faithful rebuild

- Preserve reference image in the repository and attach its actual SHA-256; then render at matching crop/scale for comparison.
- Design and encode a three-quarter projection/position system appropriate to the reference. This remains a separate development task: the existing floor painter is flat orthogonal tile layout.
- Author complete seamless angled walls, front/side cliff faces, staircase transitions and 4-view perspective assets. Detailed single-view cutouts cannot satisfy a turntable-camera requirement.
- Correct origins to physical ground contact. Turn on and validate unified world sort only in an independently reviewed map revision.
- Complete and validate environment collision + altitude + navigation data; do not touch character controllers or special abilities.
- Tune contact/long sunlight shadows using the actual reference. Compare a real Godot screenshot against it and fix the largest deviations before approving quality.

Status: technical block rotation delivered, but visual reference matching and complete collision/navigation are not finished. Character assets, gameplay scripts, NPCs, UI and dialogue were not changed.
