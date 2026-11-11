extends Node2D
## Hands-on Map Factory editor: pick a part from the catalog, click to place it, drag to move it, resize,
## turn, flip or delete it, then save. Saving publishes a new immutable room version through the factory
## (tools/room_editor_save.py), so F5 shows the edited room. Walking still follows the grid; this edits the look.
## Agent: claude (Claude Code); model: Fable 5.2.
##
## Mouse: left click selects or places, drag moves, wheel resizes the selection (or zooms the view),
## right or middle drag pans. Keys: Q/E turn, F flip, Delete removes, arrows nudge, G grid snap,
## 1-5 target level, Ctrl+Z undo, Ctrl+S save, Esc cancel / back to the room.

const LAYERS := ["background_objects", "ground_overlays", "back_objects", "objects", "front_objects"]
const LAYER_LABEL := {"background_objects": "1 Background (sea, sky)", "ground_overlays": "2 Ground (rugs, decals)",
	"back_objects": "3 Walls and back", "objects": "4 Furniture, plants, decor", "front_objects": "5 Front"}
const HIDDEN_CATEGORIES := ["characters", "ui", "shadows"]
const ROOM_SCENE := "res://scenes/main.tscn"
const SAVE_TOOL := "res://tools/room_editor_save.py"
const SCALE_STEP := 0.05
const TURN_STEP := 15.0

@export var map_id: String = "hero_room_01"
var python_executable: String = "python"
var save_dry_run: bool = false  # tests validate without publishing a version

var room: Node2D
var map_data: Dictionary = {}
var blocks: Dictionary = {}      # instance_id -> {id, layer, x, y, scale, rotation_degrees, flip_h}
var original: Dictionary = {}    # the same, as loaded
var nodes: Dictionary = {}       # instance_id -> Node2D shown on screen
var selected: String = ""
var placing_part: String = ""
var active_layer: String = "objects"
var snap_to_grid: bool = false
var status: String = ""

var _catalog: AssetCatalog
var _assets: AssetFactory
var _undo: Array[Dictionary] = []
var _base_rotation: Dictionary = {}  # instance_id -> node rotation that belongs to the facing, not to the edit
var _added_root: Node2D
var _overlay: Node2D
var _camera: Camera2D
var _dragging: bool = false
var _drag_moved: bool = false
var _drag_offset: Vector2 = Vector2.ZERO
var _panning: bool = false
var _counter: int = 0
var _parts_list: ItemList
var _category: OptionButton
var _layer_pick: OptionButton
var _status_label: Label
var _part_ids: Array[String] = []


func _ready() -> void:
	_catalog = AssetCatalog.shared()
	_assets = AssetFactory.new(_catalog)
	_camera = Camera2D.new()
	_camera.position = Vector2(768, 512)
	_camera.zoom = Vector2.ONE * 0.8
	add_child(_camera)
	_build_ui()
	load_map()


# ---------------------------------------------------------------- model

func load_map() -> bool:
	if room != null:
		remove_child(room)
		room.free()
	nodes.clear()
	blocks.clear()
	original.clear()
	_base_rotation.clear()
	_undo.clear()
	selected = ""
	var path := "res://map_factory/maps/%s/latest.json" % map_id
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if typeof(data) != TYPE_DICTIONARY:
		_say("Cannot read " + path)
		return false
	map_data = data
	room = RoomFactory.new().build_room(path, self)
	if room == null:
		_say("Cannot build " + path)
		return false
	_added_root = Node2D.new()
	_added_root.name = "EditorAdded"
	_added_root.z_index = 60
	room.add_child(_added_root)
	_overlay = Node2D.new()
	_overlay.name = "EditorOverlay"
	_overlay.z_index = 4000
	_overlay.draw.connect(_draw_overlay)
	room.add_child(_overlay)
	for layer: String in LAYERS:
		for item: Dictionary in map_data.get(layer, []):
			var id := String(item.get("instance_id", ""))
			var node := room.find_child(id, true, false) as Node2D
			if id == "" or node == null:
				continue  # mounted or merged pieces are not editable here
			blocks[id] = {"id": String(item["id"]), "layer": layer, "x": float(item["x"]), "y": float(item["y"]),
				"scale": float(item.get("scale", 1.0)), "rotation_degrees": float(item.get("rotation_degrees", 0.0)),
				"flip_h": bool(item.get("flip_h", false))}
			nodes[id] = node
			_base_rotation[id] = node.rotation_degrees - (float(item.get("rotation_degrees", 0.0)) if _turn_shows(item) else 0.0)
	original = blocks.duplicate(true)
	_say("%s v%04d loaded: %d editable pieces" % [map_id, int(map_data.get("version", 0)), blocks.size()])
	return true


