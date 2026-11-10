extends SceneTree
## Headless verification of EnemyAI. Agent: claude (Claude Code); model: Sonnet 5.5.

const Manager = preload("res://scenes/battle/turn_manager.gd")
const Resolver = preload("res://scenes/battle/battle_resolver.gd")
const AI = preload("res://scenes/battle/enemy_ai.gd")

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	_test_approach()
	_test_attack_choice()
	_test_full_battle()
	if _failures == 0:
		print("ENEMY_AI_OK")
	quit(0 if _failures == 0 else 1)


func _manager(seed_value: int = 1):
	return Manager.new(Resolver.new(null, seed_value))


func _test_approach() -> void:
	var m = _manager()
	var ws = m.resolver.weapons
	m.add("hero", "player", ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD"), Vector2i(0, 0))
	m.add("brute", "enemy", ws.make_unit("CHAR004", ["WPN_BATTLE_AXE"], "WPN_BATTLE_AXE"), Vector2i(12, 0))
	m.add("shooter", "enemy", ws.make_unit("CHAR006", ["WPN_LONG_BOW"], "WPN_LONG_BOW"), Vector2i(0, 12))
	var ai = AI.new()
	var brute = m.find("brute")
	var plan: Dictionary = ai.plan(m, brute)
	_check(plan.target_id == "", "far enemy cannot attack yet")
	_check(plan.move_to.x < 12 and plan.move_to.y == 0, "brute approaches, got %s" % str(plan.move_to))
	var shooter = m.find("shooter")
	var plan2: Dictionary = ai.plan(m, shooter)
	_check(plan2.move_to.y < 12, "shooter approaches")
	_check(m.find("brute").cell == Vector2i(12, 0), "plan is read-only")


func _test_attack_choice() -> void:
	var m = _manager()
	var ws = m.resolver.weapons
	m.add("tank", "player", ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD"), Vector2i(3, 3))
	m.add("mage", "player", ws.make_unit("CHAR005", ["WPN_WOOD_STAFF"], "WPN_WOOD_STAFF"), Vector2i(5, 3))
	m.add("brute", "enemy", ws.make_unit("CHAR004", ["WPN_BATTLE_AXE"], "WPN_BATTLE_AXE"), Vector2i(4, 7))
	var ai = AI.new()
	var plan: Dictionary = ai.plan(m, m.find("brute"))
	_check(plan.target_id == "mage", "prefers the likely kill / weakest target, got %s" % plan.target_id)
	m.find("mage").unit.hp = 999
	var plan2: Dictionary = ai.plan(m, m.find("brute"))
	_check(plan2.target_id != "", "still attacks something")


func _test_full_battle() -> void:
	var m = _manager(11)
	var ws = m.resolver.weapons
	m.add("hero", "player", ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD"), Vector2i(2, 5))
	m.add("archer", "player", ws.make_unit("CHAR006", ["WPN_SHORT_BOW"], "WPN_SHORT_BOW"), Vector2i(1, 6))
	m.add("brute", "enemy", ws.make_unit("CHAR004", ["WPN_BATTLE_AXE"], "WPN_BATTLE_AXE"), Vector2i(9, 5))
	m.add("thief", "enemy", ws.make_unit("CHAR001", ["WPN_ASSASSIN_DAGGER"], "WPN_ASSASSIN_DAGGER"), Vector2i(9, 6))
	var ai = AI.new()
	m.start_round()
	var turns := 0
	while m.winner == "" and turns < 200:
		ai.act(m, m.current())
		turns += 1
	_check(m.winner != "", "both sides AI-controlled battle ends (%d turns)" % turns)
	_check(turns < 200, "battle terminates")
