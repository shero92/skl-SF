# Five-level Room Factory composition rules

A room is assembled from five distinct blocks passes and never displayed as one static screenshot. No characters or gameplay scripts are edited.

| Data pass | Content | Godot draw z |
| --- | --- | ---: |
| 0 background | sky, sea, cliffs, islands | 0 |
| 1 ground | stone tile grid, carpet decals | 10 |
| 2 walls | walls, arches, pillars, stairs | 30 |
| 3 decorations | flowers, wall banners, lanterns, furniture | 40 |
| 4 shadows | independent owner-linked shadow PNG textures | 20 |

Shadows are generated last but draw between ground and walls: this keeps the shadow **under** the object casting it, rather than darkening the furniture itself.

The compiler saves each version's five-pass graph under map_factory/maps/MAP_ID/layers/latest.json and layers/v000N.json. Each placement records instance_id, shared asset ID, texture_path, dimensions, origin, position, scale, rotation, category, collision, shadow, and attachment metadata.

Wall-mounted detail example: set mount_on to a placed wall instance ID and mount_offset to [dx,dy]. The world position is recomputed from the wall location. This allows the wall and its ivy/lantern/banner to move together. Broken/cyclic mounts are rejected.

Never guess 100 percent artistic quality from available PNGs; validate image files, metadata, pixel fidelity, occlusion and a real Godot render before approval. See MAP_FACTORY_RULES.md. Unknown sprite shapes require individual PNG reconstruction and human review.

## Painted shadow level and light level (TASK-0109, TASK-0110)

Shadows are a **separate level**, not only static shadow strips. `ShadowPainter.build_layer(room, light)` (map_factory/scripts/shadow_painter.gd) creates `Level4_PaintedShadows` (z 20, below walls and decor, so it never darkens the object that casts it). For every ground-standing Sprite2D it paints the shadow from the sprite's real alpha silhouette: the silhouette is projected along the light direction onto the ground plane, fades with height, is softened, and gets a contact occlusion ellipse under the footprint. Flat or wall-hung pieces (rugs, emblems, banners, lanterns, glow, mounted decor) are skipped. Each shadow records `owner_ref`, follows its owner via `ShadowPainter.sync(room)` and is removed with it. `ShadowPainter.set_shadows_visible(room, false)` hides the level. Nothing is generated as art; it is deterministic runtime painting.

Light parameters (all optional, defaults in `default_light()`): `direction` [x,y] (shadow falls toward it), `length`, `opacity`, `height_fade`, `blur`, `color` [r,g,b], `contact_opacity`, `contact_height`. Maps opt in with `"shadow_mode": "painted"` and an optional `"lighting"` object with those keys.

`ShadowPainter.build_light_layer(room)` creates `Level5_Light` (z 60): a soft additive warm pool around each lantern or candle, toggled with `set_light_visible`.

## Scale and rotation rules (TASK-0115)

Every placed block has `scale` (limits in map_factory/metadata/transform_rules.json, default 0.1 to 4.0) and optional `rotation_degrees`. Free rotation (any angle that is not a quarter turn) is only valid for pieces listed in `rotation_safe` or flat pieces (floors, rugs, decals); the CLI rejects it for upright perspective pieces, which must use their four facing variants. A block with `"free_transform": true` is exempt: it may take any angle, and a grid-placed part with the flag may also be resized and drawn away from its cell anchor while its `grid_placement` cells keep reserving the walking grid (design is free, movement stays on squares). `tools/room_design.py` (`Design.place/transform/remove/write_patch`) writes such patches from code. `rotation_range_degrees` can limit the tilt per id (flower clusters tilt about 50 degrees in total, so they stay upright). `tools/map_variation.py` creates a seeded patch of scale and rotation changes; scale and rotation snap to `scale_snap` and `rotation_snap_degrees` so pixel density stays consistent. The map camera `zoom` (0.25 to 4.0) zooms the whole view.
