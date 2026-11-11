---
id: TASK-0167
status: review
owner: claude
agent: claude
priority: high
branch: claude/battle-maps
depends_on: TASK-0166
issue: none
art_request: none
touches: .agents/tasks/TASK-0167_battle_maps_from_editor.md,scenes/map_factory_editor.gd,scenes/battle/tactical_battle.gd,scenes/battle/tactical_battle_scene.gd,tools/verify_room_editor.gd,tools/verify_tactical_battle.gd,tools/capture_game_window.gd,game_factory/battles/hero_room_01.json,docs/previews/map_factory_renders/t0167_battle_maps/battle_on_hero_room.png
test: python tools/run_tests.py --changed
done_when: In the editor the owner can mark blocked squares and the start squares of both teams on any map, save that as a battle and play it at once; the skirmish runs over the Map Factory map on the map's own squares, and a headless test builds a battle in the editor and fights it to the end.
estimate_minutes: 180
---
# Battle maps built in the editor

Owner (2026-11-11): "so I can build complete maps and fight maps by myself".

- Editor, "Battle setup on this map": Block (toggle a blocked square), Player and Enemy (put a start square; units come in a fixed order, up to 8 per team), Clear, Save battle, Play battle. Squares without floor are always blocked.
- Battle file: `game_factory/battles/<map_id>.json` (grid = the map's own squares, blocked squares, units). One battle per map.
- `tactical_battle.gd`: `Session.new(seed, hero, battle)` and `Session.definition_error(battle)`; an invalid battle falls back to the practice field.
- `tactical_battle_scene.gd`: plays a battle file over its map (translucent squares above every map level), fits the camera to the field, Tab cycles through saved battles. B in the room still opens the practice field.
- `game_factory/battles/hero_room_01.json`: an example battle in the hero room (bed and table squares blocked).

## Evidence / handoff
- `tools/verify_room_editor.gd`: builds a battle with the editor tools, saves and reloads it, loads it in the skirmish scene, checks the squares line up with the map and fights it to the end.
- `tools/verify_tactical_battle.gd`: valid and broken battle definitions.
- Real window capture: docs/previews/map_factory_renders/t0167_battle_maps/battle_on_hero_room.png. Nobody has set up or played a battle by hand yet.
- Not done: choosing which character and weapon stands on a start square (fixed order for now), several battles per map, victory conditions other than defeating the other team, unit sprites (still circles), furniture blocking squares automatically.
