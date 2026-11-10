# Hero Room — what Codex must create to match the target (spec of 2026-11-10)

Audience: Codex (graphics producer, `image_gen`) and Claude Code (integration). Read this file, then only the ART requests it names.
Owner request 2026-11-10: "check the graphics Codex must create for the room and write exactly what is needed to get this picture."
This file is a plan and a checklist. It is **not** art, **not** an approval, and changes no map.

## 1. Reference (the picture to match)

| Item | Value |
| --- | --- |
| File | `map_factory/references/hero_room_01_target_20261110.webp` (+ `.reference.json`) |
| SHA-256 | `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323` |
| Size | 1125x750 (scale to the 1536x1024 map canvas: x 1.3653) |
| Identity | Re-encoded copy of the same design as `map_factory/references/hero_room_01_target_20261103.png` (mean abs diff 6.5/255). Treat both as ONE target. Do not "improve" the design. |
| Use | Style and composition reference only. Never paste, crop or trace it into an asset. It is not a background or screenshot. |

Current state to compare against: `docs/previews/map_factory_renders/t0128_v0021/hero_room_01_v0021.png` (hero_room_01 v0021, `visual_approval: false`) and the window check `docs/previews/runtime_checks/` if present.

## 2. Verdict in one paragraph

Most visible props **already exist as owner HD masters** (`assets_hd/**/CATALOG.md`) and many were added in v0018-v0021 (cliff base, coast, planters, palms, vines, connected walls). What still separates v0021 from the picture is: (a) a handful of **views that are wrong or missing** (the study table reads as a wooden roof, no armillary/candle shelf, no big potted plant, no stool, flat sea without light lattice, stairs/posts/rope fence only partly right), and (b) **placement work** with masters that already exist (large blue vases, conch shells, armillary, front banners). Only (a) needs new art; (b) is Claude's job and needs no Codex image.

## 3. Global rules for every new image (read once)

1. Follow `docs/GRAPHICS_PRODUCTION_POLICY.md`, `assets_hd/RULES.md`, `.agents/workflows/GRAPHICS.md`, `docs/OWNER_ART_APPROVAL_20261109.md`. One subject per file, one request per generation, transparent RGBA, **no baked shadow, no ground, no frame, no label, no multi-pose sheet, no crop from a sheet, no flip or rotation to invent another view** (every needed view is generated separately).
2. Style = the picture and the approved masters: high-detail pixel art look (hard pixel clusters, no blur), warm limestone/sandstone `#e8c48a`-family stone, cobalt blue `#2f5bb7`-family cloth with gold `#e0b04a` trim, warm oak/brown wood, deep green foliage with white and pale-blue flowers, brass lantern glow. **Light comes from the upper left**; keep one shared direction. Dark outline 1-2 px at 1x, same density as `assets_hd/furniture/*` and `assets_hd/props/*`.
3. Camera: three-quarter top-down "tactical RPG" view as in the picture (about 30 deg elevation; floor tiles are squares seen from above with slight foreshortening). Upright objects show their front and top faces as in the picture.
4. Size: build each master at **at least 4x its on-screen size on the 1536x1024 canvas** (the on-screen box is given per asset below). Keep ~3 percent transparent margin. Do not upscale small crops.
5. Output locations (same convention as ART-0032..0035): masters in `assets_hd/<category>/<group>/v001/<name>.png` (+ `.gdignore`), copy at the exact paths listed in the ART request under `.agents/graphics/deliveries/ART-####/`, review PNGs and a real Godot capture under `game_factory/environment/ART-####/v001/`, a `manifest.json` (`request_id`, every path, SHA-256, pixel_size, mode, alpha extrema, alpha-128 bounds, origin = bottom centre of visible pixels, source prompt text, tool, rejected attempts kept).
6. Keep rejected attempts (`rejected/`); never overwrite an approved or earlier file; new version = new `vNNN`.
7. Status of any produced work is `delivered`. Only the owner approves art (`reviewed`/`integrated` come after owner review and Claude integration).
8. Forbidden: characters (hero/companion are game sprites placed by code), UI, text, watermarks, paid/external image services, Aider.