func _turn_shows(item: Dictionary) -> bool:
	return not item.has("facing") or bool(item.get("free_transform", false))


func _remember() -> void:
	_undo.append({"blocks": blocks.duplicate(true), "selected": selected})
	if _undo.size() > 200:
		_undo.pop_front()


func undo() -> bool:
	if _undo.is_empty():
		return false
	var state: Dictionary = _undo.pop_back()
	var before: Dictionary = state["blocks"]
	for id: String in nodes.keys():
		if not before.has(id) and not original.has(id):
			nodes[id].queue_free()  # a piece added after that point
			nodes.erase(id)
	blocks = before
	for id: String in blocks:
		if not nodes.has(id):
			nodes[id] = _spawn(id, blocks[id])
		_show(id)
	for id: String in original:
		if nodes.has(id):
			nodes[id].visible = blocks.has(id)
	selected = String(state["selected"]) if blocks.has(String(state["selected"])) else ""
	_refresh()
	return true


func _spawn(id: String, block: Dictionary) -> Node2D:
	var node := _assets.create_asset(String(block["id"]), {})
	node.name = id
	_added_root.add_child(node)
	_base_rotation[id] = 0.0
	return node


## Pushes one block's numbers onto its node.
func _show(id: String) -> void:
	var block: Dictionary = blocks[id]
	var node: Node2D = nodes[id]
	node.visible = true
	node.position = Vector2(float(block["x"]), float(block["y"]))
	node.scale = Vector2.ONE * float(block["scale"])
	node.rotation_degrees = float(_base_rotation.get(id, 0.0)) + float(block["rotation_degrees"])
	var sprite := _sprite_of(node)
	if sprite != null:
		sprite.flip_h = bool(block["flip_h"])


func _sprite_of(node: Node) -> Sprite2D:
	if node is Sprite2D:
		return node
	for child in node.get_children():
		var found := _sprite_of(child)
		if found != null:
			return found
	return null


## Screen rectangle of a piece in room coordinates (axis-aligned box around the turned sprite).
func rect_of(id: String) -> Rect2:
	var node: Node2D = nodes.get(id)
	if node == null:
		return Rect2()
	var sprite := _sprite_of(node)
	if sprite == null or sprite.texture == null:
		return Rect2(node.global_position - Vector2(16, 32), Vector2(32, 32))
	var local := sprite.get_rect()
	var to_room: Transform2D = sprite.global_transform
	var box := Rect2(to_room * local.position, Vector2.ZERO)
	for corner: Vector2 in [Vector2(local.end.x, local.position.y), local.end, Vector2(local.position.x, local.end.y)]:
		box = box.expand(to_room * corner)
	return box


## Topmost piece under the point: the target level first, then front to back.
func pick_at(point: Vector2) -> String:
	var order: Array = [active_layer]
	for index in range(LAYERS.size() - 1, -1, -1):
		if LAYERS[index] != active_layer:
			order.append(LAYERS[index])
	for layer: String in order:
		var best := ""
		var best_y := -INF
		for id: String in blocks:
			if String(blocks[id]["layer"]) == layer and rect_of(id).has_point(point) and float(blocks[id]["y"]) > best_y:
				best = id
				best_y = float(blocks[id]["y"])
		if best != "":
			return best
	return ""


func select_at(point: Vector2) -> String:
	selected = pick_at(point)
	_refresh()
	return selected


