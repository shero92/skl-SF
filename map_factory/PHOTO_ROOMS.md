# Photo rooms

A photo room is a Map Factory map whose picture is one painting. Everything the hero room does is switched on by one file,
`map_factory/photo_rooms/<map_id>.json`, so every later map gets the same behaviour by writing that file.

## What a photo room gives a map

| Feature | File key | What it does |
| --- | --- | --- |
| Camera | `camera` | `{"follow": false}` (the hero room): the whole room in a fixed view. For maps `{"follow": true, "zoom": 1.4, "talk_zoom": 1.8, "lead": 48, "smoothing": 5, "sway": 3, "focus_offset": [0, -56]}` (set in `painted_worlds/*/world.json` for the outdoor map): the view eases after the hero, leads in his walking direction, zooms in while he talks, stays inside the board; **V** shows the whole board and back (`scenes/follow_camera.gd`). Owner rule 2026-11-13: dynamic view in maps, full view in the room. |
| Cinematic feel | `camera.sway`, `camera.step_kick`, `cinematic.step_bounce`, `cinematic.vignette`, `cinematic.parallax`, `dust` | A slow breathing drift of the view; a small push of the view and a small hop of the hero on every step; a soft dark lens edge; the far sea sliding against the room as the camera moves (depth); drifting dust motes in the sunlight (`[x, y, w, h]` area). |
| Painting as the room | `image` | Shown unchanged; the tile pieces of the map are hidden. F3 switches between painting and pieces. |
| One square per step | `hero_step`, `hero_step_offset` | Shining Force movement: each key press moves the hero exactly one square, four directions, no diagonals. |
| Walk squares | `navigation.regions` | 32 px squares (`[x, y, w, h]` in squares) the hero may stand on. |
| High-resolution hero | `hero_height` | Drawn from the 1254 px source frames with a dark rim and a long soft shadow. |
| Hero alone | `hero_only` | Hides NPCs and the companion of the map. |
| Walk behind things | `depth_objects` | Each object is cut from the painting by its outline and drawn over the hero while his feet are above its `base_y`, under him once he is in front. Bed, table, columns, posts and parapet walls all work the same way. |
| Height shadows | `depth_objects[].shadow` | A soft shadow to the lower right, as long as the object is high: `[x1, x2, y, height]` (base line) or `[x1, y1, x2, y2, height]` (vertical edge). |
| Moving sea | `sea` | Polygons over water: rippling swells, sun glints, painted foam that pulses with the swell. |
| Fog and shadows of clouds | `mist` | A drifting haze over the whole picture. |
| Clouds from the painted sky | `clouds` | Cut from the painting's own sky; drift behind arches and rocks. |
| Petals, lantern glow | `petals`, `lanterns` | Drifting petals; flickering warm glow at lantern points `[x, y, size]`. |
| Cover patches | `patches` | A piece of the painting copied over another (hides painted characters until a clean painting exists). |
| Moved talk spots | `moves` | Relocates NPCs and talk spots that sit on painted furniture; a third number widens the reach. |

## Making a new photo room

```bash
python tools/photo_room_tool.py new --map-id sunset_hall --image map_factory/references/sunset_hall.png
python tools/photo_room_tool.py preview --map-id sunset_hall
python tools/photo_room_tool.py check --map-id sunset_hall
```

1. `new` registers the map (indoor preset) when needed and writes a starting file with sensible defaults.
2. Fill `navigation.regions` by looking at `preview` (walk squares are green, depth objects red with a blue base line, shadows purple, the hero's step squares white dots).
3. Cut every tall thing the hero should pass behind into `depth_objects` (measure the outline on the painting; put `base_y` at the object's foot).
4. Play it: set `Main.next_map_id = "sunset_hall"` (static variable of `scenes/main.gd`) before the main scene starts.
5. Walk the hero to every square beside each object and look: `tools/verify_main_equipment.gd` is the model for a headless check.

## Rules

- The painting file is never edited by the game or the tool. Art that is missing (clean painting, real waves, flying creatures) is requested under `.agents/graphics/requests/`, not drawn in code.
- Gameplay (NPCs, talk spots, spawn) comes from `map_factory/rooms/<map_id>.json`; without that file the room has only the hero and the `spawn` of the photo file.
- The hero's high-resolution frames are local files: on a machine without them the 96 px factory frames show.
- Tools: `tools/photo_room_tool.py`; runtime: `scenes/main.gd`, `scenes/photo_room_life.gd`, `scenes/hero_source_art.gd`, `scenes/player.gd`; test: `tools/tests/test_photo_room_tool.py` and `tools/verify_main_equipment.gd`.
