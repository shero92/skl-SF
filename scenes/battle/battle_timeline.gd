extends RefCounted
## Deterministic, manually ticked battle animation clock. All times are milliseconds.
## Implementation: Codex (GPT-6). Hitstop occupies an ordinary timed frame.

signal event_fired(event_name: StringName)
signal finished

const EPSILON_MS := 0.000001

var position_ms: float = 0.0
var duration_ms: float = 0.0
var frame_index: int = 0
var running: bool = false
var paused: bool = false
var speed: float = 1.0

var _frames: Array[Dictionary] = []
var _starts: Array[float] = []
var _consumed: Dictionary = {}


func _init() -> void:
	configure([
		{"duration_ms": 180.0},
		{"duration_ms": 250.0},
		{"duration_ms": 50.0, "events": [&"hit"]},
		{"duration_ms": 170.0},
		{"duration_ms": 400.0},
	])


## Events belong to frame entry; durations include any hitstop.
## Invalid configuration leaves the existing timeline untouched.
func configure(frames: Array) -> bool:
	if frames.is_empty():
		return false
	var prepared: Array[Dictionary] = []
	var starts: Array[float] = []
	var total := 0.0
	for value in frames:
		if not value is Dictionary:
			return false
		var duration = value.get("duration_ms", 0.0)
		if not (duration is float or duration is int):
			return false
		if not is_finite(float(duration)) or duration <= 0.0:
			return false
		var events = value.get("events", [])
		if not events is Array:
			return false
		var names: Array[StringName] = []
		for event in events:
			if not (event is String or event is StringName):
				return false
			if String(event).is_empty():
				return false
			names.append(StringName(event))
		starts.append(total)
		total += float(duration)
		if not is_finite(total):
			return false
		prepared.append({"duration_ms": float(duration), "events": names})
	_frames = prepared
	_starts = starts
	duration_ms = total
	cancel()
	return true


func set_speed(value: float) -> bool:
	if not is_finite(value) or value <= 0.0:
		return false
	speed = value
	return true


## A restart is the only transport operation that re-arms all events.
func restart() -> void:
	cancel()
	running = true
	_emit_frame_events(0)


func pause() -> void:
	paused = true


func resume() -> void:
	paused = false


## Restore the initial transport state without emitting signals.
func cancel() -> void:
	position_ms = 0.0
	frame_index = 0
	running = false
	paused = false
	_consumed.clear()


## Silent scrubbing consumes crossed events, including when stopped or paused.
## Scrubbing backwards never re-arms an event within the same cycle.
func seek(time_ms: float) -> void:
	if not is_finite(time_ms):
		return
	position_ms = clampf(time_ms, 0.0, duration_ms)
	for index in range(_frames.size()):
		if _starts[index] <= position_ms + EPSILON_MS:
			_consumed[index] = true
	_update_frame()
	if position_ms >= duration_ms:
		running = false


## Single-frame debugging is always silent and leaves playback paused.
func step_frame() -> void:
	pause()
	var next_index := frame_index + 1
	if next_index < _starts.size():
		seek(_starts[next_index])
	else:
		seek(duration_ms)


## Advance using seconds, as supplied by Godot's process callbacks.
## Scan every crossed boundary so large ticks cannot lose events.
func advance(delta_seconds: float) -> void:
	if not running or paused:
		return
	if not is_finite(delta_seconds) or delta_seconds <= 0.0:
		return
	var increment := delta_seconds * 1000.0 * speed
	if not is_finite(increment):
		return
	var target := minf(position_ms + increment, duration_ms)
	if duration_ms - target <= EPSILON_MS:
		target = duration_ms
	for index in range(_frames.size()):
		if _starts[index] <= target + EPSILON_MS and not _consumed.has(index):
			position_ms = _starts[index]
			frame_index = index
			_emit_frame_events(index)
			# Honour transport changes made by signal listeners.
			if not running or paused or position_ms != _starts[index]:
				return
	position_ms = target
	_update_frame()
	if position_ms >= duration_ms:
		running = false
		finished.emit()


func _emit_frame_events(index: int) -> void:
	if _consumed.has(index):
		return
	_consumed[index] = true
	for event in _frames[index]["events"]:
		event_fired.emit(event)


func _update_frame() -> void:
	frame_index = 0
	for index in range(_starts.size()):
		if _starts[index] <= position_ms + EPSILON_MS:
			frame_index = index
		else:
			break