func snapped_point(point: Vector2) -> Vector2:
	if not snap_to_grid:
		return point.round()
	var tile := float(map_data.get("tile_size", 64))
	var offset: Array = map_data.get("ground_offset", [0, 0])
	var origin := Vector2(float(offset[0]), float(offset[1]))
	var cell := ((point - origin) / tile).floor()
	return origin + Vector2((cell.x + 0.5) * tile, (cell.y + 1.0) * tile)  # bottom centre of the square


## Adds a new independent piece on the target level. Returns its instance id ("" when the part is unknown).
func place(part_id: String, point: Vector2) -> String:
	if _catalog.get_asset(part_id).is_empty():
		return ""
	_remember()
	_counter += 1
	var id := "Ed%s_%d" % [part_id.replace("_", ""), _counter]
	while blocks.has(id) or original.has(id):
		_counter += 1
		id = "Ed%s_%d" % [part_id.replace("_", ""), _counter]
	var at := snapped_point(point)
	blocks[id] = {"id": part_id, "layer": active_layer, "x": at.x, "y": at.y, "scale": 1.0, "rotation_degrees": 0.0, "flip_h": false}
	nodes[id] = _spawn(id, blocks[id])
	_show(id)
	selected = id
	_refresh()
	return id


func move_selected(point: Vector2, remember: bool = true) -> bool:
	if selected == "":
		return false
	if remember:
		_remember()
	var at := snapped_point(point)
	blocks[selected]["x"] = at.x
	blocks[selected]["y"] = at.y
	_show(selected)
	_refresh()
	return true


func scale_selected(steps: int) -> bool:
	if selected == "":
		return false
	_remember()
	blocks[selected]["scale"] = clampf(snappedf(float(blocks[selected]["scale"]) + steps * SCALE_STEP, SCALE_STEP), 0.1, 4.0)
	_show(selected)
	_refresh()
	return true


func rotate_selected(degrees: float) -> bool:
	if selected == "":
		return false
	_remember()
	blocks[selected]["rotation_degrees"] = fposmod(float(blocks[selected]["rotation_degrees"]) + degrees + 180.0, 360.0) - 180.0
	_show(selected)
	_refresh()
	return true


func flip_selected() -> bool:
	if selected == "":
		return false
	_remember()
	blocks[selected]["flip_h"] = not bool(blocks[selected]["flip_h"])
	_show(selected)
	_refresh()
	return true


func delete_selected() -> bool:
	if selected == "":
		return false
	_remember()
	var id := selected
	blocks.erase(id)
	if original.has(id):
		nodes[id].visible = false
	else:
		nodes[id].queue_free()
		nodes.erase(id)
	selected = ""
	_refresh()
	return true


## The edits since loading, as the list tools/room_editor_save.py understands.
func pending_changes() -> Array:
	var changes: Array = []
	for id: String in original:
		if not blocks.has(id):
			changes.append({"op": "remove", "instance_id": id})
	for id: String in blocks:
		var now: Dictionary = blocks[id]
		if not original.has(id):
			changes.append({"op": "add", "instance_id": id, "layer": now["layer"], "id": now["id"], "x": now["x"], "y": now["y"],
				"scale": now["scale"], "rotation_degrees": now["rotation_degrees"], "flip_h": now["flip_h"]})
			continue
		var was: Dictionary = original[id]
		var updates: Dictionary = {}
		for key: String in ["x", "y", "scale", "rotation_degrees", "flip_h"]:
			if now[key] != was[key]:
				updates[key] = now[key]
		if not updates.is_empty():
			changes.append({"op": "update", "instance_id": id, "set": updates})
	return changes


## Publishes the edits as a new room version. Returns {ok, message}.
func save() -> Dictionary:
	var changes := pending_changes()
	if changes.is_empty():
		_say("Nothing to save")
		return {"ok": false, "message": "Nothing to save"}
	var request := {"map_id": map_id, "changes": changes,
		"note": "%s edited by hand in the in-game room editor: %d change(s). Visual approval is still pending." % [map_id, changes.size()]}
	var path := ProjectSettings.globalize_path("user://room_editor_changes.json")
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		_say("Cannot write " + path)
		return {"ok": false, "message": "Cannot write " + path}
	file.store_string(JSON.stringify(request, "  "))
	file.close()
	var arguments: Array = [ProjectSettings.globalize_path(SAVE_TOOL), "--changes", path]
	if save_dry_run:
		arguments.append("--dry-run")
	var output: Array = []
	var code := OS.execute(python_executable, arguments, output, true)
	var text := "\n".join(output).strip_edges()
	var last := text.get_slice("\n", text.get_slice_count("\n") - 1) if text != "" else "Could not run %s (exit %d)" % [python_executable, code]
	if code == 0 and not save_dry_run:
		load_map()
	_say(last)
	return {"ok": code == 0, "message": last}


