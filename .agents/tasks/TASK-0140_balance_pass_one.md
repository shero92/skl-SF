---
id: TASK-0140
status: review
owner: claude
agent: claude
priority: medium
branch: claude/balance-tuning
depends_on: TASK-0139
issue: none
art_request: none
touches: game_factory/weapons/weapon_stats.json,tools/verify_weapon_battle.gd,docs/WEAPON_BALANCE_REPORT_20261110.md
test: python tools/run_tests.py --changed
done_when: Class HP is raised and brawler claws lowered per the balance report, duels last longer, and the tests still pass.
estimate_minutes: 30
---
# Balance pass one

Applied the first two suggestions of the balance report: class base HP x2.5 and natural claws attack 9 to 6. Average duel length went from 1.4 to 2.5 rounds, no draws. Mage (5%) and healer (16%) are still weak: staff magic is a design decision left to the owner. `verify_weapon_battle.gd` no longer hard-codes the foe's HP.

## Evidence / handoff
- Win rates after: warrior 88, knight 86, swordsman 64, brawler 63, lancer 62, archer 36, thief 31, healer 16, mage 5.
- Revert by restoring the previous values in weapon_stats.json (see git history).
