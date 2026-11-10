# Weapon and class balance simulation (2026-11-10)

Tool: `tools/simulate_battles.gd` (`godot --headless --path . --script res://tools/simulate_battles.gd -- <seeds> <max_turns>`, prints one JSON line). Each class equips its highest-attack non-builtin weapon of tier <= 2 and duels every class 1v1 with the real `TurnManager`, `BattleResolver` and `EnemyAI` on an open 12x8 grid, alternating sides by seed. 1620 duels (20 seeds per pairing) ran in about 5 s. Informational only: the numbers in `game_factory/weapons/weapon_stats.json` are placeholders for the owner to tune; nothing was changed.

## Findings
- Duels last **1.4 rounds on average** and no duel hit the turn limit (draw rate 0.0%). One or two hits end a fight, because base HP (12 to 26) is close to a single hit (weapon + base attack minus defense is 10 to 20). Shining Force pacing needs roughly 3 to 5 exchanges, so HP should be about 2 to 3 times higher or damage lower.
- **Dominant:** brawler (natural claws, attack 9 and 6 percent crit, no price or tier), knight, warrior, swordsman.
- **Weak:** mage (dagger chosen as its highest-attack weapon, 12 HP) and healer (mace); thief loses to every armoured class. A staff/mage should get a magic advantage or a longer reach, and the support classes need a reason to be taken.
- Ranged (archer) and spear (lancer) land near 50 percent: the AI moves into reach, so range matters less in a duel than in a team fight.

## Overall win rate by class
| Class | Weapon used | Win rate |
|---|---|---|
| brawler | (natural claws) | 79% |
| knight | WPN_STEEL_SWORD | 76% |
| warrior | WPN_BATTLE_AXE | 72% |
| swordsman | WPN_STEEL_SWORD | 66% |
| lancer | WPN_STEEL_SWORD | 48% |
| archer | WPN_LONG_BOW | 46% |
| thief | WPN_STEEL_SWORD | 32% |
| healer | WPN_IRON_MACE | 24% |
| mage | WPN_ASSASSIN_DAGGER | 6% |

## Matchup matrix (row wins against column, percent)
| vs | arch | braw | heal | knig | lanc | mage | swor | thie | warr |
|---|---|---|---|---|---|---|---|---|---|
| archer | 60 | 0 | 85 | 0 | 75 | 100 | 70 | 5 | 20 |
| brawler | 100 | 45 | 100 | 90 | 85 | 100 | 10 | 100 | 80 |
| healer | 15 | 0 | 45 | 0 | 0 | 85 | 0 | 70 | 0 |
| knight | 100 | 10 | 100 | 50 | 95 | 100 | 100 | 100 | 30 |
| lancer | 25 | 15 | 100 | 5 | 50 | 100 | 10 | 100 | 30 |
| mage | 0 | 0 | 15 | 0 | 0 | 40 | 0 | 0 | 0 |
| swordsman | 30 | 90 | 100 | 0 | 90 | 100 | 50 | 100 | 30 |
| thief | 95 | 0 | 30 | 0 | 0 | 100 | 0 | 50 | 10 |
| warrior | 80 | 20 | 100 | 70 | 70 | 100 | 70 | 90 | 45 |

## Suggested next steps (owner decision)
1. Raise class HP (about x2.5) or lower weapon attack until duels last 3 to 5 exchanges.
2. Reduce natural claws (attack 9 to about 6) or give the brawler lower defense/HP.
3. Give staffs a magic power stat or a minimum damage so the mage is not better with a dagger.
4. Re-run the simulation after each change; it is deterministic for the same seeds.

## Pass one applied (TASK-0140)
Class base HP x2.5 and natural claws attack 9 to 6. Result (20 seeds): average 2.5 rounds, 0% draws. Win rates: warrior 88, knight 86, swordsman 64, brawler 63, lancer 62, archer 36, thief 31, healer 16, mage 5. Still open: a magic stat or minimum damage for staffs so mage and healer have a role.

## Staff magic applied (TASK-0141)
Staffs (`kind: magic`) ignore target defense; the simulation uses each class's first weapon type. Win rates: lancer 92, warrior 80, knight 75, brawler 59, swordsman 44, archer 38, healer 38, mage 19, thief 9. Open: tune steel spear down and thief up.
