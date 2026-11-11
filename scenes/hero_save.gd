class_name HeroSave
extends RefCounted
## Persists the hero's weapon unit (equipped weapon + bag) as JSON. Invalid or missing saves fall back to the default unit,
## so a hand-edited file can never give an item the weapon data does not know or exceed the bag size.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const DEFAULT_PATH := "user://hero_unit.json"


static func save(unit: Dictionary, path: String = DEFAULT_PATH) -> bool:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		return false
	file.store_string(JSON.stringify({"version": 1, "weapon_id": unit.get("weapon_id", ""), "inventory": unit.get("inventory", [])}))
	return true


## Applies a saved weapon/bag to `unit` when it is valid for its class; returns true when something was applied.
static func load_into(weapons, unit: Dictionary, path: String = DEFAULT_PATH) -> bool:
	if not FileAccess.file_exists(path):
		return false
	var json := JSON.new()
	if json.parse(FileAccess.get_file_as_string(path)) != OK:
		return false
	var parsed: Variant = json.data
	if not (parsed is Dictionary) or int(parsed.get("version", 0)) != 1:
		return false
	var bag: Variant = parsed.get("inventory", [])
	var weapon_id: String = String(parsed.get("weapon_id", ""))
	if not (bag is Array) or bag.size() > weapons.capacity():
		return false
	var known: Dictionary = weapons.data.get("weapons", {})
	for item: Variant in bag:
		if not (item is String) or not known.has(item):
			return false
	var candidate: Dictionary = unit.duplicate(true)
	candidate.inventory = bag.duplicate()
	candidate.weapon_id = ""
	if weapon_id != "":
		if not known.has(weapon_id):
			return false
		candidate.inventory.append(weapon_id)  # the equipped weapon is stored apart from the bag
		if not weapons.equip(candidate, weapon_id).ok:
			return false
	unit.inventory = candidate.inventory
	unit.weapon_id = candidate.weapon_id
	return true
