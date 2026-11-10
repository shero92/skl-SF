---
id: TASK-0139
status: review
owner: claude
agent: claude
priority: medium
branch: claude/main-equip-key
depends_on: TASK-0121
issue: none
art_request: none
touches: tools/simulate_battles.gd,tools/tests/test_simulate_battles.py,tools/test_map.json,docs/WEAPON_BALANCE_REPORT_20261110.md
test: python tools/run_tests.py --changed
done_when: A deterministic headless simulation reports class and weapon balance using the real battle code, with a written report and a test.
estimate_minutes: 45
---
# Weapon and class balance simulation

`tools/simulate_battles.gd` runs every class against every class (1620 duels in about 5 s) through TurnManager, BattleResolver and EnemyAI and prints a JSON report; docs/WEAPON_BALANCE_REPORT_20261110.md records the first run: duels last 1.4 rounds on average (HP too low for the damage), brawler/knight/warrior/swordsman dominate, mage and healer are weak. No data was changed; the numbers are the owner's to tune.

## Evidence / handoff
- Tests: test_simulate_battles.py (id simulate_battles): determinism, every class covered, duels end.
- Next: owner chooses HP/attack targets; re-run the simulation after each change.
