extends RefCounted
## Shining Force style weapon rules: equip/unequip, stats, range and damage.
## Data: res://game_factory/weapons/weapon_stats.json. Agent: claude (Claude Code); model: Sonnet 5.5.
## A unit is a plain Dictionary: {class_id, character_id?, stat_offsets?, weapon_id, inventory:Array}.
## Every API returns plain data (Dictionary / int / bool) so battle, inventory and UI can share it.

const DATA_PATH := "res://game_factory/weapons/weapon_stats.json"
const STATS := ["hp", "mp", "attack", "defense", "agility", "move"]

var data: Dictionary = {}


static func load_default() -> RefCounted:
	var system := new()
	system.data = JSON.parse_string(FileAccess.get_file_as_string(DATA_PATH))
	return system


func capacity() -> int:
	return int(data.get("inventory_capacity", 4))


func weapon(weapon_id: String) -> Dictionary:
	return data.get("weapons", {}).get(weapon_id, {})


func class_def(class_id: String) -> Dictionary:
	return data.get("classes", {}).get(class_id, {})


## Creates a unit for a character id (CHAR001...) with its class, empty hands and inventory.
func make_unit(character_id: String, inventory: Array = [], weapon_id: String = "") -> Dictionary:
	var entry: Dictionary = data.get("characters", {}).get(character_id, {})
	var unit := {
		"character_id": character_id,
		"class_id": entry.get("class", ""),
		"stat_offsets": entry.get("stat_offsets", {}).duplicate(),
		"weapon_id": "",
		"inventory": inventory.duplicate(),
	}
	if weapon_id != "":
		unit.inventory.append(weapon_id)
		if not equip(unit, weapon_id).ok:
			unit.inventory.erase(weapon_id)
	return unit


## Why a weapon cannot be used by a class: "" when it can.
func equip_block_reason(class_id: String, weapon_id: String) -> String:
	var cls := class_def(class_id)
	var item := weapon(weapon_id)
	if cls.is_empty():
		return "unknown_class"
	if item.is_empty():
		return "unknown_weapon"
	if not item.get("equip_classes", [class_id]).has(class_id):
		return "class_locked"
	if not cls.get("weapon_types", []).has(item.type) and not (item.get("builtin", false) and item.get("equip_classes", []).is_empty()):
		return "wrong_type"
	return ""


func can_equip(class_id: String, weapon_id: String) -> bool:
	return equip_block_reason(class_id, weapon_id) == ""


## Equips a weapon that is in the unit's inventory. The old weapon returns to the inventory.
## Returns {ok, reason, previous}.
func equip(unit: Dictionary, weapon_id: String) -> Dictionary:
	var reason := equip_block_reason(unit.get("class_id", ""), weapon_id)
	if reason == "":
		var inventory: Array = unit.inventory
		if not inventory.has(weapon_id):
			reason = "not_in_inventory"
	if reason != "":
		return {"ok": false, "reason": reason, "previous": unit.get("weapon_id", "")}
	var previous: String = unit.get("weapon_id", "")
	unit.inventory.erase(weapon_id)
	unit.weapon_id = weapon_id
	if previous != "":
		unit.inventory.append(previous)
	return {"ok": true, "reason": "", "previous": previous}


## Returns the weapon to the inventory. Fails when the inventory is full or hands are empty.
func unequip(unit: Dictionary) -> Dictionary:
	var current: String = unit.get("weapon_id", "")
	if current == "":
		return {"ok": false, "reason": "nothing_equipped", "previous": ""}
	if unit.inventory.size() >= capacity():
		return {"ok": false, "reason": "inventory_full", "previous": current}
	unit.inventory.append(current)
	unit.weapon_id = ""
	return {"ok": true, "reason": "", "previous": current}


## Adds an item to the inventory, respecting capacity.
func add_to_inventory(unit: Dictionary, weapon_id: String) -> bool:
	if weapon(weapon_id).is_empty() or unit.inventory.size() >= capacity():
		return false
	unit.inventory.append(weapon_id)
	return true


## Weapons in the inventory this unit could equip right now.
func equippable_in_inventory(unit: Dictionary) -> Array:
	var result: Array = []
	for weapon_id: String in unit.inventory:
		if can_equip(unit.class_id, weapon_id):
			result.append(weapon_id)
	return result


## The weapon actually used in combat: equipped weapon, else the class's natural/fist fallback.
func active_weapon_id(unit: Dictionary) -> String:
	var current: String = unit.get("weapon_id", "")
	return current if current != "" else String(class_def(unit.get("class_id", "")).get("unarmed", ""))


