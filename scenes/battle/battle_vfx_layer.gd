extends Node2D
## Battle-only effects. Socket coordinates are sampled in this layer's space.
## Effect resources are supplied by the existing asset registry through a resolver.
## Agent: codex. Model: GPT-6.

var _enabled: bool = true
var _socket: Node2D
var _slots: Dictionary = {}
var _trail: Line2D


func set_vfx_enabled(value: bool) -> void:
	_enabled = value
	visible = value


func is_vfx_enabled() -> bool:
	return _enabled


func bind_socket(socket: Node2D) -> void:
	_socket = socket


func get_effect_slot(slot_name: StringName) -> Node2D:
	if slot_name == &"":
		return null
	if _slots.has(slot_name) and is_instance_valid(_slots[slot_name]):
		return _slots[slot_name]
	var slot := Node2D.new()
	slot.name = slot_name
	add_child(slot)
	_slots[slot_name] = slot
	return slot


func add_effect(
	asset_id: StringName, slot_name: StringName, resolve_asset: Callable
) -> Node2D:
	# The resolver returns a fresh instance of an existing effect asset by ID.
	if asset_id == &"" or slot_name == &"" or not resolve_asset.is_valid():
		return null
	var effect: Variant = resolve_asset.call(asset_id)
	if not effect is Node2D:
		if effect is Node and is_instance_valid(effect) and effect.get_parent() == null:
			effect.free()
		return null
	if not is_instance_valid(effect) or effect.get_parent() != null:
		return null
	get_effect_slot(slot_name).add_child(effect)
	return effect


func start_trail(width: float = 2.0) -> void:
	if not is_instance_valid(_trail):
		_trail = Line2D.new()
		_trail.name = &"SocketTrail"
		get_effect_slot(&"trail").add_child(_trail)
	_trail.width = maxf(width, 0.0)
	_trail.clear_points()


func sample_socket() -> void:
	if not _enabled or not is_instance_valid(_socket):
		return
	var point := to_local(_socket.global_position)
	for slot in _slots.values():
		if is_instance_valid(slot) and slot != _slots.get(&"trail"):
			slot.position = point
	if is_instance_valid(_trail):
		_trail.add_point(point)


func get_trail_points() -> PackedVector2Array:
	if not is_instance_valid(_trail):
		return PackedVector2Array()
	return _trail.points.duplicate()


func _process(_delta: float) -> void:
	sample_socket()


func clear() -> void:
	# Detach immediately: callers see no children even before the next frame.
	_socket = null
	_trail = null
	_slots.clear()
	for child in get_children():
		remove_child(child)
		child.queue_free()
