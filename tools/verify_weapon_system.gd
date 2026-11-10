extends SceneTree
## Headless verification of the weapon system rules and data.
## Agent: claude (Claude Code); model: Sonnet 5.5.

const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	var ws = WeaponSystem.load_default()
	_test_data(ws)
	_test_equip(ws)
	_test_stats(ws)
	_test_range(ws)
	_test_combat(ws)
	if _failures == 0:
		print("WEAPON_SYSTEM_OK")
	quit(0 if _failures == 0 else 1)


func _test_data(ws) -> void:
	var catalog: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/weapons/catalog.json"))
	var profiles: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://game_factory/weapons/profiles.json"))
	for weapon_id: String in ws.data.weapons:
		var item: Dictionary = ws.data.weapons[weapon_id]
		_check(ws.data.weapon_types.has(item.type), weapon_id + " has unknown type")
		_check(int(item.attack) >= 0 and int(item.price) >= 0, weapon_id + " bad numbers")
		_check(int(item.accuracy) >= 1 and int(item.accuracy) <= 100, weapon_id + " bad accuracy")
		if item.asset_id != null:
			_check(catalog.weapons.has(item.asset_id), weapon_id + " asset_id missing from catalog")
	for type_id: String in ws.data.weapon_types:
		var type_def: Dictionary = ws.data.weapon_types[type_id]
		_check(profiles.profiles.has(type_def.profile), type_id + " profile missing")
		_check(int(type_def.range[0]) <= int(type_def.range[1]), type_id + " range inverted")
	for class_id: String in ws.data.classes:
		var cls: Dictionary = ws.data.classes[class_id]
		for type_id: String in cls.weapon_types:
			_check(ws.data.weapon_types.has(type_id), class_id + " unknown type " + type_id)
		_check(ws.data.weapons.has(cls.unarmed), class_id + " unarmed weapon missing")
		_check(ws.can_equip(class_id, cls.unarmed), class_id + " cannot use its unarmed weapon")
		var usable := 0
		for weapon_id: String in ws.data.weapons:
			if ws.can_equip(class_id, weapon_id):
				usable += 1
		_check(usable >= 2, class_id + " has fewer than 2 usable weapons")
	for character_id: String in profiles.character_profiles:
		_check(ws.data.characters.has(character_id), character_id + " has no class")
	for character_id: String in ws.data.characters:
		_check(ws.data.classes.has(ws.data.characters[character_id].class), character_id + " bad class")
	_check(not ws.can_equip("swordsman", "WPN_BATTLE_AXE"), "swordsman must not use axes")
	_check(not ws.can_equip("warrior", "WPN_IRON_SWORD"), "warrior must not use swords")
	_check(not ws.can_equip("mage", "WPN_NATURAL_CLAWS"), "claws are class locked")


func _test_equip(ws) -> void:
	var hero = ws.make_unit("CHAR001", ["WPN_IRON_SWORD", "WPN_BATTLE_AXE"], "WPN_HERO_BASIC_SWORD")
	_check(hero.weapon_id == "WPN_HERO_BASIC_SWORD", "initial equip")
	_check(ws.equip(hero, "WPN_BATTLE_AXE").reason == "wrong_type", "axe rejected")
	_check(ws.equip(hero, "WPN_STEEL_SWORD").reason == "not_in_inventory", "missing item rejected")
	var swap: Dictionary = ws.equip(hero, "WPN_IRON_SWORD")
	_check(swap.ok and swap.previous == "WPN_HERO_BASIC_SWORD", "swap result")
	_check(hero.inventory.has("WPN_HERO_BASIC_SWORD") and not hero.inventory.has("WPN_IRON_SWORD"), "swap inventory")
	_check(hero.inventory[0] == "WPN_HERO_BASIC_SWORD", "the old weapon takes the new weapon's slot")
	_check(ws.equippable_in_inventory(hero) == ["WPN_HERO_BASIC_SWORD"], "equippable list")
	_check(ws.unequip(hero).ok and hero.weapon_id == "", "unequip")
	_check(ws.unequip(hero).reason == "nothing_equipped", "double unequip")
	ws.equip(hero, "WPN_IRON_SWORD")
	for filler in ["WPN_KNIFE", "WPN_WOOD_STAFF"]:
		ws.add_to_inventory(hero, filler)
	_check(hero.inventory.size() == ws.capacity(), "inventory full")
	_check(ws.unequip(hero).reason == "inventory_full", "unequip needs room")
	_check(not ws.add_to_inventory(hero, "WPN_KNIFE"), "capacity respected")
	_check(ws.equip(ws.make_unit("CHAR003", ["WPN_IRON_SWORD"]), "WPN_IRON_SWORD").reason == "wrong_type", "brawler no sword")


