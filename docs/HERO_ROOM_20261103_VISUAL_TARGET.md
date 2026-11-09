# Hero Room — owner target composition (2026-11-03)

## Reference identity and intake gate

The **new** owner-supplied target is a separate image from `map_factory/references/hero_room_01_original.png` (the previously approved 1448×1086 reference). Do not overwrite or relabel historical references.

- Target filename in repo (not yet committed): `map_factory/references/hero_room_01_target_20261103.png`
- Supplied through owner chat attachment: `3adba40a-8d9a-49fe-961b-7a900457d5e0(5).png`
- Image dimensions: **1536×1024**.
- Required SHA-256 of original uploaded PNG: `47a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b`.
- **Do not claim the file is in the repository yet.** TASK-0098 (Claude) imports the actual image from a verified owner-provided local file; do not regenerate it or substitute another image. If unavailable, stop that task with a concrete request for the file. Aider must not silently substitute historical `hero_room_reference_v2.png`.
- This is a **design target**, not approval of any reconstructed render. A source screenshot may only be used as a review reference, **not a rendered background/screenshot collage**.

## Visually observable composition (target 1536×1024)

All coordinates below are approximate **image-space review regions**, not precise sprite anchors. The tasks must convert them into world-space and footpoint anchors using actual PNG measurements and the room renderer.

| Zone | Approx. image-space target | Required composition |
|---|---|---|
| Open ocean/sky | x=0–1536, y=0–360 | Bright azure water, foam, distant sea stacks, coastal arches, sunlit clouds; no rectangular backdrops/cutout borders |
| Rear arch | x=555–990, y=0–390 | Large central open stone arch on columns, heavy ivy, white and orange flowers; sea visibly unobstructed within opening |
| Left architecture | x=100–640, y=130–700 | Connected broken limestone rear/side wall, parapet, hanging blue-gold banners, climbing vines, warm hanging lanterns |
| Right architecture | x=965–1510, y=100–710 | Connected back/right wall, arched wooden door, banners, warm lanterns and upper shelf details |
| Main floor | x=190–1390, y=315–800 | Continuous perspective-aware warm sandstone tile grid with irregular terrace perimeter; distinct from water |
| Bed zone | x=220–580, y=335–665 | Royal wooden bed with blue/gold blanket, white pillows, blue ornate rug; bookshelf, shells and flowers behind |
| Work/dining zone | x=1000–1350, y=430–675 | Wooden desk/table, blue/gold rug, books, map, fruit, jug, warm tabletop light; shelves and pots behind |
| Center floor focal | x=635–890, y=545–730 | Large blue/gold compass rose embedded/aligned in floor, unobstructed by furniture |
| Front perimeter | x=90–1460, y=640–950 | Low broken stone parapet, flower planters, ivy, sandstone/cliff depth, corner posts and coastal rock/sea foam below |
| Front central stairs | x=655–875, y=755–1024 | Straight central stair opening, stone posts on both sides, steps descending toward image bottom |
| Light/shadow | all zones | Warm daylight from upper-left plus practical lantern/candle glow and grounded cast/contact shadows, not flat pasted sprites |

Two small characters appear near x=710–830, y=440–540 in the reference. **Do not bake them into the room or generate new character images in Map Factory.** Characters, if used for a final gameplay screenshot, must be loaded as a separate optional scene layer from already-approved Game Factory assets; also capture an environment-only view.

## Architectural and asset rules

- Build every room piece from independent, properly registered, owner-approved environment images. Use `map_factory/metadata/environment_assets_v2.json` and actual source texture paths, measured dimensions and anchors.
- Existing **128 PNGs / 104 logical IDs** are a library, **not** proof all visible target props are represented. Audit missing elements instead of inventing substitutes or hallucinating art approvals. New image production requests go to Codex image_gen only, never Aider.
- Respect five passes: background → ground → walls/architecture → furniture/decor → shadows/overlays; preserve world Y-sorting and directional variants. No 90° transforms of perspective-specific sprites unless marked rotation-safe.
- Preserve v0012 and v0013 snapshots. Any correction after v0013 must create a separately versioned map patch; never overwrite a historic version.
- Target a composition close to the reference, not impossible pixel-identical reproduction from different source sprites. Report visible mismatches truthfully.

## Evidence required before visual approval

1. Actual Godot Import plus registered map, index and test-router tests, with **nonzero discovered test count**.
2. Real 1536×1024 Godot render generated with Map Factory, plus `resolved_assets`/render manifest and count of distinct texture paths and placed instances.
3. Separate reference-versus-render side-by-side and a region-based gap report: architecture, bed, study area, compass, sea, stairs, vegetation, lighting, shadows and optional character overlay.
4. Explicit `visual_approval: false` until the owner reviews the result. A deterministic render hash alone does not prove similarity.

## TASK-0102 review: v0014 real Godot render vs target (Claude, 2026-11-09)

Render: `docs/previews/map_factory_renders/hero_room_01_v0014.png` (1536x1024, real Godot gl_compatibility capture, environment only).
Side by side (target left, render right): `docs/previews/map_factory_renders/hero_room_01_v0014_vs_target.png`.
`visual_approval: false`. This is a gap review, not an approval.

Evidence gate finding: `tools/hero_room_capture_evidence.py` cannot pass on v0014. Its allowlist holds only the 128 `assets_generated` textures, but the room now uses HD runtime textures, `map_factory/parts` ocean/shadow/glow sprites and in-memory textures (empty resource path). So no `resolved_assets` manifest exists yet. A decision is needed: extend the allowlist through `assets_hd/hd_map.json` and the registered parts, or keep the gate strict. Also fixed: the canvas check compared a float array with an int array and always failed.

| Zone | Status | Gap and next step |
|---|---|---|
| Ocean and sky | partial | Flat tiled water with hard horizon, no coastal arches, few sea stacks. Needs a perspective-correct sea with distant rocks and arches (art request). |
| Rear arch | partial | Arch, ivy and flowers match well; it is a single piece over open water, with no connected walls on both sides. |
| Left architecture | missing | Only a bookshelf and a thin side column strip. Target has a connected broken limestone wall with banners and lanterns. |
| Right architecture | partial | Door piece and a bookshelf are present; no connected wall, no upper shelf details. |
| Main floor | partial | Warm tile grid matches in colour. Perimeter is a clean rectangle; target has an irregular terrace edge and cliff depth. |
| Bed zone | partial | Bed, blanket, rug present. Bed is smaller and rear-facing parts (shelf, shells, flowers) are missing. |
| Work and dining zone | partial | Table and rug present, but table is viewed from the wrong angle and misses chairs, jug, map, fruit at target scale. |
| Compass | matched | Present and centred. Size and colour close. |
| Front perimeter | partial | Low wall pieces present; planters, vines, posts and cliff rock below are mostly missing. |
| Stairs | partial | Straight central stair with side posts present; target steps are narrower and descend into a rock cliff. |
| Vegetation | missing | Almost no flowers, palms or ivy outside the arch. |
| Light and shadow | partial | Diagonal light bands exist; no lantern glow pools or grounded cast shadows at target strength. |

Next steps: (1) decide the evidence-gate allowlist question; (2) specific ART requests for the connected wall set, cliff terrace edge, sea stacks/arches and large planters (Codex image_gen); (3) a v0015 relayout once those exist. No character was inserted.
