---
id: ART-0040
status: delivered
owner: graphics-specialist
task: TASK-0102
dedupe_key: hero_room_wall_lantern_east_pointing
existing_asset_ids: L06
output_paths: .agents/graphics/deliveries/ART-0040/hero_wall_lantern_east.png
---
# East-pointing brass wall lantern for the west wall

**Why:** ART-0023 delivered only the west-pointing lantern (`hero_wall_lantern_west`, part L06), used on the east wall since hero_room_01 v0024. The west wall still shows the old flat L01/L02 lanterns, so the two side walls do not match.

**Source image and SHA-256:** `map_factory/references/hero_room_01_target_20261110.webp`, sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`. Style reference: `assets_hd/lighting/` master of `hero_wall_lantern_west` (same brass, glass and bracket; do not edit or mirror-paste it).

**Outputs:** one independent RGBA PNG at the path above.
- Lantern hanging from a bracket fixed to a wall on its **left**, arm pointing east (the true counterpart of the west view, drawn with light from the upper left, not a flipped copy).
- On-canvas size about 29x53 px (master at least 400x720). Lit warm glass, no glow halo, wall, shadow or text. Origin = the bracket's wall mount point documented in the manifest.

## Request checklist
- [x] Duplicate scan against asset IDs, active requests and previous deliveries.
- [x] Original reference path and hash attached.
- [x] Specifications reviewed; marked `requested`.

## Graphics specialist checklist
- [x] Clean PNG produced (ONLY graphics specialist); SHA-256 manifest written; mark `delivered`.

## QA checklist
- [ ] Independent visual review at Godot native scale on the west wall; mark `reviewed`.

## Integration checklist
- [ ] Registered asset and map tested; PR merged; mark `integrated`.

## Codex source-provenance supplement — 2026-11-11
Master generation and measured source annotations: game_factory/environment/ART-0040/v001/manifest.json, requests/, README.md and actual Godot capture. Complete additive delivery sidecar: .agents/graphics/deliveries/ART-0040/codex_source_manifest.json. The existing TASK-0163 packaging manifest and registered L07 stay unchanged. PR178 already uses the byte-identical master in room v0028; wall mount calibration remains provisional. Source mount [232,330] maps to [4.1734,15.6605] in the padded29x53 nearest QA; L07 is a different trimmed29x47 BOX derivative with a bottom-centre origin, so the QA pivot must not be copied directly without conversion.

Reference crop: original1536x1024 target map_factory/references/hero_room_01_target_20261103.png, SHA25647a7855cf242302108e1a6b9eaf4bfd3422f9f8c812585fa4da5bcaea948668b; box[208,326,265,411]. Crop reference only, never a production asset.
- .agents/graphics/requests/reference_crops/ART-0040_target.png; SHA256 bea0299e74ee64272b849a9cd7f357043d058f69357f571c03ddf1e3dba0ad42
- .agents/graphics/requests/reference_crops/ART-0040_compare.png; SHA256 a4c15238213e1d18d34b3004ec89d97f8f1d48de6e6847f3134135fcf8d43bde

Exact view: one brass hanging lantern, wall plate on LEFT, arm projects EAST/right, front and top planes visible from the room camera looking north/down; upper-left daylight, light inside glass. Provisional native29x53, master minimum400x720. No wall, banners, plants, floor, cast shadow, external glow, text, frame, characters or additional lanterns. Two independent image_gen calls; earlier attempt is nonselected, not owner-rejected. Actual alpha compositing disproved the apparent halo in the tool RGB preview. Owner automatic approval recorded.

Comparison provenance: ART-0040_compare.png uses docs/previews/map_factory_renders/t0149_v0027/hero_room_01_v0027.png as its historical game-side baseline (before PR178), not room v0028. Current integration evidence is the separate TASK-0163 / PR178 capture.
