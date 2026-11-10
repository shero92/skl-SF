extends SceneTree
## Headless verification of the grid TurnManager. Agent: claude (Claude Code); model: Sonnet 5.5.

const Manager = preload("res://scenes/battle/turn_manager.gd")
const Resolver = preload("res://scenes/battle/battle_resolver.gd")

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	_test_order_and_move()
	_test_attack_and_counter()
	_test_victory()
	if _failures == 0:
		print("TURN_MANAGER_OK")
	quit(0 if _failures == 0 else 1)


func _setup(seed_value: int = 1):
	var m = Manager.new(Resolver.new(null, seed_value))
	var ws = m.resolver.weapons
	m.add("hero", "player", ws.make_unit("CHAR001", ["WPN_IRON_SWORD"], "WPN_IRON_SWORD"), Vector2i(2, 2))
	m.add("archer", "player", ws.make_unit("CHAR006", ["WPN_SHORT_BOW"], "WPN_SHORT_BOW"), Vector2i(0, 2))
	m.add("foe", "enemy", ws.make_unit("CHAR004", [], ""), Vector2i(6, 2))
	return m


func _test_order_and_move() -> void:
	var m = _setup()
	_check(not m.add("dup", "enemy", {}, Vector2i(2, 2)), "occupied cell rejected")
	m.start_round()
	_check(m.order == ["archer", "hero", "foe"], "agility order, got %s" % str(m.order))
	var archer = m.current()
	_check(archer.id == "archer", "archer first")
	_check(not m.move_to(m.find("hero"), Vector2i(3, 2)), "only current may move")
	var cells: Array = m.reachable(archer)
	_check(cells.has(Vector2i(0, 2)) and cells.has(Vector2i(3, 3)) and not cells.has(Vector2i(2, 2)), "reachable respects move and allies")
	_check(not cells.has(Vector2i(6, 2)), "enemy cell excluded")
	m.blocked[Vector2i(0, 3)] = true
	_check(not m.reachable(archer).has(Vector2i(0, 3)), "blocked excluded")
	_check(m.move_to(archer, Vector2i(1, 3)) and archer.cell == Vector2i(1, 3), "move")
	_check(not m.move_to(archer, Vector2i(0, 2)), "one move per turn")
	m.end_turn()
	_check(m.current().id == "hero", "next turn hero")
	m.end_turn()
	m.end_turn()
	_check(m.round_number == 2 and m.current().id == "archer", "new round")


func _test_attack_and_counter() -> void:
	var m = _setup(5)
	m.find("foe").cell = Vector2i(4, 2)
	m.start_round()
	var archer = m.current()
	var foe = m.find("foe")
	_check(not m.attack(archer, foe).ok, "foe at distance 4 is out of bow range")
	m.move_to(archer, Vector2i(1, 2))
	var counters: Array = []
	m.attacked.connect(func(_a, _d, res, counter): counters.append([res, counter]))
	var res: Dictionary = m.attack(archer, foe)
	_check(res.ok, "bow attack at distance 3")
	_check(counters.size() == 1 and counters[0][1].is_empty(), "melee foe cannot counter at range 3")
	_check(not m.attack(archer, foe).ok, "one attack per turn")
	m.end_turn()
	var hero = m.current()
	_check(hero.id == "hero", "hero turn")
	m.move_to(hero, Vector2i(3, 2))
	m.attack(hero, foe)
	_check(counters.size() == 2, "second attack reported")
	if foe.unit.hp > 0:
		_check(not counters[1][1].is_empty() and counters[1][1].ok, "adjacent foe counter-attacks")


func _test_victory() -> void:
	var m = _setup(2)
	m.find("foe").unit.hp = 1
	m.find("foe").cell = Vector2i(3, 2)
	var ended: Array = []
	m.battle_ended.connect(func(team): ended.append(team))
	m.start_round()
	for i in 12:
		if m.winner != "":
			break
		var c = m.current()
		if c.id == "hero":
			m.attack(c, m.find("foe"))
		m.end_turn()
	_check(m.winner == "player" and ended == ["player"], "player wins, got '%s'" % m.winner)
