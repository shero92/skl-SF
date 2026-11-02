extends SceneTree
## Agent: codex; model: GPT-6.

const Controller = preload("res://scenes/battle/battle_animation_controller.gd")

var _failures: int = 0


class Actor extends RefCounted:
	var view: String = "Idle"
	var frame_name: String = "Idle"
	var frame_index: int = 0
	var resets: int = 0

	func set_view(value) -> void:
		view = value

	func set_frame(value, index) -> void:
		frame_name = value
		frame_index = index

	func reset() -> void:
		view = "Idle"
		frame_name = "Idle"
		frame_index = 0
		resets += 1


func _initialize() -> void:
	_test_lifecycle()
	_test_failures()
	_test_cancel_and_reset()
	_test_callbacks()
	if _failures == 0:
		print("BATTLE_CONTROLLER_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _controller():
	var controller = Controller.new()
	controller.attacks = {
		&"slash": {
			"assets": [],
			"frames": [
				{
					"duration_ms": 100,
					"attacker": {"view": "front", "name": "slash", "index": 0},
					"defender": {"view": "back", "name": "guard", "index": 0},
				},
				{
					"duration_ms": 100, "hit": true,
					"attacker": {"view": "front", "name": "slash", "index": 1},
					"defender": {"view": "back", "name": "react", "index": 1},
				},
				{"duration_ms": 100, "phase": "Recovery"},
			],
		},
	}
	return controller


func _test_lifecycle() -> void:
	for hz in [30, 60, 144]:
		var controller = _controller()
		var attacker := Actor.new()
		var defender := Actor.new()
		var events: Array[String] = []
		controller.started.connect(func(_id, a, d):
			_check(a == attacker and d == defender, "started actor identity")
			events.append("started"))
		controller.hit.connect(func(_id, a, d):
			_check(a.frame_index == 1 and d.frame_name == "react", "hit poses")
			events.append("hit"))
		controller.finished.connect(func(_id, a, d):
			_check(a.view == "Idle" and d.view == "Idle", "finish restores actors")
			events.append("finished"))
		_check(controller.play_attack(&"slash", attacker, defender).ok, "valid attack")
		_check(controller.state == Controller.State.ATTACK, "Idle to Attack")
		_check(attacker.frame_name == "slash" and defender.frame_name == "guard", "initial poses")
		_check(controller.play_attack(&"slash", defender, attacker).reason == "BUSY", "busy rejection")
		controller.advance(0.2)
		_check(controller.state == Controller.State.RECOVERY, "Attack to Recovery")
		for tick in range(hz):
			controller.advance(1.0 / hz)
		_check(controller.state == Controller.State.IDLE, "Recovery to Idle")
		_check(events == ["started", "hit", "finished"], "ordered signals once")
		_check(attacker.resets == 1 and defender.resets == 1, "both reset once")
		controller.advance(10.0)
		_check(events.size() == 3, "idle advance silent")

	var controller = _controller()
	var hits: Array[int] = []
	controller.hit.connect(func(_id, _a, _d): hits.append(1))
	controller.play_attack(&"slash", Actor.new(), Actor.new())
	controller.advance(10.0)
	_check(hits.size() == 1 and controller.state == Controller.State.IDLE, "large tick")


func _test_failures() -> void:
	var controller = _controller()
	var attacker := Actor.new()
	var defender := Actor.new()
	var events: Array[int] = []
	controller.started.connect(func(_id, _a, _d): events.append(1))
	_check(controller.play_attack(&"unknown", attacker, defender).reason == "MISSING_ATTACK", "missing id")
	controller.attacks[&"missing"] = {
		"assets": ["res://__missing_battle_controller_asset__.tres"],
		"frames": controller.attacks[&"slash"]["frames"],
	}
	_check(controller.play_attack(&"missing", attacker, defender).reason == "MISSING_ASSET", "missing asset")
	controller.attacks[&"bad"] = {"frames": [{"duration_ms": 0}]}
	_check(controller.play_attack(&"bad", attacker, defender).reason == "INVALID_ATTACK", "bad frames")
	_check(controller.play_attack(&"slash", null, defender).reason == "INVALID_ACTOR", "bad actor")
	_check(controller.state == Controller.State.IDLE and events.is_empty(), "failures preserve state")
	_check(attacker.resets == 0 and defender.resets == 0, "failures never reset")
	_check(attacker.view == "Idle" and defender.view == "Idle", "failures preserve poses")


func _test_cancel_and_reset() -> void:
	for operation in ["cancel", "reset"]:
		for time in [0.0, 0.15, 0.25]:
			var controller = _controller()
			var attacker := Actor.new()
			var defender := Actor.new()
			var cancelled: Array[int] = []
			var finished: Array[int] = []
			controller.cancelled.connect(func(_id, _a, _d): cancelled.append(1))
			controller.finished.connect(func(_id, _a, _d): finished.append(1))
			controller.play_attack(&"slash", attacker, defender)
			controller.advance(time)
			controller.call(operation)
			controller.call(operation)
			controller.advance(10.0)
			_check(controller.state == Controller.State.IDLE, operation + " restores Idle")
			_check(attacker.view == "Idle" and defender.view == "Idle", operation + " restores poses")
			_check(cancelled.size() == 1 and finished.is_empty(), operation + " signals")
			_check(controller.play_attack(&"slash", attacker, defender).ok, operation + " permits reuse")
			controller.advance(1.0)
			_check(finished.size() == 1, "reused controller finishes")


func _test_callbacks() -> void:
	var controller = _controller()
	var attacker := Actor.new()
	var defender := Actor.new()
	var finished: Array[int] = []
	controller.hit.connect(func(_id, _a, _d): controller.cancel())
	controller.finished.connect(func(_id, _a, _d): finished.append(1))
	controller.play_attack(&"slash", attacker, defender)
	controller.advance(1.0)
	_check(controller.state == Controller.State.IDLE and finished.is_empty(), "cancel during hit")
	_check(attacker.view == "Idle" and defender.view == "Idle", "callback cancellation restores actors")

	var early = _controller()
	early.started.connect(func(_id, _a, _d): early.reset())
	early.play_attack(&"slash", attacker, defender)
	_check(early.state == Controller.State.IDLE and attacker.view == "Idle", "reset during started")
