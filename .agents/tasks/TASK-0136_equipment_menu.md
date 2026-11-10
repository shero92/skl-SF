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
touches: scenes/equipment_menu.gd,scenes/battle/weapon_system.gd,tools/verify_equipment_menu.gd,tools/verify_weapon_system.gd,tools/tests/test_equipment_menu.py,tools/test_map.json
test: python tools/run_tests.py --changed
done_when: A code-only equip/unequip menu shows slots, class limits and the attack change and drives WeaponSystem; a swapped-out weapon takes the new weapon's slot; verified headlessly.
estimate_minutes: 60
---
# Equipment menu over WeaponSystem

`EquipmentMenu` (scenes/equipment_menu.gd): setup(weapon_system, unit), four inventory rows (unusable weapons greyed), preview line (ATK before -> after, range, hit, crit, or why it cannot be equipped), Equip / Unequip / Close buttons, `changed(unit)` and `closed` signals. WeaponSystem.equip now puts the old weapon into the slot of the new one (Shining Force swap) instead of appending it.

## Not done
No art or frame (the dialogue frame can wrap it); not opened from the main scene yet (no inventory key binding, no shop); no gamepad focus handling beyond Godot defaults.

## Evidence / handoff
- Tests: verify_equipment_menu.gd via test_equipment_menu.py (id equipment_menu); verify_weapon_system.gd gained the slot check.
- Next: open the menu from the main scene with a key and the player's unit.
