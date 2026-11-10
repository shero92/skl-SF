extends SceneTree
## Headless check of HeroSave: round trip, invalid files ignored, bag limit, unknown items.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")
const PATH := "user://verify_hero_unit.json"
var _failures := 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _write(text: String) -> void:
	var file := FileAccess.open(PATH, FileAccess.WRITE)
	file.store_string(text)
	file.close()


func _fresh(ws) -> Dictionary:
	return ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_HERO_BASIC_SWORD")


func _initialize() -> void:
	var ws = WeaponSystem.load_default()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(PATH))
	_check(not HeroSave.load_into(ws, _fresh(ws), PATH), "missing file changes nothing")
	var unit := _fresh(ws)
	_check(ws.equip(unit, "WPN_IRON_SWORD").ok, "equip iron sword")
	_check(HeroSave.save(unit, PATH), "save works")
	var restored := _fresh(ws)
	_check(HeroSave.load_into(ws, restored, PATH), "valid save loads")
	_check(restored.weapon_id == "WPN_IRON_SWORD" and restored.inventory == unit.inventory, "round trip keeps weapon and bag: %s vs %s" % [restored, unit])
	for bad in ['not json', '{"version": 2}', '{"version":1,"weapon_id":"","inventory":["WPN_NOPE"]}',
			'{"version":1,"weapon_id":"WPN_NOPE","inventory":[]}',
			'{"version":1,"weapon_id":"","inventory":["WPN_IRON_SWORD","WPN_IRON_SWORD","WPN_IRON_SWORD","WPN_IRON_SWORD","WPN_IRON_SWORD"]}',
			'{"version":1,"weapon_id":"WPN_BATTLE_AXE","inventory":["WPN_BATTLE_AXE"]}']:
		_write(bad)
		var target := _fresh(ws)
		var before := target.duplicate(true)
		_check(not HeroSave.load_into(ws, target, PATH) and target == before, "rejects: " + bad.left(40))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(PATH))
	if _failures == 0:
		print("HERO_SAVE_OK")
	quit(0 if _failures == 0 else 1)
