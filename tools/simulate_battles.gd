extends SceneTree
## Weapon/class balance simulation: every class (with its best tier<=2 weapon) fights every class 1v1 with the real
## TurnManager, BattleResolver and EnemyAI on an open 12x8 grid, many seeds. Prints one JSON report.
## Usage: godot --headless --path . --script res://tools/simulate_battles.gd -- [seeds=20] [max_turns=60]
## Agent: claude (Claude Code); model: Sonnet 5.5. Informational: the numbers are the owner's to tune.

const Manager = preload("res://scenes/battle/turn_manager.gd")
const Resolver = preload("res://scenes/battle/battle_resolver.gd")
const AI = preload("res://scenes/battle/enemy_ai.gd")
const WeaponSystemScript = preload("res://scenes/battle/weapon_system.gd")


static func best_weapon(ws, class_id: String, max_tier: int = 2) -> String:
	var best := ""
	var best_attack := -1
	for weapon_id: String in ws.data.weapons:
		var item: Dictionary = ws.data.weapons[weapon_id]
		if bool(item.get("builtin", false)) or int(item.get("tier", 0)) > max_tier or not ws.can_equip(class_id, weapon_id):
			continue
		if int(item.attack) > best_attack:
			best_attack = int(item.attack)
			best = weapon_id
	return best


static func make_class_unit(ws, class_id: String) -> Dictionary:
	var unit := {"class_id": class_id, "character_id": "", "stat_offsets": {}, "weapon_id": "", "inventory": []}
	var weapon_id := best_weapon(ws, class_id)
	if weapon_id != "":
		unit.inventory.append(weapon_id)
		ws.equip(unit, weapon_id)
	return unit


## Returns "a", "b" or "draw" and the number of rounds played.
static func duel(class_a: String, class_b: String, seed_value: int, max_turns: int) -> Dictionary:
	var manager = Manager.new(Resolver.new(null, seed_value))
	var ws = manager.resolver.weapons
	manager.bounds = Rect2i(0, 0, 12, 8)
	manager.add("a", "a", make_class_unit(ws, class_a), Vector2i(2, 3))
	manager.add("b", "b", make_class_unit(ws, class_b), Vector2i(9, 3))
	manager.start_round()
	var ai = AI.new()
	var turns := 0
	while manager.winner == "" and turns < max_turns:
		ai.act(manager, manager.current())
		turns += 1
	return {"winner": manager.winner if manager.winner != "" else "draw", "rounds": manager.round_number}


static func run(seeds: int, max_turns: int) -> Dictionary:
	var ws = WeaponSystemScript.load_default()
	var classes: Array = ws.data.classes.keys()
	classes.sort()
	var matrix := {}
	var totals := {}
	var draws := 0
	var battles := 0
	var rounds := 0
	for class_a: String in classes:
		matrix[class_a] = {}
		totals[class_a] = {"wins": 0, "games": 0}
		for class_b: String in classes:
			var wins := 0
			for seed_value in seeds:
				# Alternate sides by seed parity so the starting position cannot decide the matchup.
				var swap := seed_value % 2 == 1
				var outcome := duel(class_b if swap else class_a, class_a if swap else class_b, seed_value, max_turns)
				battles += 1
				rounds += int(outcome.rounds)
				if outcome.winner == "draw":
					draws += 1
				elif (outcome.winner == "a") != swap:
					wins += 1
			matrix[class_a][class_b] = snappedf(float(wins) / seeds, 0.01)
			totals[class_a].games += seeds
			totals[class_a].wins += wins
	var summary := {}
	for class_id: String in classes:
		summary[class_id] = {"weapon": best_weapon(ws, class_id), "win_rate": snappedf(float(totals[class_id].wins) / totals[class_id].games, 0.01)}
	return {"seeds": seeds, "max_turns": max_turns, "battles": battles, "draw_rate": snappedf(float(draws) / battles, 0.001),
		"avg_rounds": snappedf(float(rounds) / battles, 0.1), "summary": summary, "matrix": matrix}


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var seeds: int = int(args[0]) if args.size() > 0 else 20
	var max_turns: int = int(args[1]) if args.size() > 1 else 60
	print("SIMULATION_REPORT " + JSON.stringify(run(seeds, max_turns)))
	quit(0)
