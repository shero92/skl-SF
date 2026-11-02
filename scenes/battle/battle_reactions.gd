extends Node
## Battle-only reaction adapter.
## Hit payload: {outcome, defender_id, defender_is_hero, defender_view_id?}.
## Art table: {view_id: {reaction: existing Godot resource path}}.
## Connect reaction_started/reaction_cleared to the battle presentation layer.
## Execution provenance: Agent: codex; model: GPT-6.

signal reaction_started(reaction: Dictionary)
signal reaction_cleared
signal missing_reaction_art(details: Dictionary)

const MISSING_REACTION_ART := "MISSING_REACTION_ART"
const REACTIONS := {
	"hit": "hit",
	"block": "block",
}

@export var reaction_duration: float = 0.3

var _art: Dictionary = {}
var _active: Dictionary = {}
var _remaining: float = 0.0
var _generation: int = 0
var _connections: Array[Dictionary] = []


func configure(art: Dictionary) -> void:
	_art = art.duplicate(true)
	reset()


## Lifecycle signal names may be overridden to match the source's API.
## All three signals must exist; hit emits one Dictionary, lifecycle signals no args.
func bind_source(
	source: Object,
	hit_signal: StringName = &"hit",
	cancel_signal: StringName = &"cancelled",
	reset_signal: StringName = &"reset"
) -> bool:
	unbind_source()
	if not is_instance_valid(source):
		return false
	var bindings := [
		{"signal": hit_signal, "callback": Callable(self, "on_hit")},
		{"signal": cancel_signal, "callback": Callable(self, "cancel")},
		{"signal": reset_signal, "callback": Callable(self, "reset")},
	]
	for binding in bindings:
		if not source.has_signal(binding["signal"]):
			return false
	for binding in bindings:
		var callback: Callable = binding["callback"]
		var signal_name: StringName = binding["signal"]
		var error := source.connect(signal_name, callback)
		if error != OK:
			unbind_source()
			return false
		_connections.append({
			"source": weakref(source),
			"signal": signal_name,
			"callback": callback,
		})
	return true


func unbind_source() -> void:
	for connection in _connections:
		var source: Object = connection["source"].get_ref()
		if is_instance_valid(source):
			if source.is_connected(connection["signal"], connection["callback"]):
				source.disconnect(connection["signal"], connection["callback"])
	_connections.clear()
	cancel()


func active_reaction() -> Dictionary:
	return _active.duplicate(true)


func on_hit(payload: Dictionary) -> void:
	_generation += 1
	var generation := _generation
	_clear()
	# A presentation listener may cancel/reset synchronously while clearing.
	if generation != _generation:
		return
	var outcome := str(payload.get("outcome", ""))
	if not REACTIONS.has(outcome):
		return
	var reaction: String = REACTIONS[outcome]
	# The attacked hero must always use authored front art.
	var view_id := "front"
	if not bool(payload.get("defender_is_hero", false)):
		view_id = str(payload.get("defender_view_id", "front"))
	var views: Variant = _art.get(view_id, {})
	var asset_id := ""
	if views is Dictionary:
		asset_id = str(views.get(reaction, ""))
	if (
		asset_id.is_empty()
		or not asset_id.begins_with("res://")
		or not ResourceLoader.exists(asset_id)
	):
		var details := {
			"code": MISSING_REACTION_ART,
			"defender_id": str(payload.get("defender_id", "")),
			"view_id": view_id,
			"reaction": reaction,
			"asset_id": asset_id,
		}
		push_warning("%s: %s/%s" % [MISSING_REACTION_ART, view_id, reaction])
		missing_reaction_art.emit(details)
		return
	if not is_finite(reaction_duration) or reaction_duration <= 0.0:
		return
	_active = {
		"defender_id": str(payload.get("defender_id", "")),
		"view_id": view_id,
		"reaction": reaction,
		"asset_id": asset_id,
	}
	_remaining = reaction_duration
	set_process(true)
	reaction_started.emit(active_reaction())


func cancel() -> void:
	_generation += 1
	_clear()


func reset() -> void:
	cancel()


func _clear() -> void:
	var had_reaction := not _active.is_empty()
	_active = {}
	_remaining = 0.0
	set_process(false)
	if had_reaction:
		reaction_cleared.emit()


func _process(delta: float) -> void:
	if _active.is_empty() or not is_finite(delta) or delta < 0.0:
		return
	_remaining = maxf(0.0, _remaining - delta)
	if _remaining <= 0.0:
		_clear()


func _exit_tree() -> void:
	unbind_source()