# ---------------------------------------------------------------- screen

func _say(text: String) -> void:
	status = text
	_refresh()


func _refresh() -> void:
	if _overlay != null:
		_overlay.queue_redraw()
	if _status_label == null:
		return
	var line := status
	if placing_part != "":
		line = "Placing %s on level %s: click on the map (Esc cancels)" % [placing_part, LAYER_LABEL[active_layer]]
	elif selected != "":
		var block: Dictionary = blocks[selected]
		line = "%s  [%s]  x %d  y %d  size %.2f  turn %d  %s   |  %d unsaved change(s)" % [selected, block["id"], int(block["x"]),
			int(block["y"]), float(block["scale"]), int(block["rotation_degrees"]), LAYER_LABEL[String(block["layer"])], pending_changes().size()]
	_status_label.text = line


func _draw_overlay() -> void:
	if selected != "" and nodes.has(selected):
		var box := rect_of(selected)
		_overlay.draw_rect(box.grow(2), Color(1, 0.9, 0.2), false, 2.0)
		_overlay.draw_circle(Vector2(float(blocks[selected]["x"]), float(blocks[selected]["y"])), 4, Color(1, 0.3, 0.2))
	if snap_to_grid:
		var tile := float(map_data.get("tile_size", 64))
		var offset: Array = map_data.get("ground_offset", [0, 0])
		var size: Array = map_data.get("size", [17, 10])
		for x in int(size[0]) + 1:
			_overlay.draw_line(Vector2(float(offset[0]) + x * tile, float(offset[1])),
				Vector2(float(offset[0]) + x * tile, float(offset[1]) + float(size[1]) * tile), Color(1, 1, 1, 0.25))
		for y in int(size[1]) + 1:
			_overlay.draw_line(Vector2(float(offset[0]), float(offset[1]) + y * tile),
				Vector2(float(offset[0]) + float(size[0]) * tile, float(offset[1]) + y * tile), Color(1, 1, 1, 0.25))


func _build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := PanelContainer.new()
	panel.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	panel.custom_minimum_size = Vector2(250, 0)
	layer.add_child(panel)
	var column := VBoxContainer.new()
	panel.add_child(column)
	var title := Label.new()
	title.text = "Room editor"
	column.add_child(title)
	_layer_pick = OptionButton.new()
	for name: String in LAYERS:
		_layer_pick.add_item(LAYER_LABEL[name])
	_layer_pick.select(LAYERS.find(active_layer))
	_layer_pick.item_selected.connect(func(index: int): set_active_layer(LAYERS[index]))
	column.add_child(_layer_pick)
	_category = OptionButton.new()
	var categories: Array[String] = []
	for record: Dictionary in _catalog.all_assets():
		var category := String(record.get("category", ""))
		if category != "" and not HIDDEN_CATEGORIES.has(category) and not categories.has(category):
			categories.append(category)
	categories.sort()
	for category: String in categories:
		_category.add_item(category)
	_category.item_selected.connect(func(index: int): show_category(_category.get_item_text(index)))
	column.add_child(_category)
	_parts_list = ItemList.new()
	_parts_list.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_parts_list.fixed_icon_size = Vector2i(48, 48)
	_parts_list.item_selected.connect(func(index: int): start_placing(_part_ids[index]))
	column.add_child(_parts_list)
	for row: Array in [["Grid snap (G)", func(): toggle_snap()], ["Undo (Ctrl+Z)", func(): undo()],
			["Save new version (Ctrl+S)", func(): save()], ["Back to the room (Esc)", func(): get_tree().change_scene_to_file(ROOM_SCENE)]]:
		var button := Button.new()
		button.text = row[0]
		button.pressed.connect(row[1])
		column.add_child(button)
	var help := Label.new()
	help.text = "Click: select / place   Drag: move\nWheel: resize   Q/E: turn   F: flip\nDelete: remove   Arrows: nudge\nRight drag: pan   1-5: level"
	help.add_theme_font_size_override("font_size", 12)
	column.add_child(help)
	_status_label = Label.new()
	_status_label.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_status_label.offset_left = 260
	_status_label.offset_top = -30
	_status_label.add_theme_color_override("font_outline_color", Color.BLACK)
	_status_label.add_theme_constant_override("outline_size", 6)
	layer.add_child(_status_label)
	if not categories.is_empty():
		show_category(categories[0])


