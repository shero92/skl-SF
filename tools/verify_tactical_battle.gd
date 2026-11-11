extends SceneTree
## Headless check of the playable skirmish: player move/attack rules, enemy turns, a full battle ends, scene clicks.
## Agent: claude (Claude Code); model: Fable 5.2.

const Session = preload("res://scenes/battle/tactical_battle.gd")
const TEST_SAVE := "user://verify_tactical_hero.json"
var _failures := 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


## Simple player policy: attack when possible, otherwise step towards the nearest enemy.
func _play_turn(s) -> void:
	var ids: Array[String] = s.target_ids()
	if ids.is_empty():
		var me = s.current()
		var best: Vector2i = me.cell
		var best_distance := 9999
		for cell: Vector2i in s.move_cells():
			for enemy: Dictionary in s.manager.alive("enemy"):
				var d: int = absi(cell.x - enemy.cell.x) + absi(cell.y - enemy.cell.y)
				if d < best_distance:
					best_distance = d
					best = cell
		if best != me.cell:
			s.move(best)
		ids = s.target_ids()
	if ids.is_empty():
		s.wait()
	else:
		s.attack(ids[0])


func _initialize() -> void:
	var s = Session.new(7)
	_check(s.manager.combatants.size() == 6, "six combatants placed")
	_check(not s.is_over(), "battle starts running")
	var guard := 0
	while not s.is_player_turn() and guard < 10:
		_check(s.step_enemy(), "enemy steps while it is its turn")
		guard += 1
	_check(s.is_player_turn(), "player gets a turn")
	_check(not s.step_enemy(), "enemy cannot act on the player's turn")
	var me = s.current()
	var start: Vector2i = me.cell
	_check(not s.move(Vector2i(4, 2)), "cannot move onto a rock")
	_check(not s.attack("raider_a") or s.target_ids().has("raider_a"), "out-of-range attack is refused")
	var cells: Array[Vector2i] = s.move_cells()
	_check(cells.size() > 1, "player has cells to move to")
	var destination: Vector2i = cells[cells.size() - 1]
	_check(s.move(destination) and me.cell == destination, "player moves to a reachable cell")
	_check(s.move_cells().is_empty() and not s.move(start), "only one move per turn")
	_check(s.wait(), "player can wait")
	_check(s.current() == null or s.current().id != me.id or s.is_over(), "turn passes after waiting")
	# Whole battle with a simple policy must finish with a winner and a log.
	guard = 0
	while not s.is_over() and guard < 600:
		if s.is_player_turn():
			_play_turn(s)
		else:
			s.step_enemy()
		guard += 1
	_check(s.is_over(), "battle ends within the turn limit")
	_check(s.winner() == "player" or s.winner() == "enemy", "winner is one of the teams")
	_check(not s.log_lines.is_empty(), "attacks are logged")
	_check(not s.move(Vector2i(0, 0)) and not s.wait() and not s.step_enemy(), "no actions after the battle ends")
	# Same seed, same policy: identical log.
	var logs: Array = []
	for n in 2:
		var replay = Session.new(11)
		guard = 0
		while not replay.is_over() and guard < 600:
			if replay.is_player_turn():
				_play_turn(replay)
			else:
				replay.step_enemy()
			guard += 1
		logs.append(replay.log_lines)
	_check(logs[0] == logs[1] and not logs[0].is_empty(), "same seed replays identically")
	# Scene: builds, converts clicks to cells, and uses an isolated save file.
	var scene: Node = load("res://scenes/battle/tactical_battle.tscn").instantiate()
	scene.save_path = TEST_SAVE
	root.add_child(scene)
	await process_frame
	_check(scene.session != null, "scene creates a session")
	if scene.session == null:
		quit(1)
		return
	_check(scene.cell_at(scene.cell_rect(Vector2i(3, 2)).get_center()) == Vector2i(3, 2), "click maps back to its cell")
	while not scene.session.is_player_turn() and not scene.session.is_over():
		scene.session.step_enemy()
	var options: Array[Vector2i] = scene.session.move_cells()
	_check(scene.click_cell(options[options.size() - 1]), "clicking a blue cell moves the unit")
	_check(not scene.click_cell(Vector2i(4, 2)), "clicking a rock does nothing")
	# Attack playback: the scene queues the director, locks input, and the drawn hp follows the hit frame.
	scene.restart()
	var battle = scene.session
	while not battle.is_player_turn() and not battle.is_over():
		battle.step_enemy()
	while scene.is_animating():
		scene._process(0.05)
	var target_unit = battle.manager.alive("enemy")[0]
	var hero_unit = battle.current()
	for reach in [1, 2, 3]:  # melee, spear or bow: put the enemy at the first distance this weapon can hit
		var spot: Vector2i = hero_unit.cell + Vector2i(reach, 0)
		if battle.manager.occupant(spot) == null and not battle.manager.blocked.has(spot):
			target_unit.cell = spot
			if battle.target_ids().has(String(target_unit.id)):
				break
	var before: int = battle.hp(String(target_unit.id))
	_check(battle.target_ids().has(String(target_unit.id)), "adjacent enemy is a target")
	_check(scene.click_cell(target_unit.cell), "clicking the enemy attacks it")
	_check(scene.is_animating(), "an attack starts a playback")
	_check(int(scene._shown_hp[String(target_unit.id)]) == before, "drawn hp waits for the hit frame")
	_check(not scene.click_cell(Vector2i(0, 0)), "input is locked during the playback")
	var play_steps := 0
	while scene.is_animating() and play_steps < 400:
		scene._process(0.05)
		play_steps += 1
	_check(not scene.is_animating(), "playback ends")
	for c: Dictionary in battle.manager.combatants:
		_check(int(scene._shown_hp[String(c.id)]) == battle.hp(String(c.id)), "drawn hp equals real hp after playback: " + String(c.id))
	_check(scene._actors[String(hero_unit.id)].pose == "idle", "attacker returns to idle")
	scene.queue_free()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	if _failures == 0:
		print("TACTICAL_BATTLE_OK")
	quit(1 if _failures > 0 else 0)
