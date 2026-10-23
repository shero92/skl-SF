# Hero Room composition review — not an art-quality claim

## Reference and scope

Source comparison: the user's uploaded *Hero’s Seaside Sanctuary* screenshot. The source was provided in chat, not yet committed to map_factory/references; therefore its SHA-256 is not falsely claimed in the map JSON.

This map-only revision changes no actor sprites, abilities, NPCs or interface assets.

## Root problem

Earlier screenshots looked like a **floating rectangular tile grid** with nice individual props: side/back walls were incomplete, no meaningful front entrance parapet, an overly tall empty sky, and the center nautical floor inlay disappeared.

## What the factory changed

- Hero Room v0001 remains immutable in versions/v0001.json.
- v0002: re-arranged 39 originally placed parts into a coherent seaside sanctuary and placed additional ruin, railing, stair, side-banner, ivy and distant island instances from existing reusable IDs. A coherent front entrance with ST006, ST001–ST005, ST007–ST008 now opens between front stone railings. Reduced excessively high sky and grouped the bed/bookshelf and desk/bookshelf zones.
- Technical bug fixed: Godot JSON tile override coordinate keys were not normalized, silently dropping the nine compass floor IDs. RoomFactory now uses integer grid keys. CI verifies actual floor sprite IDs/textures; the corrected v0002 Godot image shows the full gold-on-sapphire emblem.
- v0003: removed two ST014 parapet instances that displayed unwanted source-sheet labels over the water, and removed their stale navigation obstacle reference. Their shared PNG images were NOT deleted.
- Set per-map navigation metadata to blocked-by-default with reviewed future floor/entrance regions; this is not yet connected to character movement physics.

## Screenshot evidence (real Godot build)

- Before: [v0001 image](previews/map_factory_renders/hero_room_01_v0001.png).
- Recomposition before tile-coordinate fix: [v0002 initial screenshot](previews/map_factory_renders/hero_room_01_v0002.png) — this path is updated with the corrected build.
- Cleaned latest layout: [v0003 image](previews/map_factory_renders/hero_room_01_v0003.png).

## Honest remaining mismatch

The current layout is closer but **not identical to the source**: the illustrated sanctuary has a more organic broken-stone perimeter, richer asymmetrical sky/rock background, stronger sunlight and shadow gradients, and some unique props not yet modeled as separate independent assets. Floor repetition is more apparent than in the source. These require further art and composition iterations, not character changes.

**Current state:** visual_qa=needs_review; do not claim 100% match or human artistic approval yet.
