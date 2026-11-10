extends SceneTree
## Headless verification of EquipmentMenu on top of WeaponSystem. Agent: claude (Claude Code); model: Sonnet 5.5.

const WeaponSystemScript = preload("res://scenes/battle/weapon_system.gd")

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	var ws = WeaponSystemScript.load_default()
	var unit: Dictionary = ws.make_unit("CHAR001", ["WPN_IRON_SWORD", "WPN_BATTLE_AXE", "WPN_KNIFE"], "WPN_HERO_BASIC_SWORD")
	var menu := EquipmentMenu.new()
	root.add_child(menu)
	var changes: Array = []
	menu.changed.connect(func(u): changes.append(u.weapon_id))
	menu.setup(ws, unit)
	_check(menu.title_label.text.contains("Hero") and menu.title_label.text.contains("Swordsman"), "title shows name and class")
	_check(menu.slots.item_count == ws.capacity(), "one list row per inventory slot")
	_check(menu.slots.get_item_text(0) == "Iron Sword" and menu.slots.get_item_text(3) == "-", "slots show names and empty marker")
	_check(menu.equipped_label.text.contains("Hero's Basic Sword") and menu.equipped_label.text.contains("Range 1-1"), "equipped line")
	_check(menu.equip_button.disabled and not menu.unequip_button.disabled, "no selection: equip disabled")

	menu.select_slot(0)
	_check(menu.preview_label.text.contains("ATK 14 -> 16 (+2)") or menu.preview_label.text.contains("(+2)"), "preview shows the attack change: " + menu.preview_label.text)
	_check(not menu.equip_button.disabled, "iron sword can be equipped")
	menu.select_slot(1)
	_check(menu.preview_label.text.contains("wrong_type") and menu.equip_button.disabled, "axe is shown as unusable")
	_check(not menu.equip_selected().ok, "equip of an unusable weapon fails")
	_check(changes.is_empty(), "no change signal on failure")

	menu.select_slot(0)
	var result: Dictionary = menu.equip_selected()
	_check(result.ok and unit.weapon_id == "WPN_IRON_SWORD", "equip works through WeaponSystem")
	_check(menu.slots.get_item_text(0) == "Hero's Basic Sword", "old weapon takes the slot of the new one")
	_check(changes == ["WPN_IRON_SWORD"], "change signal fired once")
	_check(menu.stats_label.text.contains("ATK 16"), "stats refreshed: " + menu.stats_label.text)

	_check(menu.unequip().ok and unit.weapon_id == "", "unequip")
	_check(menu.equipped_label.text.contains("Bare Fists") or menu.equipped_label.text.contains("(none)"), "unarmed line")
	var full: Dictionary = ws.make_unit("CHAR001", ["WPN_IRON_SWORD", "WPN_KNIFE", "WPN_STEEL_SWORD"], "WPN_HERO_BASIC_SWORD")
	ws.add_to_inventory(full, "WPN_WOOD_STAFF")
	menu.setup(ws, full)
	_check(full.inventory.size() == ws.capacity(), "inventory full")
	_check(menu.unequip_button.disabled, "unequip is disabled when the inventory is full")
	_check(menu.unequip().reason == "inventory_full" and full.weapon_id == "WPN_HERO_BASIC_SWORD", "unequip needs a free slot")
	menu.free()
	if _failures == 0:
		print("EQUIPMENT_MENU_OK")
	quit(0 if _failures == 0 else 1)