## 4. Gap matrix (zone by zone; target boxes are approximate canvas px in 1536x1024, measure the committed reference for exact values)

Legend: **P** = placed in v0021 · **M** = master exists in `assets_hd` (placement work only) · **R** = existing ART request (id, status) · **N** = new request in this PR.

### 4.1 Sky, sea, distant coast (y 0-360, plus the sea around the island)
| Target element | v0021 | Needed |
| --- | --- | --- |
| Sky gradient with warm white clouds | P (flat clouds) | R: ART-0002 clouds (blocked_reference; unblocked by the reference above). Priority low. |
| Many tall sea stacks and two big rock arches | P (ART-0034 delivered, placed: 2 arches, 5 stacks) | M/P. Add more stacks of the delivered set (placement only). |
| **Water with a lattice of fine white glints/foam lines** (visible all over the sea, x 0-1536) | missing (flat azure tile) | **N: ART-0037** sea light-lattice overlay (tileable). |
| Foam where waves hit rocks | P (ART-0033/0034 foam) | R: ART-0003 loop (animated, low priority). |

### 4.2 Rear arch and columns (x 555-990, y 0-400)
| Element | v0021 | Needed |
| --- | --- | --- |
| Arch with ivy and white/orange flowers | P | none |
| Two tall **blue-white ceramic urns** beside the arch bases (x 519-560 and 1031-1079, y 328-410) | missing | M: `assets_hd/props/vase_blue` x4 (placement). |
| Blue/gold banner hanging at the right column | P partly | M: `assets_hd/decor/banner_blue_long` (placement). |
| Sun shafts through the arch onto the floor | P (painted) | R: ART-0013 (low; runtime already paints light shafts). |

### 4.3 Left wall and bed zone (x 100-640, y 130-700)
| Element | v0021 | Needed |
| --- | --- | --- |
| Connected ruined wall, parapet, ivy | P (ART-0004/0032 pieces) | none; unused ART-0032 corner/parapet pieces = placement. |
| **Small window opening in the rear-left wall** showing sea (x 240-285, y 165-215) with a potted flower | missing | **N: ART-0038** wall piece with window opening. |
| Bed with blue/gold blanket, white pillows | P (HD bed) | R: ART-0001 four views, ART-0007 blanket (low: current bed is acceptable). |
| **Headboard shelf**: books, flower pots, shell above the bed (x 245-385, y 215-300) | missing | R: ART-0008 headboard shelf (blocked_reference; now unblocked). |
| Bedside table with **pink conch shell** and flower | P (table) | M: `assets_hd/props/shell_conch` (placement). |
| Gold-blue banners on the wall faces and outer front wall (x 109-177, y 440-792) | P partly | M + R: ART-0023 side banner/lantern views (requested). |
| Brass hanging lanterns (several, lit) | P | M: `assets_hd/lighting/wall_lantern` x3. |
| Rug under the bed | P | none |

### 4.4 Right wall and study zone (x 965-1510, y 100-710)
| Element | v0021 | Needed |
| --- | --- | --- |
| Arched wooden door with compass emblem in the stone wall | P (ruined_door) | R: ART-0005 closed compass door (blocked_reference; medium). |
| **Right bookshelf**: low open shelf with books, candle trio, **armillary sphere on top**, stacked crates beside it (x 1085-1297, y 293-437) | partly (plain bookcase, no sphere, no candles) | R: ART-0020 four-view bookshelf (blocked_reference) + M: `props/armillary_sphere`, `lighting/candle_cluster`, `furniture/crate`, `furniture/bookcase_armillary`. |
| **Large potted plant with white flowers in a blue-white vase** (x 1270-1400, y 348-498) | missing | R: ART-0011 (blocked_reference; the unverified stack idea in that request is replaced by an independent image). **High priority.** |
| **Study table seen correctly**: wooden table, blue/gold runner, open map, scrolls, white jug, fruit bowl, lit brass lantern; **two benches and one stool** (x 1017-1311, y 450-655) | wrong (table top reads as a roof) | R: ART-0019 four-view study table (blocked_reference). **N: ART-0039** wooden stool. **Highest priority.** |
| Blue/gold rug under the table | P | R: ART-0015 second rug (low). |
| Closed wooden chest on the floor near the stairs (x 1190-1265, y 690-760) | P (crate) | R: ART-0021 chest views (low). |

