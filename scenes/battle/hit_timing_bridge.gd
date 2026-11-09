extends RefCounted
## Signal-only adapter; subscribing damage code owns all damage decisions.
## Execution provenance: Agent: codex; model: GPT-6.
##
## Bind before playback. hit_index is zero-based within each accepted play_attack.
## Restart playback with cancel/reset followed by play_attack, which starts a new
## hit sequence. Silent timeline previews never produce confirmed hits.

signal hit_confirmed(attacker, defender, attack_id: StringName, hit_index: int)

const Controller = preload("res://scenes/battle/battle_animation_controller.gd")

var _controller: Controller
var _next_hit_index: int = 0


func bind_controller(controller: Controller) -> bool:
	# Repeated binding must neither duplicate connections nor reset the counter.
	if controller == null:
		return false
	if controller == _controller:
		return true
	# Attaching partway through playback cannot reconstruct earlier hit indices.
	if controller.state != Controller.State.IDLE:
		return false
	unbind_controller()
	_controller = controller
	_controller.started.connect(_on_started)
	_controller.hit.connect(_on_hit)
	return true


func unbind_controller() -> void:
	if _controller != null:
		_controller.started.disconnect(_on_started)
		_controller.hit.disconnect(_on_hit)
	_controller = null
	_next_hit_index = 0


func _on_started(_attack_id: StringName, _attacker, _defender) -> void:
	_next_hit_index = 0


func _on_hit(attack_id: StringName, attacker, defender) -> void:
	# The timeline consumes each frame event once, including across pause/seek.
	# Advance before dispatch: a subscriber may cancel and start another attack.
	var hit_index := _next_hit_index
	_next_hit_index += 1
	hit_confirmed.emit(attacker, defender, attack_id, hit_index)
