extends RefCounted
## Explicitly advanced animation controller; no damage or character dependencies.
## Agent: codex; model: GPT-6.
##
## Populate attacks with attack_id -> {frames: [...], assets: [resource paths]}.
## Each frame has duration_ms, optional hit: true, phase: "Attack"/"Recovery",
## and optional attacker/defender poses {view, name, index}. Recovery is required.
## Actors implement set_view(view), set_frame(name, index), reset().
## play_attack while active returns BUSY without replacing the current attack.

signal started(attack_id: StringName, attacker, defender)
signal hit(attack_id: StringName, attacker, defender)
signal finished(attack_id: StringName, attacker, defender)
signal cancelled(attack_id: StringName, attacker, defender)

const Timeline = preload("res://scenes/battle/battle_timeline.gd")

enum State { IDLE, ATTACK, RECOVERY }

var state: State = State.IDLE
var attacks: Dictionary = {}

var _timeline
var _frames: Array[Dictionary] = []
var _attacker
var _defender
var _attack_id: StringName
var _generation: int = 0
var _resetting: bool = false


func play_attack(attack_id: StringName, attacker, defender) -> Dictionary:
	if state != State.IDLE or _resetting:
		return {"ok": false, "reason": "BUSY"}
	if not attacks.has(attack_id):
		return {"ok": false, "reason": "MISSING_ATTACK"}
	if not _valid_actor(attacker) or not _valid_actor(defender):
		return {"ok": false, "reason": "INVALID_ACTOR"}
	var definition: Variant = attacks[attack_id]
	if not definition is Dictionary:
		return {"ok": false, "reason": "INVALID_ATTACK"}
	var assets: Variant = definition.get("assets", [])
	if not assets is Array:
		return {"ok": false, "reason": "INVALID_ATTACK"}
	for asset in assets:
		if not asset is String or asset.is_empty() or not ResourceLoader.exists(asset):
			return {"ok": false, "reason": "MISSING_ASSET"}
	var source: Variant = definition.get("frames", [])
	if not source is Array or source.is_empty():
		return {"ok": false, "reason": "INVALID_ATTACK"}
	var frames: Array[Dictionary] = []
	var clock_frames: Array[Dictionary] = []
	var recovery := false
	for index in range(source.size()):
		var frame: Variant = source[index]
		if not frame is Dictionary:
			return {"ok": false, "reason": "INVALID_ATTACK"}
		var duration: Variant = frame.get("duration_ms")
		if not (duration is int or duration is float):
			return {"ok": false, "reason": "INVALID_ATTACK"}
		if not is_finite(float(duration)) or float(duration) <= 0.0:
			return {"ok": false, "reason": "INVALID_ATTACK"}
		var phase: Variant = frame.get("phase", "Attack")
		if phase != "Attack" and phase != "Recovery":
			return {"ok": false, "reason": "INVALID_ATTACK"}
		if index == 0 and phase != "Attack":
			return {"ok": false, "reason": "INVALID_ATTACK"}
		if recovery and phase != "Recovery":
			return {"ok": false, "reason": "INVALID_ATTACK"}
		recovery = phase == "Recovery"
		if not frame.get("hit", false) is bool:
			return {"ok": false, "reason": "INVALID_ATTACK"}
		for role in ["attacker", "defender"]:
			if frame.has(role) and not _valid_pose(frame[role]):
				return {"ok": false, "reason": "INVALID_ATTACK"}
		frames.append(frame.duplicate(true))
		clock_frames.append({"duration_ms": duration, "events": [str(index)]})
	if not recovery:
		return {"ok": false, "reason": "INVALID_ATTACK"}
	var timeline = Timeline.new()
	if not timeline.configure(clock_frames):
		return {"ok": false, "reason": "INVALID_ATTACK"}
	_generation += 1
	var generation := _generation
	_frames = frames
	_timeline = timeline
	_attacker = attacker
	_defender = defender
	_attack_id = attack_id
	state = State.ATTACK
	timeline.event_fired.connect(
		func(event): _on_frame(int(str(event)), generation)
	)
	timeline.restart()
	started.emit(attack_id, attacker, defender)
	# A started listener may cancel/reset or start a different attack.
	if generation == _generation:
		_on_frame(0, generation, false)
	return {"ok": true, "reason": "OK"}


func advance(delta_seconds: float) -> void:
	if state == State.IDLE or _resetting:
		return
	if not _timeline.playing:
		return
	var generation := _generation
	var timeline = _timeline
	timeline.advance(delta_seconds)
	if generation == _generation and timeline.position_ms >= timeline.duration_ms:
		_end(false)


func pause() -> void:
	if _timeline != null:
		_timeline.pause()


func resume() -> void:
	if _timeline != null:
		_timeline.resume()


func set_speed(value: float) -> bool:
	return _timeline.set_speed(value) if _timeline != null else false


func seek(time_ms: float) -> void:
	if _timeline == null or not is_finite(time_ms):
		return
	_timeline.seek(time_ms)
	# Scrubbing updates poses but never dispatches a gameplay hit.
	_on_frame(_timeline.frame_index, _generation, false)


func step_frame() -> void:
	if _timeline != null:
		_timeline.step_frame()
		_on_frame(_timeline.frame_index, _generation, false)


func get_position_ms() -> float:
	return _timeline.position_ms if _timeline != null else 0.0


func get_frame_index() -> int:
	return _timeline.frame_index if _timeline != null else 0


func is_playing() -> bool:
	return _timeline != null and _timeline.playing


func cancel() -> void:
	if state != State.IDLE and not _resetting:
		_end(true)


func reset() -> void:
	# Idle reset is idempotent; active reset has the same signal contract as cancel.
	cancel()


func _valid_actor(actor: Variant) -> bool:
	return (
		actor is Object and is_instance_valid(actor)
		and actor.has_method("set_view") and actor.has_method("set_frame")
		and actor.has_method("reset")
	)


func _valid_pose(pose: Variant) -> bool:
	if not pose is Dictionary:
		return false
	return (
		(pose.get("view") is String or pose.get("view") is StringName)
		and (pose.get("name") is String or pose.get("name") is StringName)
		and pose.get("index") is int and pose["index"] >= 0
	)


func _on_frame(index: int, generation: int, emit_hit: bool = true) -> void:
	if generation != _generation or state == State.IDLE:
		return
	var frame := _frames[index]
	state = State.RECOVERY if frame.get("phase", "Attack") == "Recovery" else State.ATTACK
	for role in ["attacker", "defender"]:
		if not frame.has(role):
			continue
		var actor = _attacker if role == "attacker" else _defender
		if not is_instance_valid(actor):
			cancel()
			return
		var pose: Dictionary = frame[role]
		actor.set_view(pose["view"])
		if generation != _generation:
			return
		actor.set_frame(pose["name"], pose["index"])
		if generation != _generation:
			return
	if emit_hit and frame.get("hit", false):
		hit.emit(_attack_id, _attacker, _defender)


func _end(was_cancelled: bool) -> void:
	var attack_id := _attack_id
	var attacker = _attacker
	var defender = _defender
	_generation += 1
	_timeline.cancel()
	_timeline = null
	_frames.clear()
	_attacker = null
	_defender = null
	state = State.IDLE
	# Block playback from actor reset callbacks until both actors are restored.
	_resetting = true
	if is_instance_valid(attacker):
		attacker.reset()
	if defender != attacker and is_instance_valid(defender):
		defender.reset()
	_resetting = false
	if was_cancelled:
		cancelled.emit(attack_id, attacker, defender)
	else:
		finished.emit(attack_id, attacker, defender)
