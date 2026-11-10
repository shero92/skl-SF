extends SceneTree
## Headless verification of world depth sorting for characters (RoomFactory.entities_parent).
## Agent: claude (Claude Code); model: Sonnet 5.5.
## A node's draw order is decided by its effective z (sum of relative z_index up to the first non-relative
## ancestor) and then, inside a Y-sorted parent, by its Y. So characters, walls and decor must share one
## effective z and one Y-sort root on unified maps.

var _failures: int = 0


func _check(condition: bool, message: String) -> void:
	if not condition:
		_failures += 1
		printerr("FAIL: " + message)


func _initialize() -> void:
	_test_unified_room()
	_test_legacy_room()
	_test_existing_entities()
	if _failures == 0:
		print("DEPTH_SORTING_OK")
	quit(0 if _failures == 0 else 1)


func _effective_z(node: Node) -> int:
	var total := 0
	var current: Node = node
	while current is CanvasItem:
		total += (current as CanvasItem).z_index
		if not (current as CanvasItem).z_as_relative:
			break
		current = current.get_parent()
	return total


func _ysorted_chain(node: Node, top: Node) -> bool:
	var current: Node = node
	while current != top:
		if not (current as CanvasItem).y_sort_enabled:
			return false
		current = current.get_parent()
	return (top as CanvasItem).y_sort_enabled


func _test_unified_room() -> void:
	var holder := Node2D.new()
	root.add_child(holder)
	var room := RoomFactory.new().build_latest("hero_room_01", holder)
	var depth := room.get_node_or_null("WorldDepthSort") as Node2D
	_check(depth != null, "latest hero room uses the unified WorldDepthSort root")
	if depth == null:
		holder.free()
		return
	var entities := RoomFactory.entities_parent(room)
	_check(entities.get_parent() == depth, "characters live inside WorldDepthSort")
	_check(RoomFactory.entities_parent(room) == entities, "entities parent is created once")
	var walls := depth.get_node("Level2_Walls") as Node2D
	var decor := depth.get_node("Level3_Decorations") as Node2D
	_check(_effective_z(entities) == _effective_z(walls) and _effective_z(entities) == _effective_z(decor),
		"characters, walls and decor share one effective z (only Y decides)")
	_check(_ysorted_chain(entities, depth) and _ysorted_chain(walls, depth) and _ysorted_chain(decor, depth),
		"every group up to the shared root is Y-sorted")
	var shadows := room.get_node("Level4_Shadows") as Node2D
	_check(_effective_z(shadows) < _effective_z(entities), "shadows stay below characters and walls")
	# A character and a wall piece: the one with the larger ground Y is drawn in front.
	var wall: Node2D = null
	for child in walls.get_children():
		if child is Node2D and (child as Node2D).position.y > 600.0:
			wall = child
			break
	_check(wall != null, "found a wall piece south of the middle")
	var hero := Node2D.new()
	entities.add_child(hero)
	hero.position = Vector2(700.0, 300.0)
	_check(hero.position.y < wall.position.y, "hero standing north of that wall sorts behind it")
	hero.position = Vector2(700.0, wall.position.y + 40.0)
	_check(hero.position.y > wall.position.y, "hero standing south of that wall sorts in front of it")
	holder.free()


func _test_legacy_room() -> void:
	var holder := Node2D.new()
	root.add_child(holder)
	var room := RoomFactory.new().build_room("res://map_factory/maps/courtyard_demo_01/latest.json", holder)
	var entities := RoomFactory.entities_parent(room)
	_check(entities != null and entities.y_sort_enabled, "legacy room still gets a Y-sorted entities node")
	_check(room.get_node_or_null("WorldDepthSort") != null or entities.z_index == 35 or entities.name == "Entities",
		"legacy room keeps its fixed layer when it has no unified sort")
	holder.free()


func _test_existing_entities() -> void:
	var room := Node2D.new()
	var existing := Node2D.new()
	existing.name = "Entities"
	room.add_child(existing)
	_check(RoomFactory.entities_parent(room) == existing, "an existing Entities node is reused")
	var plain := Node2D.new()
	var created := RoomFactory.entities_parent(plain)
	_check(created.z_index == 35 and created.y_sort_enabled and created.get_parent() == plain,
		"a room without unified sort gets the legacy z 35 Y-sorted layer")
	room.free()
	plain.free()
