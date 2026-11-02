extends SceneTree
## Behavioural checks using metadata tokens, without loading or changing art.

const Perspective = preload("res://scenes/battle/battle_perspective.gd")

var failures: int = 0


func check(condition: bool, message: String) -> void:
	if not condition:
		failures += 1
		printerr("ERROR: " + message)


func _initialize() -> void:
	var assets: Dictionary = {
		"hero_rear_3q": "authored hero rear",
		"hero_front": "authored hero front",
		"monster_front": "authored monster front",
		"monster_rear": "authored monster rear",
	}
	# Independent expectations exercise every documented attacker/phase pair.
	var cases: Array = [
		["hero", "attack", "HERO_REAR_3Q", ["hero_rear_3q", "monster_front"]],
		["hero", "defend", "HERO_FRONT", ["hero_front", "monster_rear"]],
		["monster", "attack", "HERO_FRONT", ["hero_front", "monster_rear"]],
		["monster", "defend", "MONSTER_REAR", ["monster_rear", "hero_front"]],
	]
	for entry in cases:
		var label: String = entry[0] + "/" + entry[1]
		var result: Dictionary = Perspective.resolve(entry[0], entry[1], assets)
		check(result["view_id"] == entry[2], label + ": view")
		check(result["required_asset_keys"] == entry[3], label + ": asset keys")
		check(result["ready"], label + ": complete assets")
		check(result["warnings"].is_empty(), label + ": unexpected warning")
		check(result["missing_asset_keys"].is_empty(), label + ": unexpected missing art")
		check(result["resolved_assets"].size() == 2, label + ": only required assets")
		for key in entry[3]:
			check(result["resolved_assets"].get(key) == assets[key], label + ": authored asset")

			for null_resource in [false, true]:
				var incomplete: Dictionary = assets.duplicate()
				if null_resource:
					incomplete[key] = null
				else:
					incomplete.erase(key)
				# Side art must never satisfy a missing front or rear requirement.
				incomplete["hero_side"] = "side hero"
				incomplete["monster_side"] = "side monster"
				var missing: Dictionary = Perspective.resolve(entry[0], entry[1], incomplete)
				var warning: String = (
					"MISSING_REAR_ART" if "rear" in key else "MISSING_FRONT_ART"
				)
				check(missing["view_id"] == entry[2], label + ": no fallback view")
				check(not missing["ready"], label + ": missing art blocks readiness")
				check(missing["missing_asset_keys"] == [key], label + ": missing key")
				check(missing["warnings"] == [warning], label + ": warning category")
				check(not missing["resolved_assets"].has(key), label + ": no substitute")

		var empty: Dictionary = Perspective.resolve(entry[0], entry[1])
		check(not empty["ready"], label + ": empty assets")
		check(empty["missing_asset_keys"] == entry[3], label + ": all missing")
		check(empty["warnings"].size() == 2, label + ": front and rear warnings")
		check(empty["resolved_assets"].is_empty(), label + ": no fabricated assets")

		# Mutating returned metadata must not alter later resolutions.
		result["required_asset_keys"].clear()
		result["resolved_assets"].clear()
		var fresh: Dictionary = Perspective.resolve(entry[0], entry[1], assets)
		check(fresh["required_asset_keys"] == entry[3], label + ": isolated result")

	for invalid in [["unknown", "attack"], ["hero", "unknown"], ["", ""]]:
		var result: Dictionary = Perspective.resolve(invalid[0], invalid[1], assets)
		check(result["view_id"] == "", "invalid request: no view")
		check(not result["ready"], "invalid request: not ready")
		check(result["warnings"] == ["INVALID_PERSPECTIVE"], "invalid request: warning")
		check(result["required_asset_keys"].is_empty(), "invalid request: no requirements")
		check(result["resolved_assets"].is_empty(), "invalid request: no assets")

	check(
		Perspective.resolve("hero")["view_id"] == "HERO_REAR_3Q",
		"default phase is attack"
	)
	if failures == 0:
		print("BATTLE_PERSPECTIVE_OK")
	quit(0 if failures == 0 else 1)
