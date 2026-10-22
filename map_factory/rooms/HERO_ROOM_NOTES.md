# Hero Room starter layout

The scene is a **modular draft**, not an exact copy of the original reference.

- Edit positions, IDs, layer lists, shadows, and collision in `hero_room.json`.
- `RoomFactory` renders an ocean-colored backdrop, reusable floor tiles and independently indexed sprites.
- Floor overlays support compass symbols and rugs without covering the player.
- Back objects render before player actors. Entities use y-sort and per-item physics footprints.
- Interaction locations are data, consumed by `scenes/main.gd`.
- The 152 atlas-cropped images require visual cleanup and quality approval. Mark as `needs_cleanup`, not `ready`.

To reuse the same furniture in another map, copy its ID into another room JSON. You do not need duplicate PNGs.
