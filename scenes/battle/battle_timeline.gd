extends RefCounted
## Explicitly advanced battle clock. Durations include hitstop; never add it twice.
## advance() takes seconds; frame durations, seek() and position_ms use milliseconds.
## Preview operations (seek/step_frame) consume crossed events without emitting them.

signal event_fired(event_name: StringName)

var position_ms: float = 0.0
var duration_ms: float = 0.0
var frame_index: int = 0
var playing: bool = false
var speed: float = 1.0

var _frames: Array[Dictionary] = []
var _starts: Array[float] = []
var _consumed: Dictionary = {}


func configure(frames: Array[Dictionary]) -> bool:
	# Validate before replacing an existing timeline.
	var starts: Array[float] = []
	var total := 0.0
	for frame in frames:
		var duration := float(frame.get("duration_ms", 0.0))
		if not is_finite(duration) or duration <= 0.0:
			return false
		var events: Variant = frame.get("events", [])
		if not events is Array:
			return false
		for event in events:
			if not (event is String or event is StringName):
				return false
			if str(event).is_empty():
				return false
		starts.append(total)
		total += duration
		if not is_finite(total):
			return false
	if frames.is_empty():
		return false
	_frames = frames.duplicate(true)
	_starts = starts
	duration_ms = total
	cancel()
	return true


func restart() -> void:
	position_ms = 0.0
	frame_index = 0
	_consumed.clear()
	playing = not _frames.is_empty()


func pause() -> void:
	playing = false


func resume() -> void:
	playing = not _frames.is_empty() and position_ms < duration_ms


func cancel() -> void:
	position_ms = 0.0
	frame_index = 0
	playing = false
	speed = 1.0
	_consumed.clear()


func set_speed(value: float) -> bool:
	if not is_finite(value) or value <= 0.0:
		return false
	speed = value
	return true


func advance(delta_seconds: float) -> void:
	if not playing or not is_finite(delta_seconds) or delta_seconds <= 0.0:
		return
	if not is_finite(speed) or speed <= 0.0:
		return
	var target := minf(position_ms + delta_seconds * 1000.0 * speed, duration_ms)
	# Visit boundaries in order, including all boundaries crossed by a large tick.
	for index in range(_frames.size()):
		if _starts[index] > target + 0.000001:
			break
		if _consumed.has(index):
			continue
		position_ms = _starts[index]
		frame_index = index
		_consumed[index] = true
		for event in _frames[index].get("events", []):
			event_fired.emit(StringName(event))
			# A listener may pause/cancel/seek during dispatch.
			if not playing or position_ms != _starts[index]:
				return
	position_ms = target
	_update_frame()
	if position_ms >= duration_ms:
		playing = false


func seek(time_ms: float) -> void:
	if not is_finite(time_ms):
		return
	position_ms = clampf(time_ms, 0.0, duration_ms)
	# Backward seeks retain consumed events; only restart begins a fresh cycle.
	for index in range(_starts.size()):
		if _starts[index] <= position_ms + 0.000001:
			_consumed[index] = true
	_update_frame()
	if position_ms >= duration_ms:
		playing = false


func step_frame() -> void:
	pause()
	if frame_index + 1 < _starts.size():
		seek(_starts[frame_index + 1])
	else:
		seek(duration_ms)


func _update_frame() -> void:
	frame_index = 0
	for index in range(_starts.size()):
		if _starts[index] > position_ms + 0.000001:
			break
		frame_index = index
