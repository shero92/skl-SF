---
id: TASK-0136
status: review
owner: claude
agent: claude
priority: medium
branch: claude/equip-menu
depends_on: TASK-0118
issue: none
art_request: none
touches: scenes/main.gd,tools/verify_main_equipment.gd,scenes/equipment_menu.gd,scenes/battle/weapon_system.gd,tools/verify_equipment_menu.gd,tools/verify_weapon_system.gd,tools/tests/test_equipment_menu.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: A code-only equip/unequip menu shows slots, class limits and the attack change and drives WeaponSystem; a swapped-out weapon takes the new weapon's slot; verified headlessly.
estimate_minutes: 60
---
# Equipment menu over WeaponSystem

`EquipmentMenu` (scenes/equipment_menu.gd): setup(weapon_system, unit), four inventory rows (unusable weapons greyed), preview line (ATK before -> after, range, hit, crit, or why it cannot be equipped), Equip / Unequip / Close buttons, `changed(unit)` and `closed` signals. WeaponSystem.equip now puts the old weapon into the slot of the new one (Shining Force swap) instead of appending it.

## Not done
No art or frame (the dialogue frame can wrap it); no shop; no gamepad focus handling beyond Godot defaults.

## Evidence / handoff
- Tests: verify_equipment_menu.gd via test_equipment_menu.py (id equipment_menu); verify_weapon_system.gd gained the slot check.
- Main scene: I opens and closes the menu for the hero unit (CHAR001, basic sword equipped, an iron sword in the bag); the hero is frozen and interactions are blocked while it is open, and I is ignored during a dialogue (tools/verify_main_equipment.gd).
- Next: persistent hero inventory, a shop, and showing the equipped sword on the hero sprite.