### 4.5 Centre floor (x 190-1390, y 315-800)
| Element | v0021 | Needed |
| --- | --- | --- |
| Compass rose diamond inlay (x 635-887, y 539-724), blue with gold star | P | R: ART-0022 oblique inlay (requested) |
| Sandstone paving with irregular slab pattern and warm sun stripes | P (tile grid + light shafts) | R: ART-0014 integrated; no new art. Floor repetition is a known gap (tiles G01-G12). |
| Irregular broken terrace edge | P (ART-0014/0033) | none |

### 4.6 Front perimeter, stairs and cliff (y 640-1024)
| Element | v0021 | Needed |
| --- | --- | --- |
| Low broken parapet with planters, flowers, ivy | P (ART-0035) | none; more planters = placement. |
| Two **stone posts topped with a sphere** at the stairs (x 600-690 and 790-874, y 770-900) | P (plain pillars) | R: ART-0006 sphere finial (blocked_reference). |
| **Straight stair with side walls**, steps descending to the bottom edge (x 600-874, y 778-1024) | partly (flat stone block) | R: ART-0025 entrance stairs (requested). **High priority.** |
| **Wooden rope-and-post fence** on both terrace edges (x 200-295, y 610-740 and 1210-1300, y 620-745) | missing | R: ART-0024 (requested). |
| Palms and flower mounds at the corners | P (ART-0035) | none |
| Pink shell and small blue vase near the front-right planter | missing | M: `props/shell_conch`, `props/vase_blue` (placement). |
| Cliff face with ivy, rubble, foam | P (ART-0033) | none |

### 4.6b Not art
Two characters (hero + companion) stand at the centre (canvas about x 735 and 795, y 490). They are game sprites placed by code. Do not draw them into any room asset.

## 5. Production order for Codex (batches; one request = one generation)

| Batch | Requests | Why first |
| --- | --- | --- |
| B1 (largest visual gain) | ART-0019 study table, **ART-0039** stool, ART-0011 potted plant, ART-0025 stairs | These four are visibly wrong or missing in v0021. |
| B2 | ART-0020 bookshelf, ART-0008 headboard shelf, ART-0006 sphere finial, ART-0024 rope posts, ART-0022 compass inlay | Fill the study and bed walls and the front edge. |
| B3 | **ART-0037** sea lattice, ART-0023 side banners/lanterns, ART-0005 door, **ART-0038** window wall piece | Atmosphere and wall detail. |
| B4 (optional) | ART-0001 bed views, ART-0007 blanket, ART-0015 rug, ART-0021 chest, ART-0002 clouds, ART-0003 foam loop, ART-0013 sun shafts, ART-0016..0018 shadow masks | Polish; runtime already approximates several of them. |

Requests listed as `blocked_reference` need only a reference gate, now satisfied by the committed target (section 1); the owner or Claude flips them to `requested` after reading their own text. Where a request proposes a stacked composite, deliver the independent image instead.

## 6. Per-asset production spec (new and unblocked high-priority pieces)

Common fields: RGBA PNG, transparent background, no shadow, origin = bottom centre of visible pixels, light from upper left, master >= 4x on-screen size. `on-screen` = size on the 1536x1024 canvas.

