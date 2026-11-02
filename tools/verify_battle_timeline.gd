extends SceneTree
## Headless behavioural checks; preload avoids dependence on the class-name cache.

const Timeline = preload("res://scenes/battle/battle_timeline.gd")
var _failures: int = 0


func _initialize() -> void:
	for hz in [30, 60, 144]:
		_check_tick_rate(hz)
	_check_transport()
	_check_custom_frames()
	if _failures == 0:
		print("PASS battle timeline")
	quit(0 if _failures == 0 else 1)


func _expect(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: ", message)


func _check_tick_rate(hz: int) -> void:
	var timeline = Timeline.new()
	var events: Array = []
	var completions: Array = []
	timeline.event_fired.connect(func(name): events.append([name, timeline.position_ms]))
	timeline.finished.connect(func(): completions.append(true))
	timeline.restart()
	for tick in range(hz * 2):
		timeline.advance(1.0 / float(hz))
	_expect(events.size() == 1, "%d Hz: one hit" % hz)
	if events.size() == 1:
		_expect(events[0][0] == &"hit", "%d Hz: named hit" % hz)
		_expect(is_equal_approx(events[0][1], 430.0), "%d Hz: hit at 430 ms" % hz)
	_expect(is_equal_approx(timeline.position_ms, 1050.0), "%d Hz: duration" % hz)
	_expect(completions.size() == 1, "%d Hz: finish once" % hz)
	_expect(not timeline.running, "%d Hz: stopped at end" % hz)
	_disconnect_timeline(timeline)


func _check_transport() -> void:
	var timeline = Timeline.new()
	var events: Array = []
	timeline.event_fired.connect(func(name): events.append(name))
	timeline.restart()
	timeline.advance(0.429)
	_expect(events.is_empty(), "no early hit")
	timeline.pause()
	timeline.advance(1.0)
	_expect(is_equal_approx(timeline.position_ms, 429.0), "pause freezes clock")
	_expect(events.is_empty(), "pause is silent")
	timeline.resume()
	timeline.advance(0.001)
	_expect(events.size() == 1, "hit at exact boundary")
	timeline.advance(0.049)
	_expect(timeline.frame_index == 2, "hitstop remains inside the 50 ms frame")
	timeline.advance(0.001)
	_expect(timeline.frame_index == 3, "hitstop ends at 480 ms")
	timeline.seek(0.0)
	timeline.advance(0.5)
	_expect(events.size() == 1, "backward seek does not re-arm hit")

	timeline.restart()
	events.clear()
	timeline.seek(600.0)
	timeline.advance(0.1)
	_expect(events.is_empty(), "forward seek is silent and consumes hit")
	timeline.seek(0.0)
	timeline.advance(0.5)
	_expect(events.is_empty(), "seeked hit stays consumed")

	timeline.restart()
	events.clear()
	timeline.step_frame()
	timeline.step_frame()
	timeline.advance(1.0)
	_expect(timeline.paused, "frame step pauses")
	_expect(events.is_empty(), "frame steps are silent")
	timeline.resume()
	timeline.advance(0.1)
	_expect(events.is_empty(), "stepped hit stays consumed")

	timeline.cancel()
	_expect(timeline.position_ms == 0.0, "cancel resets time")
	_expect(timeline.frame_index == 0, "cancel resets frame")
	_expect(not timeline.running and not timeline.paused, "cancel resets transport")
	timeline.advance(1.0)
	_expect(events.is_empty(), "cancelled clock stays silent")

	timeline.restart()
	_expect(timeline.set_speed(0.5), "slow speed accepted")
	timeline.advance(0.859)
	_expect(events.is_empty(), "slow speed delays hit")
	timeline.advance(0.001)
	_expect(events.size() == 1, "slow speed reaches hit at 860 ms")
	timeline.advance(1.24)
	_expect(timeline.position_ms == 1050.0, "slow cycle finishes at 2100 ms")
	timeline.restart()
	timeline.advance(0.86)
	_expect(events.size() == 2, "restart starts a fresh cycle")
	_expect(not timeline.set_speed(0.0), "zero speed rejected")
	_expect(not timeline.set_speed(-1.0), "negative speed rejected")
	_expect(not timeline.set_speed(INF), "infinite speed rejected")
	_disconnect_timeline(timeline)


func _check_custom_frames() -> void:
	var timeline = Timeline.new()
	var events: Array = []
	timeline.event_fired.connect(func(name): events.append(name))
	_expect(timeline.configure([
		{"duration_ms": 10.0, "events": [&"start"]},
		{"duration_ms": 20.0, "events": [&"hit", &"sound"]},
		{"duration_ms": 30.0, "events": [&"recover"]},
	]), "custom frames accepted")
	timeline.restart()
	timeline.advance(1.0)
	_expect(events == [&"start", &"hit", &"sound", &"recover"],
		"large tick preserves all events in order")
	timeline.advance(1.0)
	_expect(events.size() == 4, "completed cycle remains silent")
	timeline.restart()
	_expect(events.size() == 5, "initial event re-arms on restart")
	_expect(not timeline.configure([]), "empty frames rejected")
	_expect(not timeline.configure([{"duration_ms": -1}]), "negative duration rejected")
	_expect(not timeline.configure([{"duration_ms": INF}]), "infinite duration rejected")
	_expect(not timeline.configure([{"duration_ms": 10, "events": [42]}]),
		"invalid event rejected")
	_expect(timeline.duration_ms == 60.0, "invalid configuration preserves timeline")
	timeline.cancel()
	events.clear()
	timeline.seek(0.0)
	_expect(events.is_empty(), "seek to initial event is silent")
	_disconnect_timeline(timeline)


func _disconnect_timeline(timeline: RefCounted) -> void:
	# Captured timeline references form cycles through connected lambdas.
	# Disconnect before leaving each check so RefCounted resources can release.
	for connection in timeline.event_fired.get_connections():
		timeline.event_fired.disconnect(connection["callable"])
	for connection in timeline.finished.get_connections():
		timeline.finished.disconnect(connection["callable"])
