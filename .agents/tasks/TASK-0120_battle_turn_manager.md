---
id: TASK-0120
status: review
owner: claude
agent: claude
priority: medium
branch: claude/battle-turn-manager
depends_on: TASK-0119
issue: none
art_request: none
touches: scenes/battle/turn_manager.gd,tools/verify_turn_manager.gd,tools/tests/test_turn_manager.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: A data-only grid turn manager handles agility initiative, BFS movement, ranged/melee targeting, attack with counter-attack and victory, verified headlessly.
estimate_minutes: 60
---
# Grid turn manager on top of the weapon resolver

`TurnManager` (scenes/battle/turn_manager.gd): add combatants, start_round (agility order), reachable/move_to (one move per turn, enemies block, allies pass), targets/attack (counter-attack when the defender can reach back), end_turn, battle_ended signal. Uses BattleResolver, so weapon range and stats apply.

## Not done
Enemy AI, terrain costs, inventory/shop UI, live battle scene, wiring `attacked` to the animation controller.

## Evidence / handoff
- Tests: verify_turn_manager.gd via test_turn_manager.py (id turn_manager).
- Next: simple enemy AI (move toward nearest target, attack) using reachable/targets.