| Asset (request) | View | On-screen box | Master min | Must contain | Must not contain |
| --- | --- | --- | --- | --- | --- |
| Study table (ART-0019) | 4 files: south (front, used), north, east, west, each independently drawn | about 150x110 per piece with its runner; table top plane clearly seen from above, two front legs visible, apron with plain board | 1450x1080 | dark-oak table, **blue runner with gold border and compass motif**, tabletop clear (props are separate files), thick top edge, 4 turned legs | roof-like overhang, rug underneath, props baked on, bench |
| Stool (ART-0039) | south, three-quarter | 36x40 | 500x560 | small round-seat wooden stool, 3 visible legs, same oak as benches | cushion, shadow, floor |
| Large potted plant (ART-0011) | south | 130x150 | 1100x1300 | blue-white glazed urn (gold rim band) with a big tropical plant and white plumeria flowers, soil hidden by leaves | stand, floor, shadow |
| Entrance stairs (ART-0025) | south (visible) | 274x246 (width x height, includes both side-wall caps) | 2200x1960 | 5-6 straight limestone steps descending toward the viewer, thick low side walls with ivy and broken tops, post sockets at the top for the sphere posts | water, cliff, floor tiles outside the stair |
| Sphere finial post (ART-0006) | south | 56x120 | 450x960 | square carved limestone pillar with a smooth stone sphere cap, ivy on the base | companion pieces |
| Rope post + rope rails (ART-0024) | post, west rail, east rail | post 40x90, rails 110x40 | 3 files | weathered wooden post with rope loop, sagging rope between two posts | ground, shadow |
| Bookshelf with armillary and candles (ART-0020) | south and north (needed now), east/west later | 212x144 | 1700x1150 | low wide open shelf, many blue/brown books, **brass armillary sphere on top**, **three lit candles** with soft flame, small crates stacked beside | wall, shadow, floor |
| Headboard shelf (ART-0008) | south | 140x85 | 1100x680 | small wooden shelf above the bed head with books, a flower pot with pink/white flowers, a pink conch | bed |
| Sea light lattice (**ART-0037**) | top-down overlay, tileable | one tile 512x512 on canvas | 2048x2048 (seamless, wraps in x and y) | **fine white and pale-cyan glint lines forming a loose square lattice** over transparent background, soft sparkle nodes, alpha 0-70 percent | land, rocks, solid fill, visible seam, text |
| Window wall piece (**ART-0038**) | south, one connected wall run | 320x190 (same footprint as `wall_straight_long_a`) | 1280x760 | same limestone, ivy and flowers as ART-0032 wall pieces, a rectangular **opening** (about 60x75 px on canvas) with a thin stone sill, transparent through the opening | glass, curtain, interior |

For every file also record in `manifest.json`: view/facing, intended anchor (bottom centre), footprint in 64 px cells, and which masters it visually matches.

## 7. Integration plan (Claude, after delivery, not Codex)
1. Register each delivery as parts (`tools/register_environment_art.py` pattern; owner approval recorded) with new IDs.
2. Publish hero_room_01 **v0022+** with `map_factory_cli.py apply` (never edit older versions): replace the study table and bookcase instances (keep instance IDs so lanterns/banners stay mounted), add vases, shells, armillary, finial posts, rope posts, plant, stool, headboard shelf, stairs, window wall piece, sea overlay.
3. Real Godot capture + side-by-side with the reference; `visual_approval` stays false until the owner reviews.
4. Run `python tools/run_tests.py --all`, `tools/graphics_validation.py --all`, navigation and depth-sorting checks (new colliders only where furniture really blocks).

## 8. Acceptance checklist (per delivery)
- [ ] PNG is RGBA, real transparency, no halo, no baked shadow, subject not clipped (alpha-128 bbox inside the canvas).
- [ ] Independent generation per file; no crop/flip/rotation of another file; rejected attempts kept.
- [ ] Style, palette, outline weight and light direction match `assets_hd` masters and the reference at the on-screen size (check in a real Godot capture, not only the sheet).
- [ ] Manifest complete with hashes; request status set to `delivered` only.
- [ ] Nothing in `assets/`, `assets_generated/`, `assets_hd/` masters, `map_factory/parts/` or earlier map versions was edited.
