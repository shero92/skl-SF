---
id: TASK-0141
status: review
owner: claude
agent: claude
priority: medium
branch: claude/staff-magic
depends_on: TASK-0140
issue: none
art_request: none
touches: scenes/battle/weapon_system.gd,tools/verify_weapon_system.gd,tools/simulate_battles.gd,docs/WEAPON_BALANCE_REPORT_20261110.md
test: python tools/run_tests.py --changed
done_when: Weapon types of kind magic ignore target defense, the simulation uses each class's signature weapon type, tests pass.
estimate_minutes: 30
---
# Staff magic

`WeaponSystem.damage()` ignores the target's defense when the active weapon type has `kind: magic` (staffs). The simulation now equips each class's first listed weapon type, so mage and healer use staffs. Result (20 seeds, with TASK-0140): mage 19%, healer 38%, lancer 92%, warrior 80%, knight 75%, brawler 59%, swordsman 44%, archer 38%, thief 9%. Lancer (steel spear) and thief are now the outliers for the owner to tune.

## Evidence / handoff
- Tests: verify_weapon_system.gd gained a staff-ignores-defense check.
