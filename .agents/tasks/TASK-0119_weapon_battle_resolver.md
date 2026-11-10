---
id: TASK-0119
status: review
owner: claude
agent: claude
priority: medium
branch: claude/weapon-battle-wiring
depends_on: TASK-0118
issue: none
art_request: none
touches: scenes/battle/battle_resolver.gd,tools/verify_weapon_battle.gd,tools/tests/test_weapon_battle.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: Weapon attacks resolve in battle (range, hit, crit, damage, defeat, status) and land on the animation controller hit signal, verified headlessly.
estimate_minutes: 60
---
# Wire the weapon system into battle

`BattleResolver` (scenes/battle/battle_resolver.gd) applies WeaponSystem rules: can_target, resolve (seeded RNG, damage to unit hp, defeat, poison on hit) and art_asset_id for ModularActorAdapter.equip. The animation controller and adapter are unchanged; connect `controller.hit` to `resolve`.

## Not done
No counter-attacks, no turn/order manager, no inventory/shop UI, no live scene (none exists yet).

## Evidence / handoff
- Tests: verify_weapon_battle.gd via test_weapon_battle.py (id weapon_battle).
- Next: a turn manager that moves units and calls can_target/resolve.
