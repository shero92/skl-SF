---
id: TASK-0121
status: review
owner: claude
agent: claude
priority: medium
branch: claude/enemy-ai
depends_on: TASK-0120
issue: none
art_request: none
touches: scenes/battle/enemy_ai.gd,tools/verify_enemy_ai.gd,tools/tests/test_enemy_ai.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: A deterministic enemy AI picks the best attack from any reachable cell (likely kills first, avoids counters) or approaches to its weapon's ideal range, and an AI-vs-AI battle ends, verified headlessly.
estimate_minutes: 60
---
# Enemy AI for the turn manager

`EnemyAI` (scenes/battle/enemy_ai.gd): plan() is read-only and returns {move_to, target_id}; act() plays the whole turn (move, attack, end_turn). Scores expected damage x hit chance, big bonus for likely kills, small penalty for being countered; with no target it steps toward the nearest enemy, stopping at its weapon's max range (archers keep distance).

## Not done
Terrain costs, healing/magic AI, group tactics, animation wiring, live scene.

## Evidence / handoff
- Tests: verify_enemy_ai.gd via test_enemy_ai.py (id enemy_ai).
- Next: connect TurnManager.attacked to the animation controller and ModularActorAdapter in a playable battle scene.
