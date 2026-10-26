# Blender part factory (TASK-0046)

Owner decision 2026-10-26: every missing environment piece is **built in Blender**, the room is assembled in Godot from those pieces, and only the **final Godot capture** is compared with the reference. Defects are fixed by improving the pieces (spec, builder, material, projection) and re-rendering, not by AI image generation or hand-edited pixels. The nine accepted HD sprites (W021, W022, A017, A018, D019, P023-P026) stay as they are.

## Commands (owner's Windows host; Blender 5.2 LTS)
```text
py -3 tools/blender_factory.py calibrate          # a 1x1 floor tile must render exactly 64x64
py -3 tools/blender_factory.py deliver ART-0004   # spec -> .agents/graphics/deliveries/ART-0004/ + manifest.json
py -3 tools/blender_factory.py render tools/blender/specs/ART-0014.json --out <dir>
```
Blender is found through `--blender`, `BLENDER_EXECUTABLE` or `blender_executable` in `.agents/planner/config.json`.

## Files
| File | Runs in | Role |
| --- | --- | --- |
| `projection.json` | config | 64 px per tile, supersample, camera elevation, sun (upper left), engine and samples |
| `lib.py` | Blender | scene, orthographic camera with square-floor pixel aspect, sun, materials, framing, colour + separate shadow pass |
| `builders.py` | Blender | parametric pieces; each returns objects and ground anchors |
| `render_part.py` | Blender | renders every output (facing) of one spec |
| `specs/ART-*.json` | data | one spec per ART request; output names equal the request's `output_paths` |
| `../blender_factory.py` | Python | finds Blender, renders, native + 4x master + shadow PNGs, technical QA, manifest |
| `../art_qa.py` | Python | technical PNG QA (transparency, backing, halo, clipping, mirrored/rotated copies) |

## Conventions
- 1 Blender unit = 1 map tile. +X east, +Y north (into the screen), +Z up. Builders model the front facing south (toward the camera); a facing rotates the 3D model, so every facing is a real render, never a mirrored bitmap.
- The camera is orthographic, looks north and is tilted down by `camera_elevation_deg`; pixel aspect keeps the floor grid square, so heights appear scaled by cot(elevation). **Calibrate the elevation against the final Godot capture.**
- In a pure north-looking orthographic view the inner faces of east/west side walls are edge-on (only their top and end are visible). If side walls must show masonry, that is a projection decision for the owner (see TASK-0046).
- Deliveries are `rendered_unreviewed`: `deliver` never changes ART/TASK status, never writes `map_factory/parts/` and never approves art.
