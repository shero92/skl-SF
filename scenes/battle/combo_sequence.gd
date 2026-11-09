extends RefCounted
## Deterministic, battle-only sequence; the caller supplies elapsed battle time.
## Agent: codex; model: GPT-6.
##
## Steps: {attack_id, min_gap = 0, max_gap = min_gap, gap = min_gap}.
## Gaps precede their attack; unavailable steps, including their gaps, are skipped.
## Catalogue: {attack_id: {available: bool, duration: seconds}}.
## Availability must be explicitly granted by the caller's approved-asset registry.
## This class requests attacks; it never applies damage or selects replacement art.

signal state_changed(value: String)
signal attack_requested(attack_id: String)
signal attack_reported(attack_id: String, status: String)
signal completed(reason: String)

const IDLE := "Idle"
const ATTACK := "Attack"
const GAP := "Gap"
const RECOVERY := "Recovery"
const UNAVAILABLE := "UNAVAILABLE"

var state: String = IDLE
var current_attack: String = ""
var elapsed: float = 0.0

var _active: bool = false
var _generation: int = 0
var _steps: Array = []
var _catalogue: Dictionary = {}
var _index: int = 0
var _remaining: float = 0.0
var _recovery: float = 0.0


func is_running() -> bool:
	return _active


func start(
	definition: Array,
	catalogue: Dictionary,
	recovery_seconds: float = 0.0,
	skip_unavailable: bool = true
) -> bool:
	# Validate the complete definition before changing state or emitting signals.
	if _active or definition.is_empty() or not _seconds(recovery_seconds):
		return false
	var steps: Array = []
	for entry in definition:
		if not entry is Dictionary:
			return false
		var attack_id = entry.get("attack_id", "")
		if not attack_id is String or attack_id.strip_edges().is_empty():
			return false
		var minimum = entry.get("min_gap", 0.0)
		var maximum = entry.get("max_gap", minimum)
		var gap = entry.get("gap", minimum)
		if not _seconds(minimum) or not _seconds(maximum) or not _seconds(gap):
			return false
		if minimum > maximum or gap < minimum or gap > maximum:
			return false
		var asset = catalogue.get(attack_id, {})
		if not asset is Dictionary:
			return false
		var available = asset.get("available", false)
		if not available is bool:
			return false
		if available and not _seconds(asset.get("duration", null)):
			return false
		steps.append({"attack_id": attack_id, "gap": float(gap)})

	# Strict mode reports the first unavailable attack and rejects the sequence.
	if not skip_unavailable:
		for step in steps:
			if not catalogue.get(step.attack_id, {}).get("available", false):
				attack_reported.emit(step.attack_id, UNAVAILABLE)
				return false

	_generation += 1
	var generation: int = _generation
	_steps = steps
	_catalogue = catalogue.duplicate(true)
	_recovery = recovery_seconds
	_index = 0
	elapsed = 0.0
	_active = true
	_next(generation)
	return true


func advance(delta: float) -> bool:
	# Use the same clock as the battle timeline (pause/hitstop included).
	if not _seconds(delta):
		return false
	var generation: int = _generation
	var budget: float = delta
	while _active and generation == _generation:
		var consumed: float = minf(budget, _remaining)
		_remaining -= consumed
		budget -= consumed
		elapsed += consumed
		if _remaining > 0.0:
			break
		match state:
			GAP:
				_play(generation)
			ATTACK:
				_next(generation)
			RECOVERY:
				_finish("finished")
			_:
				break
	return true


func cancel() -> bool:
	if not _active:
		return false
	_finish("cancelled")
	return true


func interrupt() -> bool:
	if not _active:
		return false
	_finish("interrupted")
	return true


func _next(generation: int) -> void:
	while _index < _steps.size():
		var step: Dictionary = _steps[_index]
		_index += 1
		current_attack = step.attack_id
		if not _catalogue.get(current_attack, {}).get("available", false):
			attack_reported.emit(current_attack, UNAVAILABLE)
			if generation != _generation:
				return
			continue
		if step.gap > 0.0:
			_remaining = step.gap
			_set_state(GAP)
		else:
			_play(generation)
		return
	current_attack = ""
	_remaining = _recovery
	_set_state(RECOVERY)
	if generation == _generation and _remaining == 0.0:
		_finish("finished")


func _play(generation: int) -> void:
	_remaining = float(_catalogue[current_attack].duration)
	_set_state(ATTACK)
	if generation == _generation:
		attack_requested.emit(current_attack)


func _set_state(value: String) -> void:
	if state != value:
		state = value
		state_changed.emit(state)


func _finish(reason: String) -> void:
	_generation += 1
	var generation: int = _generation
	_active = false
	_remaining = 0.0
	current_attack = ""
	_steps = []
	_catalogue = {}
	_index = 0
	_set_state(IDLE)
	# A signal listener may already have started a replacement sequence.
	if generation == _generation:
		completed.emit(reason)


func _seconds(value: Variant) -> bool:
	if typeof(value) != TYPE_INT and typeof(value) != TYPE_FLOAT:
		return false
	return is_finite(float(value)) and float(value) >= 0.0
