---
id: TASK-0143
status: review
owner: claude
agent: claude
priority: medium
branch: claude/hero-save
depends_on: TASK-0136
issue: none
art_request: none
touches: scenes/hero_save.gd,scenes/main.gd,tools/verify_hero_save.gd,tools/verify_main_equipment.gd,tools/tests/test_hero_save.py,tools/test_map.json,docs/RUNTIME_INTEGRATION.md
test: python tools/run_tests.py --changed
done_when: The hero's equipped weapon and bag persist between runs, invalid saves are ignored, and tests prove both.
estimate_minutes: 40
---
# Hero weapon save

`HeroSave` writes `{version, weapon_id, inventory}` to `user://hero_unit.json` (outside the repo) whenever the equipment menu changes something, and `main.gd` applies it on start. A save is rejected as a whole (hero keeps defaults) when it is unparsable, a different version, has unknown items, exceeds the bag size, or equips something the class cannot use.

## Evidence / handoff
- Tests: test_hero_save.py (round trip, six rejected files); test_equipment_menu.py now uses an isolated save path so tests never touch the real save.
