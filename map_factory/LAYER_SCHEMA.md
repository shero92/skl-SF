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
