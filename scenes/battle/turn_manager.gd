extends RefCounted
## Grid turn manager: initiative by agility, move (BFS), attack with counter-attack, victory.
## Agent: claude (Claude Code); model: Sonnet 5.5.
## Pure data on top of BattleResolver; no scenes. Combatants are {id, team, unit, cell, moved, acted}.

signal turn_started(id: String)
signal attacked(attacker_id: String, defender_id: String, result: Dictionary, counter: Dictionary)
signal battle_ended(winner_team: String)

const Resolver = preload("res://scenes/battle/battle_resolver.gd")

var resolver
var combatants: Array[Dictionary] = []
var blocked: Dictionary = {} # Vector2i -> true (walls, water)
var bounds := Rect2i(0, 0, 16, 16)
var order: Array[String] = []
var turn_index: int = -1
var round_number: int = 0
var winner: String = ""


func _init(battle_resolver = null) -> void:
	resolver = battle_resolver if battle_resolver != null else Resolver.new()


func add(id: String, team: String, unit: Dictionary, cell: Vector2i) -> bool:
	if find(id) != null or not bounds.has_point(cell) or blocked.has(cell) or occupant(cell) != null:
		return false
	combatants.append({"id": id, "team": team, "unit": unit, "cell": cell, "moved": false, "acted": false})
	return true


func find(id: String):
	for c in combatants:
		if c.id == id:
			return c
	return null


func occupant(cell: Vector2i):
	for c in combatants:
		if c.cell == cell and not resolver.is_defeated(c.unit):
			return c
	return null


func alive(team: String = "") -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for c in combatants:
		if not resolver.is_defeated(c.unit) and (team == "" or c.team == team):
			result.append(c)
	return result


## Starts a new round: living combatants sorted by agility (high first, ties keep insertion order).
func start_round() -> void:
	round_number += 1
	var living := alive()
	var keyed: Array = []
	for i in living.size():
		keyed.append([-int(resolver.weapons.effective_stats(living[i].unit).get("agility", 0)), i, living[i].id])
	keyed.sort()
	order.clear()
	for k in keyed:
		order.append(k[2])
	for c in combatants:
		c.moved = false
		c.acted = false
	turn_index = -1
	next_turn()


func current():
	return find(order[turn_index]) if turn_index >= 0 and turn_index < order.size() else null


## Advances to the next living combatant; starts a new round when everyone has acted.
func next_turn() -> void:
	if winner != "":
		return
	turn_index += 1
	while turn_index < order.size() and resolver.is_defeated(find(order[turn_index]).unit):
		turn_index += 1
	if turn_index >= order.size():
		start_round()
		return
	turn_started.emit(order[turn_index])


## Cells the combatant can reach: BFS over free cells within its move stat (can pass allies, not enemies).
func reachable(c: Dictionary) -> Array[Vector2i]:
	var move := int(resolver.weapons.effective_stats(c.unit).get("move", 0))
	var seen := {c.cell: 0}
	var queue: Array[Vector2i] = [c.cell]
	var result: Array[Vector2i] = []
	while not queue.is_empty():
		var cell: Vector2i = queue.pop_front()
		if occupant(cell) == null or cell == c.cell:
			result.append(cell)
		if seen[cell] >= move:
			continue
		for d in [Vector2i.LEFT, Vector2i.RIGHT, Vector2i.UP, Vector2i.DOWN]:
			var next: Vector2i = cell + d
			if seen.has(next) or not bounds.has_point(next) or blocked.has(next):
				continue
			var other = occupant(next)
			if other != null and other.team != c.team:
				continue
			seen[next] = seen[cell] + 1
			queue.append(next)
	return result


func move_to(c: Dictionary, cell: Vector2i) -> bool:
	if c != current() or c.moved or c.acted or not reachable(c).has(cell):
		return false
	c.cell = cell
	c.moved = true
	return true


## Living enemies the combatant can attack from where it stands.
func targets(c: Dictionary) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for other in alive():
		if other.team != c.team and resolver.can_target(c.unit, c.cell, other.cell):
			result.append(other)
	return result


## Attack; a surviving defender that can reach back counter-attacks. Ends the actor's action.
func attack(c: Dictionary, target: Dictionary) -> Dictionary:
	if c != current() or c.acted or not targets(c).has(target):
		return {"ok": false, "reason": "invalid_attack"}
	var result: Dictionary = resolver.resolve(c.unit, target.unit, c.cell, target.cell)
	c.acted = true
	var counter := {}
	if not result.defeated and resolver.can_target(target.unit, target.cell, c.cell):
		counter = resolver.resolve(target.unit, c.unit, target.cell, c.cell)
	attacked.emit(c.id, target.id, result, counter)
	_check_victory()
	return result


func end_turn() -> void:
	if current() != null:
		current().acted = true
	next_turn()


func _check_victory() -> void:
	var teams := {}
	for c in alive():
		teams[c.team] = true
	if teams.size() <= 1:
		winner = String(teams.keys()[0]) if teams.size() == 1 else "none"
		battle_ended.emit(winner)
