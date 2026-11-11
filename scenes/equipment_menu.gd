extends PanelContainer
class_name EquipmentMenu
## Equip / unequip menu over WeaponSystem. Pure code UI (no art): the owner dialogue frame can wrap it later.
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## setup(weapon_system, unit) then the player picks an inventory slot (select_slot) and presses Equip.
## All rules (class limits, 4 slots, swap returning the old weapon) live in WeaponSystem; this only shows them.

signal changed(unit: Dictionary)
signal closed

const WeaponSystemScript = preload("res://scenes/battle/weapon_system.gd")

var weapons
var unit: Dictionary = {}
var selected_slot: int = -1

var title_label := Label.new()
var stats_label := Label.new()
var equipped_label := Label.new()
var preview_label := Label.new()
var message_label := Label.new()
var slots := ItemList.new()
var equip_button := Button.new()
var unequip_button := Button.new()
var close_button := Button.new()


func _init() -> void:
	name = "EquipmentMenu"
	var box := VBoxContainer.new()
	add_child(box)
	for label: Label in [title_label, stats_label, equipped_label, preview_label, message_label]:
		label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		box.add_child(label)
	slots.name = "InventorySlots"
	slots.custom_minimum_size = Vector2(260, 96)
	slots.item_selected.connect(select_slot)
	box.add_child(slots)
	var row := HBoxContainer.new()
	box.add_child(row)
	equip_button.text = "Equip"
	equip_button.pressed.connect(equip_selected)
	unequip_button.text = "Unequip"
	unequip_button.pressed.connect(unequip)
	close_button.text = "Close"
	close_button.pressed.connect(func(): closed.emit())
	for button: Button in [equip_button, unequip_button, close_button]:
		row.add_child(button)


func setup(weapon_system, target_unit: Dictionary) -> void:
	weapons = weapon_system
	unit = target_unit
	selected_slot = -1
	message_label.text = ""
	refresh()


func weapon_name(weapon_id: String) -> String:
	return String(weapons.weapon(weapon_id).get("name", weapon_id)) if weapon_id != "" else "(none)"


func refresh() -> void:
	var class_def: Dictionary = weapons.class_def(unit.get("class_id", ""))
	var character: Dictionary = weapons.data.get("characters", {}).get(unit.get("character_id", ""), {})
	title_label.text = "%s - %s" % [character.get("name", unit.get("character_id", "?")), class_def.get("name", "?")]
	var base: Dictionary = weapons.base_stats(unit)
	var effective: Dictionary = weapons.effective_stats(unit)
	stats_label.text = "ATK %d (base %d)  DEF %d  AGI %d  MOVE %d" % [
		effective.get("attack", 0), base.get("attack", 0), effective.get("defense", 0),
		effective.get("agility", 0), effective.get("move", 0)]
	var span: Dictionary = weapons.attack_range(unit)
	var current: String = unit.get("weapon_id", "")
	equipped_label.text = "Weapon: %s   Range %d-%d (%s)   Hit %d%%  Crit %d%%" % [
		weapon_name(current), span.min, span.max, span.kind,
		int(weapons.weapon(weapons.active_weapon_id(unit)).get("accuracy", 0)), weapons.crit_chance(unit)]
	slots.clear()
	for i in weapons.capacity():
		var items: Array = unit.inventory
		var text := weapon_name(String(items[i])) if i < items.size() else "-"
		slots.add_item(text)
		if i < items.size() and not weapons.can_equip(unit.class_id, String(items[i])):
			slots.set_item_custom_fg_color(i, Color(0.6, 0.6, 0.6))
	if selected_slot >= 0 and selected_slot < slots.item_count:
		slots.select(selected_slot)
	preview_label.text = preview_text(selected_item())
	equip_button.disabled = selected_item() == "" or not weapons.can_equip(unit.class_id, selected_item())
	unequip_button.disabled = current == "" or unit.inventory.size() >= weapons.capacity()


func selected_item() -> String:
	var items: Array = unit.get("inventory", [])
	return String(items[selected_slot]) if selected_slot >= 0 and selected_slot < items.size() else ""


func select_slot(index: int) -> void:
	selected_slot = index
	refresh()


## What equipping weapon_id would change, or why it cannot be equipped.
func preview_text(weapon_id: String) -> String:
	if weapon_id == "":
		return ""
	var reason: String = weapons.equip_block_reason(unit.class_id, weapon_id)
	if reason != "":
		return "%s cannot be equipped (%s)" % [weapon_name(weapon_id), reason]
	var trial := unit.duplicate(true)
	trial.weapon_id = weapon_id
	var before: int = weapons.effective_stats(unit).attack
	var after: int = weapons.effective_stats(trial).attack
	var span: Dictionary = weapons.attack_range(trial)
	return "%s: ATK %d -> %d (%+d)  Range %d-%d  Hit %d%%  Crit %d%%" % [
		weapon_name(weapon_id), before, after, after - before, span.min, span.max,
		int(weapons.weapon(weapon_id).accuracy), weapons.crit_chance(trial)]


func equip_selected() -> Dictionary:
	var weapon_id := selected_item()
	var result: Dictionary = weapons.equip(unit, weapon_id) if weapon_id != "" else {"ok": false, "reason": "nothing_selected"}
	selected_slot = -1
	message_label.text = "Equipped %s" % weapon_name(weapon_id) if result.ok else "Cannot equip: %s" % result.reason
	refresh()
	if result.ok:
		changed.emit(unit)
	return result


func unequip() -> Dictionary:
	var result: Dictionary = weapons.unequip(unit)
	selected_slot = -1
	message_label.text = "Weapon put away" if result.ok else "Cannot unequip: %s" % result.reason
	refresh()
	if result.ok:
		changed.emit(unit)
	return result