func show_category(category: String) -> void:
	_parts_list.clear()
	_part_ids.clear()
	for record: Dictionary in _catalog.all_assets():
		if String(record.get("category", "")) != category:
			continue
		var path := String(record.get("texture_path", ""))
		if not HdAssets.exists(path):
			continue
		_part_ids.append(String(record["id"]))
		_parts_list.add_item("%s  %s" % [record["id"], record.get("name", "")], load(HdAssets.resolve(path)) as Texture2D)


func start_placing(part_id: String) -> void:
	placing_part = part_id
	selected = ""
	_refresh()


func set_active_layer(layer: String) -> void:
	if LAYERS.has(layer):
		active_layer = layer
		if _layer_pick != null:
			_layer_pick.select(LAYERS.find(layer))
		_refresh()


func toggle_snap() -> void:
	snap_to_grid = not snap_to_grid
	_say("Grid snap " + ("on" if snap_to_grid else "off"))


func _unhandled_input(event: InputEvent) -> void:
	var point := get_global_mouse_position()
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				if placing_part != "":
					place(placing_part, point)
				elif select_at(point) != "":
					_dragging = true
					_drag_moved = false
					_drag_offset = Vector2(float(blocks[selected]["x"]), float(blocks[selected]["y"])) - point
			else:
				_dragging = false
		elif event.button_index in [MOUSE_BUTTON_RIGHT, MOUSE_BUTTON_MIDDLE]:
			_panning = event.pressed
		elif event.pressed and event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN]:
			var direction := 1 if event.button_index == MOUSE_BUTTON_WHEEL_UP else -1
			if selected != "":
				scale_selected(direction)
			else:
				_camera.zoom = Vector2.ONE * clampf(_camera.zoom.x * (1.1 if direction > 0 else 1.0 / 1.1), 0.3, 4.0)
	elif event is InputEventMouseMotion:
		if _panning:
			_camera.position -= event.relative / _camera.zoom
		elif _dragging and selected != "":
			move_selected(point + _drag_offset, not _drag_moved)  # one undo step per drag
			_drag_moved = true
	elif event is InputEventKey and event.pressed:
		_key(event)


func _key(event: InputEventKey) -> void:
	var nudge := {KEY_LEFT: Vector2.LEFT, KEY_RIGHT: Vector2.RIGHT, KEY_UP: Vector2.UP, KEY_DOWN: Vector2.DOWN}
	if nudge.has(event.keycode) and selected != "":
		var was_snapping := snap_to_grid
		snap_to_grid = false
		move_selected(Vector2(float(blocks[selected]["x"]), float(blocks[selected]["y"])) + nudge[event.keycode])
		snap_to_grid = was_snapping
		return
	if event.echo:
		return
	match event.keycode:
		KEY_Q:
			rotate_selected(-TURN_STEP)
		KEY_E:
			rotate_selected(TURN_STEP)
		KEY_F:
			flip_selected()
		KEY_DELETE, KEY_BACKSPACE:
			delete_selected()
		KEY_G:
			toggle_snap()
		KEY_Z:
			if event.ctrl_pressed:
				undo()
		KEY_S:
			if event.ctrl_pressed:
				save()
		KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
			set_active_layer(LAYERS[event.keycode - KEY_1])
		KEY_ESCAPE:
			if placing_part != "":
				placing_part = ""
				_refresh()
			elif selected != "":
				selected = ""
				_refresh()
			else:
				get_tree().change_scene_to_file(ROOM_SCENE)
