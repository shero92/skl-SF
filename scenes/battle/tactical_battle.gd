extends RefCounted
## Playable grid battle session: the player commands one team, EnemyAI the other.
## Agent: claude (Claude Code); model: Fable 5.2.
## Pure rules on top of TurnManager (no nodes), so the same session drives the scene and the headless test.

signal changed
signal message(text: String)

const WeaponSystem = preload("res://scenes/battle/weapon_system.gd")
const Resolver = preload("res://scenes/battle/battle_resolver.gd")
const TurnManager = preload("res://scenes/battle/turn_manager.gd")
const EnemyAI = preload("res://scenes/battle/enemy_ai.gd")

const PLAYER := "player"
const ENEMY := "enemy"
const SIZE := Vector2i(10, 7)
## Default skirmish: [id, team, character, weapon, cell]. Hero's party on the left, raiders on the right.
const ROSTER := [
	["hero", PLAYER, "CHAR001", "WPN_IRON_SWORD", Vector2i(1, 3)],
	["cely", PLAYER, "CHAR002", "WPN_BRONZE_SPEAR", Vector2i(1, 1)],
	["archer", PLAYER, "CHAR006", "WPN_SHORT_BOW", Vector2i(0, 5)],
	["raider_a", ENEMY, "CHAR004", "WPN_HAND_AXE", Vector2i(8, 3)],
	["raider_b", ENEMY, "CHAR003", "", Vector2i(8, 1)],
	["raider_c", ENEMY, "CHAR006", "WPN_SHORT_BOW", Vector2i(9, 5)],
]
const ROCKS := [Vector2i(4, 2), Vector2i(5, 2), Vector2i(4, 5), Vector2i(5, 4)]

var weapons
var manager
var ai = EnemyAI.new()
var log_lines: Array[String] = []


func _init(seed_value: int = 1, hero_unit: Dictionary = {}) -> void:
	weapons = WeaponSystem.load_default()
	manager = TurnManager.new(Resolver.new(weapons, seed_value))
	manager.bounds = Rect2i(Vector2i.ZERO, SIZE)
	for cell: Vector2i in ROCKS:
		manager.blocked[cell] = true
	for row: Array in ROSTER:
		var unit: Dictionary = weapons.make_unit(row[2], [], row[3])
		if row[0] == "hero" and not hero_unit.is_empty():
			unit = hero_unit.duplicate(true)  # the hero fights with the weapon equipped in the room
			unit.erase("hp")
		manager.add(row[0], row[1], unit, row[4])
	manager.attacked.connect(_on_attacked)
	manager.start_round()


func current():
	return manager.current()


func winner() -> String:
	return manager.winner


func is_over() -> bool:
	return manager.winner != ""


func is_player_turn() -> bool:
	var c = current()
	return not is_over() and c != null and c.team == PLAYER


func display_name(id: String) -> String:
	var c = manager.find(id)
	var entry: Dictionary = weapons.data.get("characters", {}).get(String(c.unit.character_id), {})
	return String(entry.get("name", id)) if c.team == PLAYER else id.capitalize()


func hp(id: String) -> int:
	return manager.resolver.current_hp(manager.find(id).unit)


func max_hp(id: String) -> int:
	return int(weapons.effective_stats(manager.find(id).unit).get("hp", 1))


## Cells the acting player unit may move to (empty once it has moved or acted).
func move_cells() -> Array[Vector2i]:
	var c = current()
	if not is_player_turn() or c.moved or c.acted:
		return []
	return manager.reachable(c)


func target_ids() -> Array[String]:
	var ids: Array[String] = []
	if is_player_turn() and not current().acted:
		for t: Dictionary in manager.targets(current()):
			ids.append(t.id)
	return ids


func move(cell: Vector2i) -> bool:
	if not is_player_turn() or not manager.move_to(current(), cell):
		return false
	changed.emit()
	return true


## Player attack; the turn ends after it.
func attack(target_id: String) -> bool:
	if not is_player_turn() or not target_ids().has(target_id):
		return false
	manager.attack(current(), manager.find(target_id))
	_finish_turn()
	return true


func wait() -> bool:
	if not is_player_turn():
		return false
	_finish_turn()
	return true


## Plays one enemy turn. Returns false when it is not the enemy's turn.
func step_enemy() -> bool:
	var c = current()
	if is_over() or c == null or c.team == PLAYER:
		return false
	if manager.winner == "":
		ai.act(manager, c)
	changed.emit()
	return true


func _finish_turn() -> void:
	if not is_over():
		manager.end_turn()
	changed.emit()


func _describe(attacker_id: String, defender_id: String, result: Dictionary) -> String:
	var text := "%s -> %s: " % [display_name(attacker_id), display_name(defender_id)]
	if not result.hit:
		return text + "miss"
	text += "%d%s" % [int(result.damage), " critical" if result.critical else ""]
	return text + (", defeated" if result.defeated else "")


func _on_attacked(attacker_id: String, defender_id: String, result: Dictionary, counter: Dictionary) -> void:
	_say(_describe(attacker_id, defender_id, result))
	if not counter.is_empty():
		_say("counter " + _describe(defender_id, attacker_id, counter))
	if is_over():
		_say("Victory" if manager.winner == PLAYER else "Defeat")


func _say(text: String) -> void:
	log_lines.append(text)
	message.emit(text)
