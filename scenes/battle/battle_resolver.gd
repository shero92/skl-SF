extends RefCounted
## Resolves one weapon attack between two units using WeaponSystem rules.
## Agent: claude (Claude Code); model: Sonnet 5.5.
## Pure data: no animation. Call resolve() from BattleAnimationController.hit so damage lands on the hit frame.
## Units are WeaponSystem unit Dictionaries; "hp" is created on first use from effective max HP.

const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")

var weapons
var rng := RandomNumberGenerator.new()


func _init(weapon_system = null, seed_value: int = 0) -> void:
	weapons = weapon_system if weapon_system != null else WeaponSystem.load_default()
	rng.seed = seed_value


func current_hp(unit: Dictionary) -> int:
	if not unit.has("hp"):
		unit["hp"] = int(weapons.effective_stats(unit).get("hp", 1))
	return int(unit.hp)


func is_defeated(unit: Dictionary) -> bool:
	return current_hp(unit) <= 0


## Pre-check without rolling: can `attacker` at `from_cell` attack `target_cell`?
func can_target(attacker: Dictionary, from_cell: Vector2i, target_cell: Vector2i) -> bool:
	return not is_defeated(attacker) and weapons.can_attack_at(attacker, WeaponSystem.grid_distance(from_cell, target_cell))


## Rolls and applies one attack. Returns {ok, reason, hit, critical, damage, defender_hp, defeated, statuses}.
func resolve(attacker: Dictionary, defender: Dictionary, attacker_cell: Vector2i, defender_cell: Vector2i) -> Dictionary:
	var result := {"ok": false, "reason": "", "hit": false, "critical": false, "damage": 0,
		"defender_hp": current_hp(defender), "defeated": false, "statuses": []}
	if is_defeated(attacker):
		result.reason = "attacker_defeated"
		return result
	if is_defeated(defender):
		result.reason = "defender_defeated"
		return result
	if not can_target(attacker, attacker_cell, defender_cell):
		result.reason = "out_of_range"
		return result
	result.ok = true
	result.hit = rng.randi_range(1, 100) <= weapons.hit_chance(attacker, defender)
	if not result.hit:
		return result
	result.critical = rng.randi_range(1, 100) <= weapons.crit_chance(attacker)
	result.damage = weapons.damage(attacker, defender, result.critical)
	defender.hp = maxi(0, current_hp(defender) - int(result.damage))
	result.defender_hp = defender.hp
	result.defeated = defender.hp <= 0
	if not result.defeated:
		for status: Dictionary in weapons.hit_statuses(attacker):
			if rng.randi_range(1, 100) <= int(status.chance):
				var list: Array = defender.get_or_add("statuses", [])
				if not list.has(status.status):
					list.append(status.status)
				result.statuses.append(status.status)
	return result


## Asset id of the equipped weapon for ModularActorAdapter.equip(); "" when no art exists (fists, pending art).
func art_asset_id(unit: Dictionary) -> String:
	var asset: Variant = weapons.weapon(weapons.active_weapon_id(unit)).get("asset_id")
	return "" if asset == null else String(asset)
