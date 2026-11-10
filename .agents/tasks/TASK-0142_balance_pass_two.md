---
id: TASK-0142
status: review
owner: claude
agent: claude
priority: low
branch: claude/balance-pass-two
depends_on: TASK-0141
issue: none
art_request: none
touches: game_factory/weapons/weapon_stats.json,docs/WEAPON_BALANCE_REPORT_20261110.md
test: python tools/run_tests.py --changed
done_when: The two outliers from the staff-magic run (steel spear, assassin dagger) are tuned and the spread narrows.
estimate_minutes: 20
---
# Balance pass two

Steel spear attack 11 to 8 (its 1-2 range already helps a lot in duels) and assassin dagger attack 7 to 12. Win rates (20 seeds, 2.8 rounds): knight 84, warrior 83, lancer 77, brawler 59, swordsman 44, healer 36, thief 32, archer 30, mage 10. Mage remains lowest; it is a support class and the owner may prefer it that way.

## Evidence / handoff
- Revert by restoring the two attack values in weapon_stats.json.
