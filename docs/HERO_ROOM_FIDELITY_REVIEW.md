# Hero Room reference-fidelity gap review (v0007)

**Result: improved, but NOT close enough to the original Hero's Room image to approve.**

The previous photograph the user flagged was v0004. Comparison of the subsequent real Godot captures v0005, v0006 and v0007 showed that high-quality individual props do not guarantee a convincing assembled room.

## Confirmed fixes
- v0005: floor silhouette now supports per-row cell spans and empty water-facing cutouts. The terrace uses **147 of 170 grid cells** and the opening beneath the arch shows sea.
- v0005: eliminated four large distant cutouts with hard rectangular picture boundaries; retained smaller islands.
- v0006: tested source limestone F001/F002; their thick dark tile frames looked **worse** when downscaled whole.
- v0007: uses only the inner painted limestone texture (non-destructive AtlasTexture crop) and very thin warm grout lines, leaving all original source PNGs untouched.
- The floor compass and independent sprite library remain intact. Characters/UI were not changed.

## Actual screenshots
- [Original v0004 before these changes](previews/map_factory_renders/hero_room_01_v0004.png)
- [v0005 shaped terrace](previews/map_factory_renders/hero_room_01_v0005.png)
- [v0006 rejected flooring trial](previews/map_factory_renders/hero_room_01_v0006.png)
- [v0007 natural floor and mask](previews/map_factory_renders/hero_room_01_v0007.png)

## Why the result is still visibly wrong

1. **Critical missing centerpiece:** The screenshot reference contains a sculptural antlered skull/shrine in flowering foliage in the upper-center-right. The asset catalog has **no matching independent object image**. Merely shifting existing furniture will not reconstruct it. New actual artist-level sprite art is required, then add the sprite ID and place it in the map.
2. **Architecture depth:** The original reference has stone walls and parapets that physically connect in perspective. The current room uses simpler separate sprites, so the side walls and entrance still read as separate stacked objects.
3. **Scene lighting:** The reference is sunlit with strong warm diagonally cast shadow planes and detailed contact shades. Current runtime shading is comparatively flat.
4. **Sea and horizon:** The current sky/cloud strips and water are less natural/detailed than the reference; further visual work is necessary.
5. **Floor composition:** The v0007 flooring is less gridded than v0004 but the irregular platform still needs more coherent chipped stone edges, proper wall thickness and elevation. Existing room version should not be marked approved.

## Required next art actions (map-only)

See [machine-readable visual gap inventory](../map_factory/maps/hero_room_01/reference_gaps.json). Reserve the central shrine as a genuinely new independent environmental sprite (`O027`, proposed only, **not in the library yet**). Create or curate deep cliffside border segments, front stone parapets and matching sun shadows. Rebuild the map from the parts, render it in Godot and compare with the source again. Do not falsely claim any missing PNG has been made.

**Current QA:** `needs_review` and all existing reusable art is still subject to artistic approval.
