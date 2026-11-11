extends RefCounted
## Glue between the battle rules and the animation controller: TurnManager decides, the controller plays.
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## attack() resolves immediately through TurnManager (data is final) and queues the visual playback of the
## attack and of a counter-attack; advance(delta) plays the queue one controller attack at a time. The
## controller's hit frame fires hit_landed so a UI can show damage exactly when the blow connects.
## Actors implement set_view(view), set_frame(name, index), reset() (ModularActorAdapter does).

signal playback_started(entry: Dictionary)
signal hit_landed(entry: Dictionary)
signal playback_finished(entry: Dictionary)
signal queue_empty

const Controller = preload("res://scenes/battle/battle_animation_controller.gd")

## art profile (WeaponSystem.art_profile) -> attack id.
const ATTACK_FOR_PROFILE := {"sword": &"slash", "axe": &"slash", "natural": &"slash", "spear": &"thrust", "bow": &"shoot", "staff": &"cast"}
## attack id -> frames [duration_ms, phase, hit, attacker pose, defender pose]
const ATTACKS := {
	&"slash": [[120, "Attack", false, "windup", "idle"], [80, "Attack", true, "strike", "hurt"], [160, "Recovery", false, "recover", "idle"]],
	&"thrust": [[100, "Attack", false, "windup", "idle"], [60, "Attack", true, "strike", "hurt"], [140, "Recovery", false, "recover", "idle"]],
	&"shoot": [[200, "Attack", false, "draw", "idle"], [60, "Attack", true, "release", "hurt"], [160, "Recovery", false, "recover", "idle"]],
	&"cast": [[240, "Attack", false, "cast", "idle"], [80, "Attack", true, "cast_release", "hurt"], [200, "Recovery", false, "recover", "idle"]],
}

var manager
var controller = Controller.new()
var actors: Dictionary = {}
var queue: Array[Dictionary] = []
var current: Dictionary = {}
var skipped: Array[Dictionary] = []


func _init(turn_manager) -> void:
	manager = turn_manager
	for attack_id: StringName in ATTACKS:
		var frames: Array = []
		for row: Array in ATTACKS[attack_id]:
			frames.append({"duration_ms": row[0], "phase": row[1], "hit": row[2],
				"attacker": {"view": "side", "name": row[3], "index": 0},
				"defender": {"view": "side", "name": row[4], "index": 0}})
		controller.attacks[attack_id] = {"frames": frames, "assets": []}
	controller.hit.connect(_on_hit)


func register_actor(id: String, actor) -> void:
	actors[id] = actor


func is_busy() -> bool:
	return not current.is_empty() or not queue.is_empty()


func attack_id_for(combatant_id: String) -> StringName:
	var combatant = manager.find(combatant_id)
	var profile: String = manager.resolver.weapons.art_profile(combatant.unit)
	return ATTACK_FOR_PROFILE.get(profile, &"slash")


## Resolves the attack now and queues its animations. Returns the TurnManager result.
func attack(attacker_id: String, defender_id: String) -> Dictionary:
	var attacker = manager.find(attacker_id)
	var defender = manager.find(defender_id)
	if attacker == null or defender == null:
		return {"ok": false, "reason": "unknown_combatant"}
	var counters: Array = []
	var catcher := func(_a, _d, _result, counter): counters.append(counter)
	manager.attacked.connect(catcher)
	var result: Dictionary = manager.attack(attacker, defender)
	manager.attacked.disconnect(catcher)
	if not result.ok:
		return result
	queue.append({"attack_id": attack_id_for(attacker_id), "attacker_id": attacker_id, "defender_id": defender_id,
		"result": result, "counter": false})
	if not counters.is_empty() and not counters[0].is_empty():
		queue.append({"attack_id": attack_id_for(defender_id), "attacker_id": defender_id, "defender_id": attacker_id,
			"result": counters[0], "counter": true})
	return result


func advance(delta_seconds: float) -> void:
	if current.is_empty():
		if queue.is_empty():
			return
		current = queue.pop_front()
		var attacker = actors.get(current.attacker_id)
		var defender = actors.get(current.defender_id)
		var started: Dictionary = {"ok": false}
		if attacker != null and defender != null:
			started = controller.play_attack(current.attack_id, attacker, defender)
		if not started.ok:
			# No actor or asset for this fight: the result stays valid, only the animation is skipped.
			skipped.append(current)
			var entry := current
			current = {}
			playback_started.emit(entry)
			hit_landed.emit(entry)
			playback_finished.emit(entry)
			if queue.is_empty():
				queue_empty.emit()
			return
		playback_started.emit(current)
		return
	controller.advance(delta_seconds)
	if controller.state == Controller.State.IDLE:
		var finished := current
		current = {}
		playback_finished.emit(finished)
		if queue.is_empty():
			queue_empty.emit()


func _on_hit(_attack_id, _attacker, _defender) -> void:
	hit_landed.emit(current)
