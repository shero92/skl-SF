extends Camera2D
## Battle-only camera. All animation is driven by advance(delta).
## Agent: codex. Model: GPT-6.
## Hitstop freezes focus/follow; shake continues to decay in real delta time.

@export var reference_size := Vector2(320.0, 180.0)
@export_range(0.0, 0.1) var motion_fraction := 0.1
@export_range(0.0, 3.0) var maximum_shake_px := 3.0
@export var follow_speed := 8.0

const PRESETS := {
	"hero_rear_3q": [Vector2(-16.0, 8.0), Vector2(1.1, 1.1)],
	"hero_front": [Vector2(16.0, 0.0), Vector2(1.15, 1.15)],
	"monster_rear": [Vector2(0.0, -8.0), Vector2(1.1, 1.1)],
}

var hitstop_active := false
var shake_offset := Vector2.ZERO

var _captured := false
var _initial_transform := Transform2D.IDENTITY
var _initial_offset := Vector2.ZERO
var _initial_zoom := Vector2.ONE
var _base_offset := Vector2.ZERO
var _from_offset := Vector2.ZERO
var _to_offset := Vector2.ZERO
var _from_zoom := Vector2.ONE
var _to_zoom := Vector2.ONE
var _focus_elapsed := 0.0
var _focus_duration := 0.0
var _following: Node2D
var _shake_amplitude := 0.0
var _shake_elapsed := 0.0
var _shake_duration := 0.0


func _ready() -> void:
	_capture()
	# Built-in smoothing would continue moving after restore().
	position_smoothing_enabled = false
	rotation_smoothing_enabled = false
	process_mode = Node.PROCESS_MODE_ALWAYS


func _process(delta: float) -> void:
	advance(delta)


func _capture() -> void:
	if _captured:
		return
	_initial_transform = transform
	_initial_offset = offset
	_initial_zoom = zoom
	_base_offset = offset
	_from_offset = offset
	_to_offset = offset
	_from_zoom = zoom
	_to_zoom = zoom
	_captured = true


func _bounded_offset(value: Vector2) -> Vector2:
	# Reserve room for shake so combined motion stays within the frame budget.
	var budget := reference_size.abs() * clampf(motion_fraction, 0.0, 0.1)
	budget = (budget - Vector2.ONE * clampf(maximum_shake_px, 0.0, 3.0)).max(Vector2.ZERO)
	budget /= _initial_zoom
	return _initial_offset + (value - _initial_offset).clamp(-budget, budget)


func _target_offset(target: Variant) -> Vector2:
	var world_position: Vector2
	if target is Node2D and is_instance_valid(target):
		world_position = target.global_position
	elif target is Vector2:
		world_position = target
	else:
		return _base_offset
	if not world_position.is_finite():
		return _base_offset
	return _bounded_offset(_initial_offset + to_local(world_position))


func focus_on(target: Variant, target_zoom: Vector2 = Vector2.ONE, duration: float = 0.25) -> void:
	_capture()
	if not target_zoom.is_finite() or target_zoom.x <= 0.0 or target_zoom.y <= 0.0:
		return
	if not is_finite(duration):
		return
	_following = null
	_from_offset = _base_offset
	_to_offset = _target_offset(target)
	_from_zoom = zoom
	_to_zoom = target_zoom
	_focus_elapsed = 0.0
	_focus_duration = maxf(duration, 0.0)
	if _focus_duration == 0.0 and not hitstop_active:
		_base_offset = _to_offset
		zoom = _to_zoom
		offset = _base_offset + shake_offset


func follow(target: Node2D) -> void:
	_capture()
	_following = target
	_focus_duration = 0.0


func set_preset(preset_name: String, duration: float = 0.25) -> bool:
	if not PRESETS.has(preset_name):
		return false
	var preset: Array = PRESETS[preset_name]
	focus_on(to_global(preset[0]), preset[1], duration)
	return true


func shake(amplitude_px: float, duration: float) -> void:
	_capture()
	if not is_finite(amplitude_px) or not is_finite(duration):
		return
	_shake_amplitude = clampf(amplitude_px, 0.0, clampf(maximum_shake_px, 0.0, 3.0))
	_shake_duration = maxf(duration, 0.0)
	_shake_elapsed = 0.0
	shake_offset = Vector2.ZERO
	offset = _base_offset


func advance(delta: float) -> void:
	_capture()
	if not is_finite(delta) or delta <= 0.0:
		return
	if not hitstop_active:
		if is_instance_valid(_following):
			var weight := 1.0 - exp(-maxf(follow_speed, 0.0) * delta)
			_base_offset = _base_offset.lerp(_target_offset(_following), weight)
		elif _focus_duration > 0.0:
			_focus_elapsed = minf(_focus_elapsed + delta, _focus_duration)
			var progress := _focus_elapsed / _focus_duration
			var eased := progress * progress * (3.0 - 2.0 * progress)
			_base_offset = _from_offset.lerp(_to_offset, eased)
			zoom = _from_zoom.lerp(_to_zoom, eased)
		elif _focus_elapsed == 0.0:
			_base_offset = _to_offset
			zoom = _to_zoom
	# Shake is specified in reference pixels, independently of camera zoom.
	shake_offset = Vector2.ZERO
	if _shake_duration > 0.0:
		_shake_elapsed = minf(_shake_elapsed + delta, _shake_duration)
		if _shake_elapsed < _shake_duration:
			var envelope := 1.0 - _shake_elapsed / _shake_duration
			var phase := _shake_elapsed * TAU * 24.0
			shake_offset = Vector2(cos(phase), sin(phase)) * _shake_amplitude * envelope / zoom
	offset = _base_offset + shake_offset


func restore() -> void:
	_capture()
	_following = null
	hitstop_active = false
	_focus_duration = 0.0
	_focus_elapsed = 0.0
	_shake_duration = 0.0
	_shake_elapsed = 0.0
	shake_offset = Vector2.ZERO
	_base_offset = _initial_offset
	_from_offset = _initial_offset
	_to_offset = _initial_offset
	_from_zoom = _initial_zoom
	_to_zoom = _initial_zoom
	transform = _initial_transform
	offset = _initial_offset
	zoom = _initial_zoom
	reset_smoothing()
