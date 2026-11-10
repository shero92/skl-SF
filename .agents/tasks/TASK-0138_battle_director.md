---
id: TASK-0138
status: review
owner: claude
agent: claude
priority: medium
branch: claude/battle-director
depends_on: TASK-0121
issue: none
art_request: none
touches: scenes/battle/battle_director.gd,tools/verify_battle_director.gd,tools/tests/test_battle_director.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: TurnManager attack results (and counter-attacks) are played through the existing animation controller in order, with a hit event on the hit frame, an attack per weapon profile, and a safe skip when an actor is missing; verified headlessly.
estimate_minutes: 60
---
# Battle director: rules to animation

`BattleDirector` (scenes/battle/battle_director.gd): `attack(attacker_id, defender_id)` resolves through TurnManager immediately (data is final) and queues the attack plus a counter-attack; `advance(delta)` plays them one at a time through BattleAnimationController (unchanged). Weapon art profile picks the attack (sword/axe/natural slash, spear thrust, bow shoot, staff cast). Signals `playback_started`, `hit_landed` (fires on the controller hit frame so a UI can show damage then), `playback_finished`, `queue_empty`. A missing actor skips the animation, never the result or the hit event.

## Not done
The `draw`, `release`, `cast`, `cast_release` poses have no frames in the Game Factory manifest yet (Hero has only attack_windup/attack_execute), so real actors report MISSING_ANIMATION for them via the adapter; no live battle scene, camera or VFX wiring.

## Evidence / handoff
- Tests: verify_battle_director.gd via test_battle_director.py (id battle_director).
- Next: a playable battle scene that owns a Director, a TurnManager and ModularActorAdapter actors.