func _effect_total(item: Dictionary, kind: String, field: String = "value", match_stat: String = "") -> int:
	var total := 0
	for effect: Dictionary in item.get("effects", []):
		if effect.get("kind", "") != kind:
			continue
		if match_stat != "" and effect.get("stat", "") != match_stat:
			continue
		total += int(effect.get(field, 0))
	return total


## Base stats (class + character offsets) with no weapon.
func base_stats(unit: Dictionary) -> Dictionary:
	var stats: Dictionary = class_def(unit.get("class_id", "")).get("base_stats", {}).duplicate()
	for key: String in unit.get("stat_offsets", {}):
		stats[key] = int(stats.get(key, 0)) + int(unit.stat_offsets[key])
	return stats


## Effective stats: attack = base attack + weapon attack; stat_bonus effects add to their stat.
func effective_stats(unit: Dictionary) -> Dictionary:
	var stats := base_stats(unit)
	var item := weapon(active_weapon_id(unit))
	if item.is_empty():
		return stats
	stats["attack"] = int(stats.get("attack", 0)) + int(item.attack)
	for stat: String in STATS:
		stats[stat] = int(stats.get(stat, 0)) + _effect_total(item, "stat_bonus", "value", stat)
	return stats


## {kind: melee|ranged|magic, min, max} for the active weapon (type range + range_bonus).
func attack_range(unit: Dictionary) -> Dictionary:
	var item := weapon(active_weapon_id(unit))
	var type_def: Dictionary = data.get("weapon_types", {}).get(item.get("type", ""), {})
	if type_def.is_empty():
		return {"kind": "melee", "min": 1, "max": 1}
	var span: Array = type_def.range
	return {"kind": type_def.kind, "min": int(span[0]), "max": int(span[1]) + _effect_total(item, "range_bonus")}


func can_attack_at(unit: Dictionary, distance: int) -> bool:
	var span := attack_range(unit)
	return distance >= int(span.min) and distance <= int(span.max)


## Manhattan distance on the tactical grid.
static func grid_distance(a: Vector2i, b: Vector2i) -> int:
	return absi(a.x - b.x) + absi(a.y - b.y)


## Tiles the unit can attack from `origin`.
func attackable_cells(unit: Dictionary, origin: Vector2i) -> Array:
	var span := attack_range(unit)
	var cells: Array = []
	for dx in range(-int(span.max), int(span.max) + 1):
		for dy in range(-int(span.max), int(span.max) + 1):
			var distance := absi(dx) + absi(dy)
			if distance >= int(span.min) and distance <= int(span.max):
				cells.append(origin + Vector2i(dx, dy))
	return cells


## Hit chance in percent, clamped to 5..100: weapon accuracy + (attacker agility - defender agility).
func hit_chance(attacker: Dictionary, defender: Dictionary) -> int:
	var item := weapon(active_weapon_id(attacker))
	var accuracy := int(item.get("accuracy", 90))
	var difference := int(effective_stats(attacker).get("agility", 0)) - int(effective_stats(defender).get("agility", 0))
	return clampi(accuracy + difference, 5, 100)


## Crit chance in percent, 0..100: weapon crit + crit_bonus effects.
func crit_chance(attacker: Dictionary) -> int:
	var item := weapon(active_weapon_id(attacker))
	return clampi(int(item.get("crit", 0)) + _effect_total(item, "crit_bonus"), 0, 100)


## Damage of a normal hit: max(1, attacker attack - defender defense); crits deal 1.5x (rounded down).
func damage(attacker: Dictionary, defender: Dictionary, critical: bool = false) -> int:
	var raw := int(effective_stats(attacker).attack) - int(effective_stats(defender).defense)
	var dealt := maxi(1, raw)
	return int(dealt * 1.5) if critical else dealt


## Status effects the active weapon can inflict: [{status, chance}].
func hit_statuses(unit: Dictionary) -> Array:
	var result: Array = []
	for effect: Dictionary in weapon(active_weapon_id(unit)).get("effects", []):
		if effect.get("kind", "") == "status_on_hit":
			result.append({"status": effect.status, "chance": int(effect.chance)})
	return result


## Art profile name (game_factory/weapons/profiles.json) of the active weapon, for the battle actor.
func art_profile(unit: Dictionary) -> String:
	var item := weapon(active_weapon_id(unit))
	return String(data.get("weapon_types", {}).get(item.get("type", ""), {}).get("profile", "natural"))
