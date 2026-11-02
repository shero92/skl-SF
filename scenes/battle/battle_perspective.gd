extends RefCounted
## Battle-only perspective metadata. No sprite transforms or art substitution.
##
## "attack" selects the attacking side's presentation.
## "defend" selects that side's defensive presentation.
## Asset keys identify authored views; callers provide a key -> resource map.
## An absent or null resource remains unavailable and is never substituted.

const HERO_REAR_3Q = "HERO_REAR_3Q"
const HERO_FRONT = "HERO_FRONT"
const MONSTER_REAR = "MONSTER_REAR"

const MISSING_REAR_ART = "MISSING_REAR_ART"
const MISSING_FRONT_ART = "MISSING_FRONT_ART"
const INVALID_PERSPECTIVE = "INVALID_PERSPECTIVE"

const VIEWS = {
	HERO_REAR_3Q: {
		"required_asset_keys": ["hero_rear_3q", "monster_front"],
	},
	HERO_FRONT: {
		"required_asset_keys": ["hero_front", "monster_rear"],
	},
	MONSTER_REAR: {
		"required_asset_keys": ["monster_rear", "hero_front"],
	},
}

const PERSPECTIVES = {
	"hero": {
		"attack": HERO_REAR_3Q,
		"defend": HERO_FRONT,
	},
	"monster": {
		"attack": HERO_FRONT,
		"defend": MONSTER_REAR,
	},
}

const MISSING_ART_WARNINGS = {
	"hero_rear_3q": MISSING_REAR_ART,
	"monster_rear": MISSING_REAR_ART,
	"hero_front": MISSING_FRONT_ART,
	"monster_front": MISSING_FRONT_ART,
}


static func resolve(
	attacker_kind: String,
	phase: String = "attack",
	assets: Dictionary = {}
) -> Dictionary:
	## Returns fresh collections so callers cannot mutate the mapping tables.
	## Warnings are returned as data; callers decide how to display or log them.
	var result: Dictionary = {
		"view_id": "",
		"required_asset_keys": [],
		"resolved_assets": {},
		"missing_asset_keys": [],
		"warnings": [],
		"ready": false,
	}
	if not PERSPECTIVES.has(attacker_kind):
		result["warnings"].append(INVALID_PERSPECTIVE)
		return result
	var phases: Dictionary = PERSPECTIVES[attacker_kind]
	if not phases.has(phase):
		result["warnings"].append(INVALID_PERSPECTIVE)
		return result

	var view_id: String = phases[phase]
	result["view_id"] = view_id
	result["required_asset_keys"] = VIEWS[view_id]["required_asset_keys"].duplicate()
	for key in result["required_asset_keys"]:
		if assets.has(key) and assets[key] != null:
			result["resolved_assets"][key] = assets[key]
		else:
			result["missing_asset_keys"].append(key)
			var warning: String = MISSING_ART_WARNINGS[key]
			if not result["warnings"].has(warning):
				result["warnings"].append(warning)
	result["ready"] = result["missing_asset_keys"].is_empty()
	return result
