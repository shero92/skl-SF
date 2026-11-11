---
id: TASK-0147
status: review
owner: claude
agent: claude
priority: high
branch: claude/tactical-battle
depends_on: TASK-0121
issue: none
art_request: ART-0041
touches: scenes/battle/tactical_battle.gd,scenes/battle/tactical_battle_scene.gd,scenes/battle/tactical_battle.tscn,scenes/main.gd,tools/verify_tactical_battle.gd,tools/tests/test_tactical_battle.py,tools/test_map.json,docs/RUNTIME_INTEGRATION.md
test: python tools/run_tests.py --changed
done_when: From the room, B opens a grid skirmish the player can finish (move, attack, wait against EnemyAI), Esc returns to the room, and a headless test plays a full deterministic battle.
estimate_minutes: 90
---
# Playable skirmish

`scenes/battle/tactical_battle.gd` is a node-free session over TurnManager/EnemyAI: three party members against three raiders on a 10x7 field with rocks. The hero uses the weapon saved from the room (HeroSave). `tactical_battle_scene.gd` draws the field with plain shapes (art requested in ART-0041) and handles clicks: blue cell moves, red-marked enemy attacks, Space waits, R restarts after the end, Esc returns to the room. In `main.tscn` the B key opens it.

## Evidence / handoff
- `tools/verify_tactical_battle.gd` (registry id `tactical_battle`): rules, a full battle to a winner, same-seed replay, scene click mapping.
- The scene was opened in a real window for two seconds without script errors; nobody has played it by hand yet.
- Not included: attack animations (BattleDirector is not wired in), rewards, healing/magic actions, battle art.