func _test_stats(ws) -> void:
	var hero = ws.make_unit("CHAR001", ["WPN_MITHRIL_SWORD"])
	var bare: Dictionary = ws.effective_stats(hero)
	_check(ws.active_weapon_id(hero) == "WPN_FISTS", "fists fallback")
	_check(bare.attack == 9 + 2, "bare-handed attack = base + fists, got %s" % bare.attack)
	ws.equip(hero, "WPN_MITHRIL_SWORD")
	var armed: Dictionary = ws.effective_stats(hero)
	_check(armed.attack == 9 + 16, "armed attack, got %s" % armed.attack)
	_check(armed.agility == 7 + 2, "stat_bonus agility")
	_check(ws.base_stats(hero).attack == 9, "base unchanged by weapon")


func _test_range(ws) -> void:
	var archer = ws.make_unit("CHAR006", ["WPN_SHORT_BOW", "WPN_LONG_BOW"], "WPN_SHORT_BOW")
	_check(not ws.can_attack_at(archer, 1), "bow cannot hit adjacent")
	_check(ws.can_attack_at(archer, 2) and ws.can_attack_at(archer, 3) and not ws.can_attack_at(archer, 4), "bow 2-3")
	ws.equip(archer, "WPN_LONG_BOW")
	_check(ws.can_attack_at(archer, 4), "long bow range bonus")
	var lancer = ws.make_unit("CHAR002", ["WPN_STEEL_SPEAR"], "WPN_STEEL_SPEAR")
	_check(ws.can_attack_at(lancer, 1) and ws.can_attack_at(lancer, 2) and not ws.can_attack_at(lancer, 3), "spear 1-2")
	var mage = ws.make_unit("CHAR005", ["WPN_WOOD_STAFF"], "WPN_WOOD_STAFF")
	_check(ws.attack_range(mage).kind == "magic", "staff is magic")
	var hero = ws.make_unit("CHAR001")
	_check(ws.attackable_cells(hero, Vector2i(5, 5)).size() == 4, "melee reaches 4 cells")
	_check(ws.attackable_cells(archer, Vector2i(5, 5)).size() == 8 + 12 + 16, "long bow ring 2-4 size")
	_check(WeaponSystem.grid_distance(Vector2i(0, 0), Vector2i(2, 3)) == 5, "grid distance")


func _test_combat(ws) -> void:
	var hero = ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD")
	var foe = ws.make_unit("CHAR004")
	_check(ws.damage(hero, foe) == (9 + 7) - 6, "damage = attack - defense")
	_check(ws.damage(hero, foe, true) == int(10 * 1.5), "crit damage")
	var weak = ws.make_unit("CHAR005")
	_check(ws.damage(weak, ws.make_unit("CHAR004")) == 1, "minimum damage 1")
	var mage_unit = ws.make_unit("CHAR001")
	mage_unit.class_id = "mage"
	mage_unit.inventory = ["WPN_WOOD_STAFF"]
	ws.equip(mage_unit, "WPN_WOOD_STAFF")
	var armored = ws.make_unit("CHAR004")
	_check(ws.damage(mage_unit, armored) == maxi(1, int(ws.effective_stats(mage_unit).attack)), "staff (magic) ignores target defense")
	_check(ws.hit_chance(hero, foe) == 95 + (7 - 4), "hit chance uses agility")
	var thief = ws.make_unit("CHAR001", ["WPN_ASSASSIN_DAGGER"], "WPN_ASSASSIN_DAGGER")
	_check(ws.crit_chance(thief) == 12, "crit chance")
	_check(ws.hit_statuses(thief) == [{"status": "poison", "chance": 25}], "poison on hit")
	_check(ws.art_profile(hero) == "sword", "sword profile")
	_check(ws.art_profile(ws.make_unit("CHAR006", ["WPN_SHORT_BOW"], "WPN_SHORT_BOW")) == "bow", "bow profile")
