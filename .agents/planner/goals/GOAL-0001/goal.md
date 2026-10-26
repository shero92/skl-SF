# GOAL-0001 — Hero Room from reference + production-quality Map Factory

## Owner's goal (original words)
> My first goal is to build a room like this reference image and upgrade the map factory to build maps and rooms for the game in the same quality and details, using the blocks I produce. It must be in 4 or 5 levels: background alive, ground blocks, then walls, then stuff like bed etc. on the blocks and stuff on walls, and then shadows etc.

Reference image: `references/hero_room_reference.png`. The original scene image supplied in chat is **1448×1086**, SHA-256 `42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7`. The separately committed reference has a different Git blob SHA-1 and file size; its native dimensions/hash and pixel equivalence still require explicit local verification. **1536×1024 is the target Map Factory output canvas, not the verified source-image size.** See `docs/REFERENCE_ART_DIRECTION.md` and `.agents/graphics/requests/GOAL-0001_request_coverage.json`.
Agents: do NOT open the reference during routine runs. Use the written spec below. Only the explicit final QA step may compare the Godot render with the reference.

## Written spec of the reference (derived once, so agents never need to view the image)
- **View:** top-down 3/4 JRPG perspective (Shining Force style), not true isometric. Pixel art, warm daylight.
- **Layout:** a ruined open-air stone room on top of a rocky sea cliff. Rectangular sandstone floor in the center; walls on left, back and right; open front edge with a low balustrade wall and a central stone staircase going down, flanked by two short posts with stone spheres.
- **Back wall:** central stone arch on two columns (open to the sea), covered in ivy and white flowers. Left back wall with two lanterns and a wall shelf. Right back corner: a closed arched wooden door with a compass emblem, flanked by lanterns.
- **Left zone (sleeping):** wooden double bed with a blue/gold compass-pattern blanket, two nightstands (one with a seashell), bookshelf/headboard shelf with books, plants and flowers, blue rug under the bed, tall blue-gold banners on the wall.
- **Right zone (study/dining):** wooden table with jug, fruit bowl, lantern and map/scroll, two stools/bench, bookshelf with books and candles, a brass globe, large plant in a blue-white vase, blue rug.
- **Floor center:** large blue-gold compass-rose floor emblem.
- **Decor everywhere:** blue-white ceramic vases, wooden chests, seashells, ivy/vines over walls, flowers (white, blue), palm plants on the cliff edge.
- **Characters in the reference (hero + creature) are OUT OF SCOPE.** Do not build or edit characters.

## Five render levels (matches map_factory/LAYER_SCHEMA.md)
| Level | Content | Must be |
| --- | --- | --- |
| 0 background (alive) | sky, drifting clouds, animated sea with waves/foam, distant sea stacks and rock arch, the cliff base under the room | animated, not a static picture |
| 1 ground | sandstone floor tile blocks, compass emblem, rugs as decals, stairs/cliff top surface | built from reusable blocks |
| 2 walls | wall blocks, broken wall tops, columns, arch, door, balustrade, stair sides, posts | 4-direction blocks where orientation matters |
| 3 objects | floor objects (bed, tables, shelves, vases, chests, plants) and wall-mounted objects (lanterns, banners, ivy, wall shelf) using mount_on | placed on blocks, correct sorting/occlusion |
| 4 shadows | per-object shadows, wall shadows, light shafts, lantern glow | drawn under the object casting them |

## Outcome (done when)
1. Map Factory builds this room in Godot from my own art blocks only (no generated/painted art, no single screenshot).
2. Same factory can build other rooms/maps by data (JSON), with the same five levels, 4-direction blocks, mounting, sorting and shadows.
3. A real Godot render of the room is produced by the project's factory and compared with the reference in the final QA step; I give the final visual approval.
4. Any missing art is requested from me via .agents/graphics/requests/ with full specs and a GitHub Issue; agents continue after I deliver.

## Constraints
- Agents never generate, repaint or upscale art. Missing blocks -> ART request.
- Identify existing assets only via asset_index.json, file names and metadata; never by opening PNGs.
- No character, gameplay or UI changes.
