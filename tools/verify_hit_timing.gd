extends SceneTree
## Execution provenance: Agent: codex; model: GPT-6.
## Exercise the real controller/timeline; no damage code or production actors.

const Controller = preload("res://scenes/battle/battle_animation_controller.gd")
const Bridge = preload("res://scenes/battle/hit_timing_bridge.gd")

var _failures: int = 0


class Actor extends RefCounted:
	func set_view(_value) -> void:
		pass

	func set_frame(_value, _index) -> void:
		pass

	func reset() -> void:
		pass


func _initialize() -> void:
	_test_playback()
	_test_preview()
	_test_cancel_and_restart()
	_test_bindings()
	_test_reentrant_restart()
	if _failures == 0:
		print("BATTLE_HIT_TIMING_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _controller():
	var controller = Controller.new()
	controller.attacks = {
		&"double": {
			"frames": [
				{"duration_ms": 100, "hit": true},
				{"duration_ms": 100, "hit": true},
				{"duration_ms": 100, "phase": "Recovery"},
			],
		},
	}
	return controller


func _capture(bridge, events: Array) -> void:
	bridge.hit_confirmed.connect(func(a, d, id, index):
		events.append([a, d, id, index]))


func _test_playback() -> void:
	for hz in [30, 60, 144]:
		var controller = _controller()
		var bridge = Bridge.new()
		var attacker := Actor.new()
		var defender := Actor.new()
		var events: Array = []
		_capture(bridge, events)
		_check(bridge.bind_controller(controller), "bind idle controller")
		_check(controller.play_attack(&"double", attacker, defender).ok, "start attack")
		_check(events.is_empty(), "initial pose does not confirm a hit")
		for tick in range(hz):
			controller.advance(1.0 / hz)
		_check(events == [
			[attacker, defender, &"double", 0],
			[attacker, defender, &"double", 1],
		], "ordered hits and exact actor identity at " + str(hz) + " Hz")
		controller.advance(10.0)
		_check(events.size() == 2, "idle advancement cannot repeat hits")
		bridge.unbind_controller()

	var controller = _controller()
	var bridge = Bridge.new()
	var events: Array = []
	_capture(bridge, events)
	bridge.bind_controller(controller)
	controller.play_attack(&"double", Actor.new(), Actor.new())
	controller.advance(10.0)
	_check(events.size() == 2, "large tick confirms both crossed hits")
	bridge.unbind_controller()


func _test_preview() -> void:
	var controller = _controller()
	var bridge = Bridge.new()
	var events: Array = []
	_capture(bridge, events)
	bridge.bind_controller(controller)
	controller.play_attack(&"double", Actor.new(), Actor.new())
	# The controller has no public preview API. Exercise its timeline directly;
	# calling controller.advance while paused would end the controller playback.
	var timeline = controller._timeline
	timeline.pause()
	timeline.advance(1.0)
	_check(events.is_empty(), "pause is silent")
	timeline.resume()
	controller.advance(0.05)
	_check(events.size() == 1, "resume confirms first hit once")
	timeline.pause()
	timeline.advance(1.0)
	timeline.resume()
	controller.advance(0.01)
	_check(events.size() == 1, "pause/resume does not repeat consumed hit")
	timeline.step_frame()
	_check(events.size() == 1, "frame step silently consumes second hit")
	timeline.seek(0.0)
	timeline.resume()
	controller.advance(1.0)
	_check(events.size() == 1, "backwards seek cannot replay previewed hits")
	bridge.unbind_controller()

	controller = _controller()
	bridge = Bridge.new()
	events = []
	_capture(bridge, events)
	bridge.bind_controller(controller)
	controller.play_attack(&"double", Actor.new(), Actor.new())
	controller._timeline.step_frame()
	controller._timeline.resume()
	controller.advance(1.0)
	_check(events.is_empty(), "step before first advance consumes crossed hits")
	bridge.unbind_controller()


func _test_cancel_and_restart() -> void:
	for operation in ["cancel", "reset"]:
		for elapsed in [0.0, 0.05, 0.15]:
			var controller = _controller()
			var bridge = Bridge.new()
			var events: Array = []
			_capture(bridge, events)
			bridge.bind_controller(controller)
			var attacker := Actor.new()
			var defender := Actor.new()
			controller.play_attack(&"double", attacker, defender)
			controller.advance(elapsed)
			var expected := 0 if elapsed == 0.0 else (1 if elapsed < 0.1 else 2)
			_check(events.size() == expected, "hits before " + operation)
			controller.call(operation)
			controller.call(operation)
			controller.advance(1.0)
			_check(events.size() == expected, operation + " prevents pending hits")
			events.clear()
			controller.play_attack(&"double", attacker, defender)
			controller.advance(1.0)
			_check(events == [
				[attacker, defender, &"double", 0],
				[attacker, defender, &"double", 1],
			], operation + " then replay starts a fresh hit sequence")
			events.clear()
			controller.play_attack(&"double", attacker, defender)
			controller.advance(1.0)
			_check(events.size() == 2 and events[0][3] == 0, "finished replay resets index")
			bridge.unbind_controller()


func _test_bindings() -> void:
	var controller = _controller()
	var replacement = _controller()
	var bridge = Bridge.new()
	var events: Array = []
	_capture(bridge, events)
	_check(not bridge.bind_controller(null), "null binding rejected")
	bridge.bind_controller(controller)
	controller.play_attack(&"double", Actor.new(), Actor.new())
	controller.advance(0.05)
	_check(bridge.bind_controller(controller), "repeat binding accepted during playback")
	controller.advance(0.06)
	_check(events.size() == 2 and events[1][3] == 1, "repeat binding preserves index")
	bridge.unbind_controller()
	bridge.unbind_controller()
	controller.advance(1.0)
	controller.play_attack(&"double", Actor.new(), Actor.new())
	controller.advance(1.0)
	_check(events.size() == 2, "unbound bridge stays silent")
	bridge.bind_controller(controller)
	replacement.play_attack(&"double", Actor.new(), Actor.new())
	_check(not bridge.bind_controller(replacement), "late binding rejected")
	controller.play_attack(&"double", Actor.new(), Actor.new())
	controller.advance(1.0)
	_check(events.size() == 4, "rejected binding preserves original subscription")
	replacement.cancel()
	_check(bridge.bind_controller(replacement), "replace idle controller")
	controller.play_attack(&"double", Actor.new(), Actor.new())
	controller.advance(1.0)
	_check(events.size() == 4, "old controller disconnected")
	replacement.play_attack(&"double", Actor.new(), Actor.new())
	replacement.advance(1.0)
	_check(events.size() == 6 and events[4][3] == 0, "replacement confirms fresh sequence")
	bridge.unbind_controller()


func _test_reentrant_restart() -> void:
	var controller = _controller()
	var bridge = Bridge.new()
	var attacker := Actor.new()
	var defender := Actor.new()
	var events: Array = []
	bridge.bind_controller(controller)
	bridge.hit_confirmed.connect(func(a, d, id, index):
		events.append([a, d, id, index])
		if events.size() == 1:
			controller.cancel()
			controller.play_attack(&"double", attacker, defender))
	controller.play_attack(&"double", attacker, defender)
	controller.advance(1.0)
	_check(events.size() == 1, "cancel in subscriber stops old timeline")
	controller.advance(1.0)
	_check(events == [
		[attacker, defender, &"double", 0],
		[attacker, defender, &"double", 0],
		[attacker, defender, &"double", 1],
	], "subscriber restart resets index without stale hits")
	bridge.unbind_controller()
