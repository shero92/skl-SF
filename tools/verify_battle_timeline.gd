extends SceneTree

const Timeline = preload("res://scenes/battle/battle_timeline.gd")

var _failures: int = 0


func _initialize() -> void:
	_test_rates()
	_test_controls()
	_test_large_tick_and_named_events()
	_test_validation()
	if _failures == 0:
		print("BATTLE_TIMELINE_OK")
	quit(0 if _failures == 0 else 1)


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _new_timeline():
	var timeline = Timeline.new()
	# Reference: 1050 ms total, hit at 430 ms, 50 ms hitstop INCLUDED.
	var frames: Array[Dictionary] = [
		{"duration_ms": 200.0},
		{"duration_ms": 230.0},
		{"duration_ms": 50.0, "events": ["hit"]},
		{"duration_ms": 570.0},
	]
	_check(timeline.configure(frames), "reference configuration")
	return timeline


func _test_rates() -> void:
	for hz in [30, 60, 144]:
		for rate in [1.0, 0.25]:
			var timeline = _new_timeline()
			var hits: Array[float] = []
			timeline.event_fired.connect(
				func(event): 
					if event == &"hit":
						hits.append(timeline.position_ms)
			)
			_check(timeline.set_speed(rate), "valid speed")
			timeline.restart()
			var elapsed := 0.0
			var tick := 1.0 / float(hz)
			while timeline.playing and elapsed < 10.0:
				timeline.advance(tick)
				elapsed += tick
			_check(hits.size() == 1, "one hit at %s Hz speed %s" % [hz, rate])
			if hits.size() == 1:
				_check(is_equal_approx(hits[0], 430.0), "exact hit boundary")
			_check(is_equal_approx(timeline.position_ms, 1050.0), "duration includes hitstop")
			_check(elapsed + 0.000001 >= 1.05 / rate, "no early completion")
			_check(elapsed <= 1.05 / rate + tick + 0.000001, "bounded completion")
			timeline.advance(10.0)
			_check(hits.size() == 1, "completed cycle cannot repeat")


func _test_controls() -> void:
	var timeline = _new_timeline()
	var hits: Array[StringName] = []
	timeline.event_fired.connect(func(event): hits.append(event))
	timeline.restart()
	timeline.advance(0.2)
	timeline.pause()
	timeline.advance(1.0)
	_check(is_equal_approx(timeline.position_ms, 200.0), "pause holds position")
	_check(hits.is_empty(), "pause emits nothing")
	timeline.step_frame()
	_check(is_equal_approx(timeline.position_ms, 430.0), "step reaches hit frame")
	_check(not timeline.playing and hits.is_empty(), "step is silent and paused")
	timeline.resume()
	timeline.advance(1.0)
	_check(hits.is_empty(), "stepped hit is consumed")

	timeline.restart()
	timeline.seek(430.0)
	_check(hits.is_empty(), "seek to boundary is silent")
	timeline.seek(100.0)
	timeline.advance(1.0)
	_check(hits.is_empty(), "backward seek does not replay consumed hit")

	timeline.restart()
	timeline.advance(0.43)
	_check(hits.size() == 1, "restart begins fresh event cycle")
	timeline.pause()
	timeline.resume()
	timeline.seek(0.0)
	timeline.advance(1.0)
	_check(hits.size() == 1, "pause and backward seek cannot duplicate hit")

	timeline.set_speed(0.25)
	timeline.cancel()
	_check(timeline.position_ms == 0.0, "cancel resets clock")
	_check(timeline.frame_index == 0, "cancel resets frame")
	_check(not timeline.playing and timeline.speed == 1.0, "cancel restores initial state")
	timeline.advance(2.0)
	_check(hits.size() == 1, "cancel stops playback")
	timeline.restart()
	timeline.advance(2.0)
	_check(hits.size() == 2, "restart after cancel fires once")

	timeline.restart()
	timeline.seek(-10.0)
	_check(timeline.position_ms == 0.0, "seek clamps below zero")
	timeline.seek(2000.0)
	_check(timeline.position_ms == 1050.0 and not timeline.playing, "seek clamps at end")
	_check(hits.size() == 2, "clamped seeks are silent")


func _test_large_tick_and_named_events() -> void:
	var timeline = Timeline.new()
	var frames: Array[Dictionary] = [
		{"duration_ms": 100.0, "events": ["start"]},
		{"duration_ms": 100.0, "events": ["hit", "sound"]},
		{"duration_ms": 100.0, "events": ["finish"]},
	]
	_check(timeline.configure(frames), "named event configuration")
	var events: Array[StringName] = []
	timeline.event_fired.connect(func(event): events.append(event))
	timeline.restart()
	timeline.advance(1.0)
	_check(events == [&"start", &"hit", &"sound", &"finish"], "large tick preserves event order")
	timeline.advance(1.0)
	_check(events.size() == 4, "large tick emits once")

	timeline.restart()
	timeline.advance(0.0)
	timeline.advance(-1.0)
	_check(events.size() == 4 and timeline.position_ms == 0.0, "invalid ticks do nothing")
	timeline.advance(0.1)
	timeline.advance(0.000001)
	_check(events.size() == 7, "exact boundary does not duplicate events")


func _test_validation() -> void:
	var timeline = _new_timeline()
	var invalid: Array[Dictionary] = [{"duration_ms": 0.0}]
	_check(not timeline.configure(invalid), "reject zero duration")
	_check(timeline.duration_ms == 1050.0, "invalid configuration preserves timeline")
	_check(not timeline.set_speed(0.0), "reject zero speed")
	_check(not timeline.set_speed(-1.0), "reject negative speed")
	_check(not timeline.set_speed(INF), "reject infinite speed")
	timeline.restart()
	timeline.advance(NAN)
	timeline.seek(NAN)
	_check(timeline.position_ms == 0.0, "nonfinite input leaves clock intact")
