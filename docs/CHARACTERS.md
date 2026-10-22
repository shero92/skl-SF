# Character artwork and animation specification

All characters and portraits are **individual transparent PNG files** indexed in `map_factory/metadata/asset_index.json`.

## Available first-pass character sprites

| IDs | Subject | Orientation / Action | Frames |
|---|---|---|---|
| CH001-CH004 | Hero | Idle down / up / left / right | 2 each |
| CH005-CH008 | Hero | Walk down / up / left / right | 4 each |
| CH009 | Companion | Idle | 2 |
| CH010 | Companion | Walk | 4 |
| CH011 | Green fairy / Forest Guardian | Idle | 2 |
| CH012 | Green fairy / Forest Guardian | Walk | 4 |
| UI007 | Hero portrait | Static | 1 |
| UI008 | Fairy portrait | Static | 1 |

Each character sheet is 144 pixels high? **No**: each frame is **144×192**, horizontally arranged. Two-frame sheets are **288×192**; four-frame sheets are **576×192**. UI portraits are **272×320**.

Metadata keys:
- `animation_frames` = number of columns.
- `frame_size` = [144,192].
- `fps` = timing for Godot Sprite2D.
- `origin` = [72,188], the near-bottom-center anchor **within one frame**, never the whole strip.
- `pixel_size` = full sheet dimensions.
- `shadow` = separate shadow PNG ID from the reusable shadow factory.

The low native pixel-art canvas is rendered at **2× nearest-neighbor**, without blurry scaling. That makes files large enough for Godot while preserving individual pixel clusters, but is **not proof of high visual quality**.

## Gameplay integration
- `scenes/player.gd` chooses CH001–CH008 depending on movement and facing.
- `scenes/room_companion.gd` follows the hero and switches CH009/CH010.
- `scenes/room_npc.gd` animates CH011.
- `scenes/dialogue_ui.gd` shows UI007/UI008 with the speaker's dialogue.

## Required artist approval before production
Compare the sprite silhouettes with the visual reference, including brown tousled hair, maritime blue/gold armor, facial detail, costume layering and warm lighting. Review frame alignment, no motion jitter, matching palette across all directions, consistent on-ground footprint and clean transparency.

**Upgrade rule:** Replace a PNG with the same catalog ID using a visibly more detailed, clean original sheet **with the same ordered frame contract**. If frame dimensions/counts change, update metadata and rerun Godot tests. Do not mark as ready until reviewed in motion.
