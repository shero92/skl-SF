# Godot scenes and gameplay entry points

| File | Responsibility |
| --- | --- |
| `map_factory_preview.tscn` + `map_factory_preview.gd` | Environment-only map preview, map registry selection and camera; safe for current map work |
| `main.tscn` + `main.gd` | Game startup and runtime composition |
| `ocean_background.gd` | Ocean motion and environment display |
| `room_light_fx.gd` | Room lighting effects |
| `player.gd`, `room_companion.gd`, `room_npc.gd` | Gameplay actors — DO NOT EDIT during map-only work |
| `dialogue_ui.gd` | Dialogue/UI — DO NOT EDIT during map-only work |

Test environment preview with `godot --headless --path . --editor --quit` and `scenes/map_factory_preview.tscn` as specified in factory docs. [Full direct listing](FILES.md).
