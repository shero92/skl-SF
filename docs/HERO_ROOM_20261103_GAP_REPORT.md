# Hero Room v0013 vs owner target (2026-11-03)

Evidence: real Godot capture `docs/previews/map_factory_renders/hero_room_01_v0013.png` (1536x1024) built by Map Factory from registered assets; side by side: `hero_room_01_v0013_vs_target.png` (left target, right render). `visual_approval: false`.

Counts (v0013): 127 placed blocks, 57 distinct PNG paths (plus the 12 approved G01-G12 floor tiles); categories W43 L26 A12 P12 F10 B9 R8 D7. Tests 51/51, Godot import and smoke pass.

| Zone | Status | Gap / next step |
|---|---|---|
| Ocean, sky, sea stacks | partial | Water and distant stacks present; no tall cliff mass, foam grid or sea arches; flat azure tiles. Needs cliff/sea-stack art at target scale (ART request). |
| Central arch | matched in composition | Arch, columns, ivy, flowers present; scale slightly small. |
| Three-sided ruins | partial | Side walls exist as thin front-facing stacks; the target has thick connected ruined walls with irregular tops and a rear wall behind the beds/shelves. Missing side-facing wall art (ART request). |
| Floor | partial | Approved G tiles, but a rectangular footprint; the target has an irregular terrace edge and perspective grid. |
| Bed zone | matched | Bed, rug, bedside table present; shell/flowers on the table missing. |
| Study area | partial | Table, rug, bookcase, lanterns, scrolls present; chest, armillary sphere missing. |
| Compass | matched | Centre of floor, unobstructed. |
| Lantern light | partial | 26 L-series placements with glow overlays; light is not cast onto surfaces. |
| Shadows | missing | Target has diagonal sunlight shafts and contact shadows; no registered overlay art. ART request. |
| Front perimeter and cliffs | missing | Low wall run exists; no rocky cliff base, rope posts, planters at target density. ART requests. |
| Stairs | partial | Present and centred; side posts shorter than the target. |

Attempt v0014 (`--reference-relayout`, not merged): capture saved in the owner's local backup folder; it moved the stairs off the canvas bottom and the bedside table off the floor, so v0013 stays the delivered version.

Missing art (specific requests for Codex image_gen, not for Aider): thick connected ruined wall blocks facing left/right; large cliff base segments at target scale with ivy; wooden rope posts; sunlight shaft floor overlays and cast shadow decals; shell and small chest props.
