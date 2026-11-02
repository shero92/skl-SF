extends SceneTree
## Runtime acceptance checks; no production scenes or assets are modified.

const VFXLayer = preload("res://scenes/battle/battle_vfx_layer.gd")
const SUCCESS := "BATTLE_VFX_OK"

var _failures: int = 0
var _resolved_ids: Array[StringName] = []


func _initialize() -> void:
	call_deferred("_verify")


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		push_error(message)


func _resolve_existing_effect(asset_id: StringName) -> Node2D:
	# Registry test double: records IDs without loading or generating artwork.
	_resolved_ids.append(asset_id)
	return Node2D.new()


func _verify() -> void:
	var stage := Node2D.new()
	root.add_child(stage)
	var body := Node2D.new()
	body.position = Vector2(20, 30)
	body.rotation = 0.3
	stage.add_child(body)
	var weapon := Node2D.new()
	weapon.position = Vector2(8, -4)
	weapon.scale = Vector2(2, 1)
	body.add_child(weapon)
	var socket := Marker2D.new()
	weapon.add_child(socket)

	var layer := VFXLayer.new()
	layer.position = Vector2(-12, 7)
	layer.rotation = -0.4
	layer.scale = Vector2(1.5, 0.75)
	stage.add_child(layer)
	layer.set_process(false)
	layer.bind_socket(socket)
	layer.start_trail()
	var effect := layer.add_effect(&"existing_spark", &"impact", _resolve_existing_effect)
	_check(effect != null, "Existing effect ID must resolve to an effect instance")
	_check(_resolved_ids == [&"existing_spark"], "Resolver must receive the exact asset ID")
	_check(effect.get_parent() == layer.get_effect_slot(&"impact"), "Effects need named slots")
	_check(layer.get_effect_slot(&"impact") == layer.get_effect_slot(&"impact"),
		"Named slots must be reused")

	var expected := PackedVector2Array()
	for position in [Vector2.ZERO, Vector2(4, 2), Vector2(4, 2), Vector2(-9, 11)]:
		socket.position = position
		expected.append(layer.to_local(socket.global_position))
		layer._process(1.0 / 60.0)
	_check(layer.get_trail_points() == expected, "Trail must retain every socket sample")
	_check(layer.get_effect_slot(&"impact").position == expected[-1],
		"Effect slots must follow the socket")
	var copy := layer.get_trail_points()
	copy.append(Vector2(999, 999))
	_check(layer.get_trail_points() == expected, "Returned points must be a snapshot")

	var body_transform := body.transform
	var weapon_transform := weapon.transform
	var body_children := body.get_children()
	var weapon_children := weapon.get_children()
	layer.set_vfx_enabled(false)
	_check(not layer.visible and not layer.is_vfx_enabled(), "Toggle must hide VFX")
	socket.position = Vector2(100, 100)
	layer._process(1.0 / 60.0)
	_check(layer.get_trail_points() == expected, "Disabled VFX must stop sampling")
	_check(body.visible and weapon.visible, "Toggle must leave body and weapon visible")
	_check(body.transform == body_transform and weapon.transform == weapon_transform,
		"Toggle must preserve body and weapon transforms")
	_check(body.get_children() == body_children and weapon.get_children() == weapon_children,
		"VFX must never be attached to body or weapon")
	layer.set_vfx_enabled(true)
	layer._process(1.0 / 60.0)
	expected.append(layer.to_local(socket.global_position))
	_check(layer.visible and layer.get_trail_points() == expected,
		"Re-enabling must resume socket sampling")

	layer.clear()
	_check(layer.get_child_count() == 0, "clear() must immediately leave no children")
	_check(layer.get_trail_points().is_empty(), "clear() must discard trail samples")
	_check(is_instance_valid(body) and is_instance_valid(weapon),
		"clear() must preserve body and weapon")
	layer._process(0.0)
	_check(layer.get_child_count() == 0, "Processing after clear must not recreate children")
	layer.clear()
	layer.bind_socket(socket)
	layer.start_trail()
	layer.sample_socket()
	_check(layer.get_trail_points().size() == 1, "Layer must be reusable after clear")
	socket.free()
	layer.sample_socket()
	_check(layer.get_trail_points().size() == 1, "Freed sockets must stop sampling safely")
	layer.clear()
	stage.free()
	if _failures == 0:
		print(SUCCESS)
	quit(0 if _failures == 0 else 1)
