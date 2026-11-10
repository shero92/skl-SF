extends RefCounted
## Simple deterministic enemy AI for TurnManager: best attack from any reachable cell, else approach.
## Agent: claude (Claude Code); model: Sonnet 5.5.
## plan() is read-only and returns {move_to: Vector2i, target_id: String}; act() executes it and ends the turn.

const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")


## Expected value of attacking `target` from `cell` (higher is better).
func _score(manager, c: Dictionary, cell: Vector2i, target: Dictionary) -> float:
	var resolver = manager.resolver
	var damage: int = resolver.weapons.damage(c.unit, target.unit)
	var chance: float = resolver.weapons.hit_chance(c.unit, target.unit) / 100.0
	var score: float = damage * chance
	if damage >= resolver.current_hp(target.unit):
		score += 1000.0 * chance # a likely kill beats everything
	score += 10.0 - resolver.current_hp(target.unit) * 0.1 # prefer weakened targets
	if resolver.can_target(target.unit, target.cell, cell):
		score -= 5.0 # avoid counter-attacks when an equal option exists
	return score


func plan(manager, c: Dictionary) -> Dictionary:
	var resolver = manager.resolver
	var enemies: Array = []
	for other in manager.alive():
		if other.team != c.team:
			enemies.append(other)
	if enemies.is_empty():
		return {"move_to": c.cell, "target_id": ""}
	var best_score := -INF
	var best := {}
	for cell in manager.reachable(c):
		for target in enemies:
			if not resolver.can_target(c.unit, cell, target.cell):
				continue
			var score := _score(manager, c, cell, target)
			if score > best_score:
				best_score = score
				best = {"move_to": cell, "target_id": target.id}
	if not best.is_empty():
		return best
	return {"move_to": _approach_cell(manager, c, enemies), "target_id": ""}


## No attack possible: step toward the nearest enemy, stopping at the weapon's ideal range.
func _approach_cell(manager, c: Dictionary, enemies: Array) -> Vector2i:
	var nearest: Dictionary = enemies[0]
	for other in enemies:
		if WeaponSystem.grid_distance(c.cell, other.cell) < WeaponSystem.grid_distance(c.cell, nearest.cell):
			nearest = other
	var ideal := int(manager.resolver.weapons.attack_range(c.unit).max)
	var best_cell: Vector2i = c.cell
	var best_gap := absi(WeaponSystem.grid_distance(c.cell, nearest.cell) - ideal)
	for cell in manager.reachable(c):
		var gap := absi(WeaponSystem.grid_distance(cell, nearest.cell) - ideal)
		if gap < best_gap:
			best_gap = gap
			best_cell = cell
	return best_cell


## Plays the current combatant's whole turn. Returns the plan with the attack result.
func act(manager, c: Dictionary) -> Dictionary:
	var decision := plan(manager, c)
	if decision.move_to != c.cell:
		manager.move_to(c, decision.move_to)
	if decision.target_id != "":
		decision["result"] = manager.attack(c, manager.find(decision.target_id))
	manager.end_turn()
	return decision
