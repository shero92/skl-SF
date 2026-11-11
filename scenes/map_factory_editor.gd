extends Node2D
## Hands-on Map Factory editor: pick a part from the catalog, click to place it, drag to move it, resize,
## turn, flip or delete it, then save. Saving publishes a new immutable room version through the factory
## (tools/room_editor_save.py), so F5 shows the edited room. Walking still follows the grid; this edits the look.
## Agent: claude (Claude Code); model: Fable 5.2.
##
## Mouse: left click selects or places, drag moves, wheel resizes the selection (or zooms the view),
## right or middle drag pans. Keys: Q/E turn, F flip, Delete removes, arrows nudge, G grid snap,
## 1-5 target level, Ctrl+Z undo, Ctrl+Y redo, Ctrl+D duplicate, PageUp/PageDown move the piece to another
## level, Shift+1-5 hide or show a level, Ctrl+S save, Esc cancel / back to the room.
## Ground: pick a part from "floors" and click or drag over squares to paint them; "Erase floor squares"
## removes squares from the floor shape. Maps: open any map of the registry or create one from a preset.
## Battle setup: mark blocked squares and the start squares of both teams on the map's own grid, save the
## battle (game_factory/battles/<map>.json) and play it at once. Squares without floor are always blocked.

const LAYERS := ["background_objects", "ground_overlays", "back_objects", "objects", "front_objects"]
const LAYER_LABEL := {"background_objects": "1 Background (sea, sky)", "ground_overlays": "2 Ground (rugs, decals)",
	"back_objects": "3 Walls and back", "objects": "4 Furniture, plants, decor", "front_objects": "5 Front"}
const HIDDEN_CATEGORIES := ["characters", "ui", "shadows"]
const ROOM_SCENE := "res://scenes/main.tscn"
const SAVE_TOOL := "res://tools/room_editor_save.py"
const PRESETS := ["indoor_room", "courtyard", "dungeon", "coast", "sky_island"]
const REGISTRY := "res://map_factory/maps/index.json"
const BATTLE_SCENE := "res://scenes/battle/tactical_battle.tscn"
const BattleSession = preload("res://scenes/battle/tactical_battle.gd")
## Units handed out in this order each time a start square is clicked: [character, weapon].
const PLAYER_ROSTER := [["CHAR001", "WPN_IRON_SWORD"], ["CHAR002", "WPN_BRONZE_SPEAR"], ["CHAR006", "WPN_SHORT_BOW"]]
const ENEMY_ROSTER := [["CHAR004", "WPN_HAND_AXE"], ["CHAR003", ""], ["CHAR006", "WPN_SHORT_BOW"]]
const MAX_TEAM := 8
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
var tiles: Dictionary = {}       # "x:y" -> floor part id painted on that square
var cells: Dictionary = {}       # "x:y" -> true for every square that has floor
var original_tiles: Dictionary = {}
var original_cells: Dictionary = {}
var hidden_layers: Dictionary = {}
var erasing_floor: bool = false
var battles_dir: String = "res://game_factory/battles"
var battle_tool: String = ""     # "" (off), "blocked", "player", "enemy" or "clear"
var battle_blocked: Dictionary = {}  # "x:y" -> true, squares the owner blocked by hand
var battle_units: Array[Dictionary] = []  # {id, team, character, weapon, cell: [x, y]}
var selected: String = ""
var placing_part: String = ""
var active_layer: String = "objects"
var snap_to_grid: bool = false
var status: String = ""

var _catalog: AssetCatalog
var _assets: AssetFactory
var _undo: Array[Dictionary] = []
var _redo: Array[Dictionary] = []
var _stroke_open: bool = false
var _map_pick: OptionButton
var _new_name: LineEdit
var _new_preset: OptionButton
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
	_redo.clear()
	hidden_layers.clear()
	erasing_floor = false
	placing_part = ""
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
	_load_ground()
	load_battle_setup()
	var canvas: Array = map_data.get("canvas_size", [1536, 1024])
	# Fit the canvas into the window area that the 250 px panel leaves free, and centre it there.
	var free_width := maxf(200.0, get_viewport_rect().size.x - 250.0)
	_camera.zoom = Vector2.ONE * clampf(minf(free_width / float(canvas[0]), get_viewport_rect().size.y / float(canvas[1])), 0.3, 1.0)
	_camera.position = Vector2(float(canvas[0]), float(canvas[1])) / 2.0 - Vector2(125.0 / _camera.zoom.x, 0)
	_say("%s v%04d loaded: %d editable pieces" % [map_id, int(map_data.get("version", 0)), blocks.size()])
	return true


func _turn_shows(item: Dictionary) -> bool:
	return not item.has("facing") or bool(item.get("free_transform", false))


func _state() -> Dictionary:
	return {"blocks": blocks.duplicate(true), "tiles": tiles.duplicate(), "cells": cells.duplicate(), "selected": selected}


func _remember() -> void:
	_undo.append(_state())
	_redo.clear()
	if _undo.size() > 200:
		_undo.pop_front()


func undo() -> bool:
	if _undo.is_empty():
		return false
	_redo.append(_state())
	_restore(_undo.pop_back())
	return true


func redo() -> bool:
	if _redo.is_empty():
		return false
	_undo.append(_state())
	_restore(_redo.pop_back())
	return true


func _restore(state: Dictionary) -> void:
	tiles = state["tiles"]
	cells = state["cells"]
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
		if nodes.has(id) and not blocks.has(id):
			nodes[id].visible = false
	selected = String(state["selected"]) if blocks.has(String(state["selected"])) else ""
	_refresh()


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
	node.visible = not hidden_layers.has(String(block["layer"]))
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


# ---------------------------------------------------------------- ground

func _cell_key(cell: Vector2i) -> String:
	return "%d:%d" % [cell.x, cell.y]


func _load_ground() -> void:
	tiles.clear()
	cells.clear()
	var size: Array = map_data.get("size", [0, 0])
	var spans: Array = map_data.get("floor_footprint", {}).get("row_spans", [])
	for y in int(size[1]):
		for x in int(size[0]):
			var inside := spans.is_empty()
			if not inside:
				for span: Array in spans[y]:
					if x >= int(span[0]) and x <= int(span[1]):
						inside = true
			if inside:
				cells[_cell_key(Vector2i(x, y))] = true
	for entry: Dictionary in map_data.get("tile_overrides", []):
		tiles[_cell_key(Vector2i(int(entry["x"]), int(entry["y"])))] = String(entry["id"])
	original_tiles = tiles.duplicate()
	original_cells = cells.duplicate()


func grid_origin() -> Vector2:
	var offset: Array = map_data.get("ground_offset", [0, 0])
	return Vector2(float(offset[0]), float(offset[1]))


func cell_at(point: Vector2) -> Vector2i:
	return Vector2i(((point - grid_origin()) / float(map_data.get("tile_size", 64))).floor())


func cell_rect(cell: Vector2i) -> Rect2:
	var tile := float(map_data.get("tile_size", 64))
	return Rect2(grid_origin() + Vector2(cell) * tile, Vector2(tile, tile))


func in_grid(cell: Vector2i) -> bool:
	var size: Array = map_data.get("size", [0, 0])
	return cell.x >= 0 and cell.y >= 0 and cell.x < int(size[0]) and cell.y < int(size[1])


func is_floor_part(part_id: String) -> bool:
	return String(_catalog.get_asset(part_id).get("category", "")) == "floors"


## Paints one square with a floor part; a square outside the floor shape joins it.
func paint_tile(cell: Vector2i, part_id: String, remember: bool = true) -> bool:
	if not in_grid(cell) or not is_floor_part(part_id):
		return false
	var key := _cell_key(cell)
	if cells.has(key) and String(tiles.get(key, "")) == part_id:
		return false
	if remember:
		_remember()
	cells[key] = true
	tiles[key] = part_id
	_refresh()
	return true


## Removes one square from the floor shape (the sea or backdrop shows there).
func erase_cell(cell: Vector2i, remember: bool = true) -> bool:
	var key := _cell_key(cell)
	if not cells.has(key) or cells.size() <= 1:
		return false
	if remember:
		_remember()
	cells.erase(key)
	tiles.erase(key)
	_refresh()
	return true


func _row_spans() -> Array:
	var size: Array = map_data.get("size", [0, 0])
	var rows: Array = []
	for y in int(size[1]):
		var spans: Array = []
		var start := -1
		for x in int(size[0]) + 1:
			var filled := x < int(size[0]) and cells.has(_cell_key(Vector2i(x, y)))
			if filled and start < 0:
				start = x
			elif not filled and start >= 0:
				spans.append([start, x - 1])
				start = -1
		rows.append(spans)
	return rows


# ---------------------------------------------------------------- battle setup

func battle_file() -> String:
	return battles_dir.path_join(map_id + ".json")


func load_battle_setup() -> bool:
	battle_tool = ""
	battle_blocked.clear()
	battle_units.clear()
	if not FileAccess.file_exists(battle_file()):
		return false
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(battle_file()))
	if not data is Dictionary:
		return false
	for cell: Array in data.get("blocked_by_hand", []):
		battle_blocked[_cell_key(Vector2i(int(cell[0]), int(cell[1])))] = true
	for unit: Dictionary in data.get("units", []):
		battle_units.append(unit.duplicate(true))
	return true


func set_battle_tool(tool: String) -> void:
	battle_tool = tool if ["blocked", "player", "enemy", "clear"].has(tool) else ""
	placing_part = ""
	erasing_floor = false
	selected = ""
	_refresh()


func unit_at(cell: Vector2i) -> int:
	for index in battle_units.size():
		if int(battle_units[index]["cell"][0]) == cell.x and int(battle_units[index]["cell"][1]) == cell.y:
			return index
	return -1


func is_battle_blocked(cell: Vector2i) -> bool:
	return battle_blocked.has(_cell_key(cell)) or not cells.has(_cell_key(cell))


## One click of the current battle tool on a square. Returns true when something changed.
func battle_click(cell: Vector2i) -> bool:
	if not in_grid(cell):
		return false
	var key := _cell_key(cell)
	var changed := false
	match battle_tool:
		"blocked":
			if cells.has(key) and unit_at(cell) < 0:
				if battle_blocked.has(key):
					battle_blocked.erase(key)
				else:
					battle_blocked[key] = true
				changed = true
		"clear":
			if unit_at(cell) >= 0:
				battle_units.remove_at(unit_at(cell))
				changed = true
			elif battle_blocked.has(key):
				battle_blocked.erase(key)
				changed = true
		"player", "enemy":
			var team := battle_tool
			var count := battle_units.filter(func(u: Dictionary) -> bool: return u["team"] == team).size()
			if not is_battle_blocked(cell) and unit_at(cell) < 0 and count < MAX_TEAM:
				var roster: Array = PLAYER_ROSTER if team == "player" else ENEMY_ROSTER
				var pick: Array = roster[count % roster.size()]
				var number := 1
				while battle_units.any(func(u: Dictionary) -> bool: return u["id"] == "%s_%d" % [team, number]):
					number += 1
				var id := "hero" if team == "player" and count == 0 and not battle_units.any(func(u: Dictionary) -> bool: return u["id"] == "hero") \
					else "%s_%d" % [team, number]
				battle_units.append({"id": id, "team": team, "character": pick[0], "weapon": pick[1], "cell": [cell.x, cell.y]})
				changed = true
	if changed:
		_refresh()
	return changed


## The battle as the skirmish scene reads it: the map's own squares, every square without floor blocked.
func battle_definition() -> Dictionary:
	var size: Array = map_data.get("size", [0, 0])
	var blocked: Array = []
	var by_hand: Array = []
	for y in int(size[1]):
		for x in int(size[0]):
			var cell := Vector2i(x, y)
			if is_battle_blocked(cell):
				blocked.append([x, y])
			if battle_blocked.has(_cell_key(cell)):
				by_hand.append([x, y])
	return {"schema_version": 1, "battle_id": map_id, "map_id": map_id, "map_version": int(map_data.get("version", 0)),
		"cols": int(size[0]), "rows": int(size[1]), "origin": [grid_origin().x, grid_origin().y],
		"cell_size": float(map_data.get("tile_size", 64)), "blocked": blocked, "blocked_by_hand": by_hand,
		"units": battle_units.duplicate(true)}


## Writes the battle file. Returns {ok, message}.
func save_battle() -> Dictionary:
	var battle := battle_definition()
	var problem: String = BattleSession.definition_error(battle)
	if problem != "":
		_say("Battle not saved: " + problem)
		return {"ok": false, "message": problem}
	if not pending_changes().is_empty():
		_say("Battle not saved: save the map first (Ctrl+S), the battle uses the saved floor")
		return {"ok": false, "message": "unsaved map edits"}
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(battles_dir))
	var file := FileAccess.open(battle_file(), FileAccess.WRITE)
	if file == null:
		_say("Cannot write " + battle_file())
		return {"ok": false, "message": "cannot write " + battle_file()}
	file.store_string(JSON.stringify(battle, "  ") + "\n")
	file.close()
	_say("Battle saved: %s (%d units, %d blocked squares)" % [battle_file(), battle_units.size(), battle["blocked"].size()])
	return {"ok": true, "message": battle_file()}


func play_battle() -> void:
	if save_battle()["ok"]:
		load(BATTLE_SCENE.replace(".tscn", "_scene.gd")).next_battle_path = battle_file()
		get_tree().change_scene_to_file(BATTLE_SCENE)


# ---------------------------------------------------------------- levels and copies

func move_selected_to_layer(layer: String) -> bool:
	if selected == "" or not LAYERS.has(layer) or String(blocks[selected]["layer"]) == layer:
		return false
	_remember()
	blocks[selected]["layer"] = layer
	_show(selected)
	_refresh()
	return true


func duplicate_selected() -> String:
	if selected == "":
		return ""
	var source: Dictionary = blocks[selected].duplicate(true)
	var keep_layer := active_layer
	active_layer = String(source["layer"])
	var was_snapping := snap_to_grid
	snap_to_grid = false
	var copy := place(String(source["id"]), Vector2(float(source["x"]) + 24.0, float(source["y"]) + 24.0))
	snap_to_grid = was_snapping
	active_layer = keep_layer
	if copy != "":
		for key: String in ["scale", "rotation_degrees", "flip_h"]:
			blocks[copy][key] = source[key]
		_show(copy)
		_refresh()
	return copy


func set_layer_hidden(layer: String, hidden: bool) -> void:
	if hidden:
		hidden_layers[layer] = true
	else:
		hidden_layers.erase(layer)
	for id: String in blocks:
		if String(blocks[id]["layer"]) == layer:
			nodes[id].visible = not hidden
	_say("%s %s" % [LAYER_LABEL[layer], "hidden" if hidden else "shown"])


# ---------------------------------------------------------------- maps

func map_ids() -> Array[String]:
	var ids: Array[String] = []
	var registry: Variant = JSON.parse_string(FileAccess.get_file_as_string(REGISTRY))
	if typeof(registry) == TYPE_DICTIONARY:
		for id: String in registry.get("maps", {}):
			ids.append(id)
	ids.sort()
	return ids


func open_map(id: String) -> bool:
	if not map_ids().has(id):
		_say("Unknown map: " + id)
		return false
	map_id = id
	var ok := load_map()
	_fill_map_pick()
	return ok


## Creates a new empty map from a factory preset and opens it. Returns {ok, message}.
func create_map(new_id: String, preset: String) -> Dictionary:
	var arguments: Array = ["--new", new_id, "--preset", preset]
	if save_dry_run:
		arguments.append("--dry-run")
	var result := _run_save_tool(arguments)
	if result["ok"] and not save_dry_run:
		open_map(new_id)
	_say(String(result["message"]))
	return result


func _run_save_tool(arguments: Array) -> Dictionary:
	var output: Array = []
	var code := OS.execute(python_executable, [ProjectSettings.globalize_path(SAVE_TOOL)] + arguments, output, true)
	var text := "\n".join(output).strip_edges()
	var last := text.get_slice("\n", text.get_slice_count("\n") - 1) if text != "" else "Could not run %s (exit %d)" % [python_executable, code]
	return {"ok": code == 0, "message": last}


func _same_keys(a: Dictionary, b: Dictionary) -> bool:
	if a.size() != b.size():
		return false
	for key in a:
		if not b.has(key):
			return false
	return true


## The edits since loading, as the list tools/room_editor_save.py understands.
func pending_changes() -> Array:
	var changes: Array = []
	if not _same_keys(cells, original_cells):
		changes.append({"op": "property", "key": "floor_footprint",
			"value": {"row_spans": _row_spans(), "shape": "editor", "notes": "Floor shape edited by hand in the room editor."}})
	var touched: Dictionary = {}
	for key: String in tiles:
		touched[key] = true
	for key: String in original_tiles:
		touched[key] = true
	for key: String in touched:
		if String(tiles.get(key, "")) != String(original_tiles.get(key, "")):
			var xy := key.split(":")
			changes.append({"op": "tile", "x": int(xy[0]), "y": int(xy[1]), "id": tiles.get(key)})
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
		for key: String in ["x", "y", "scale", "rotation_degrees", "flip_h", "layer"]:
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
	var arguments: Array = ["--changes", path]
	if save_dry_run:
		arguments.append("--dry-run")
	var result := _run_save_tool(arguments)
	if result["ok"] and not save_dry_run:
		load_map()
	_say(String(result["message"]))
	return result


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
	if battle_tool != "":
		line = "Battle setup [%s]: click squares (Esc stops)   players %d, enemies %d, blocked by hand %d" % [battle_tool,
			battle_units.filter(func(u: Dictionary) -> bool: return u["team"] == "player").size(),
			battle_units.filter(func(u: Dictionary) -> bool: return u["team"] == "enemy").size(), battle_blocked.size()]
	elif erasing_floor:
		line = "Erasing floor squares: click or drag over squares (Esc stops)"
	elif placing_part != "" and is_floor_part(placing_part):
		line = "Painting floor %s: click or drag over squares (Esc stops)" % placing_part
	elif placing_part != "":
		line = "Placing %s on level %s: click on the map (Esc cancels)" % [placing_part, LAYER_LABEL[active_layer]]
	elif selected != "":
		var block: Dictionary = blocks[selected]
		line = "%s  [%s]  x %d  y %d  size %.2f  turn %d  %s   |  %d unsaved change(s)" % [selected, block["id"], int(block["x"]),
			int(block["y"]), float(block["scale"]), int(block["rotation_degrees"]), LAYER_LABEL[String(block["layer"])], pending_changes().size()]
	_status_label.text = line


func _draw_overlay() -> void:
	# Ground edits are previewed here; the factory draws them with joints and shading after saving.
	for key: String in tiles:
		if String(tiles[key]) != String(original_tiles.get(key, "")):
			var xy := key.split(":")
			var path := String(_catalog.get_asset(String(tiles[key])).get("texture_path", ""))
			if HdAssets.exists(path):
				_overlay.draw_texture_rect(load(HdAssets.resolve(path)) as Texture2D, cell_rect(Vector2i(int(xy[0]), int(xy[1]))), false)
	for key: String in original_cells:
		if not cells.has(key):
			var xy := key.split(":")
			_overlay.draw_rect(cell_rect(Vector2i(int(xy[0]), int(xy[1]))), Color(0.1, 0.4, 0.8, 0.75))
	if battle_tool != "" or not battle_units.is_empty() or not battle_blocked.is_empty():
		var faint := 1.0 if battle_tool != "" else 0.45
		var size: Array = map_data.get("size", [0, 0])
		for y in int(size[1]):
			for x in int(size[0]):
				var cell := Vector2i(x, y)
				if battle_blocked.has(_cell_key(cell)):
					_overlay.draw_rect(cell_rect(cell).grow(-2), Color(0.9, 0.15, 0.1, 0.5 * faint))
				elif battle_tool != "" and cells.has(_cell_key(cell)):
					_overlay.draw_rect(cell_rect(cell).grow(-1), Color(1, 1, 1, 0.3), false, 1.0)
		for unit: Dictionary in battle_units:
			var centre := cell_rect(Vector2i(int(unit["cell"][0]), int(unit["cell"][1]))).get_center()
			_overlay.draw_circle(centre, 22, Color(0.2, 0.45, 0.9, faint) if unit["team"] == "player" else Color(0.85, 0.25, 0.2, faint))
			_overlay.draw_string(ThemeDB.fallback_font, centre + Vector2(-20, 5), String(unit["id"]).left(5), HORIZONTAL_ALIGNMENT_LEFT, 44, 13, Color.WHITE)
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
	_map_pick = OptionButton.new()
	_map_pick.item_selected.connect(func(index: int): open_map(_map_pick.get_item_text(index)))
	column.add_child(_map_pick)
	_fill_map_pick()
	var new_row := HBoxContainer.new()
	column.add_child(new_row)
	_new_name = LineEdit.new()
	_new_name.placeholder_text = "new_map_id"
	_new_name.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	new_row.add_child(_new_name)
	_new_preset = OptionButton.new()
	for preset: String in PRESETS:
		_new_preset.add_item(preset)
	new_row.add_child(_new_preset)
	var create := Button.new()
	create.text = "Create new map"
	create.pressed.connect(func(): create_map(_new_name.text.strip_edges(), PRESETS[_new_preset.selected]))
	column.add_child(create)
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
	for row: Array in [["Erase floor squares", func(): toggle_erasing()], ["Grid snap (G)", func(): toggle_snap()],
			["Undo (Ctrl+Z)", func(): undo()], ["Redo (Ctrl+Y)", func(): redo()],
			["Save new version (Ctrl+S)", func(): save()], ["Back to the room (Esc)", func(): get_tree().change_scene_to_file(ROOM_SCENE)]]:
		var button := Button.new()
		button.text = row[0]
		button.pressed.connect(row[1])
		column.add_child(button)
	var battle_title := Label.new()
	battle_title.text = "Battle setup on this map"
	column.add_child(battle_title)
	var battle_row := HBoxContainer.new()
	column.add_child(battle_row)
	for pair: Array in [["Block", "blocked"], ["Player", "player"], ["Enemy", "enemy"], ["Clear", "clear"]]:
		var tool_button := Button.new()
		tool_button.text = pair[0]
		tool_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		tool_button.pressed.connect(func(): set_battle_tool(pair[1]))
		battle_row.add_child(tool_button)
	var play_row := HBoxContainer.new()
	column.add_child(play_row)
	for pair: Array in [["Save battle", func(): save_battle()], ["Play battle", func(): play_battle()]]:
		var battle_button := Button.new()
		battle_button.text = pair[0]
		battle_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		battle_button.pressed.connect(pair[1])
		play_row.add_child(battle_button)
	var help := Label.new()
	help.text = "Click: select / place (Shift keeps placing)   Drag or Ctrl+drag: move\nWheel: resize   Q/E: turn   F: flip\nDelete: remove   Arrows: nudge\nCtrl+D: copy   PgUp/PgDn: level of piece\nRight drag: pan   1-5: level\nShift+1-5: hide level\nfloors: click/drag paints squares"
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


func _fill_map_pick() -> void:
	if _map_pick == null:
		return
	_map_pick.clear()
	for id: String in map_ids():
		_map_pick.add_item(id)
		if id == map_id:
			_map_pick.select(_map_pick.item_count - 1)


func toggle_erasing() -> void:
	battle_tool = ""
	erasing_floor = not erasing_floor
	placing_part = ""
	selected = ""
	_refresh()


func start_placing(part_id: String) -> void:
	erasing_floor = false
	battle_tool = ""
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


## A left-button press at a world point. Ctrl grabs the piece under the mouse even while a part is armed.
func press(point: Vector2, ctrl: bool = false, shift: bool = false) -> void:
	if battle_tool != "":
		battle_click(cell_at(point))
	elif ctrl and placing_part != "" and not erasing_floor and select_at(point) != "":
		# Ctrl while a part is armed: grab the piece under the mouse instead of placing another.
		_dragging = true
		_drag_moved = false
		_drag_offset = Vector2(float(blocks[selected]["x"]), float(blocks[selected]["y"])) - point
	elif erasing_floor or (placing_part != "" and is_floor_part(placing_part)):
		_stroke_open = true
		_ground_stroke(point, true)
	elif placing_part != "":
		var placed := place(placing_part, point)
		if placed != "" and not shift:
			placing_part = ""  # one piece per pick; it stays selected so it can be dragged at once
			selected = placed
			_refresh()
	elif select_at(point) != "":
		_dragging = true
		_drag_moved = false
		_drag_offset = Vector2(float(blocks[selected]["x"]), float(blocks[selected]["y"])) - point


func _unhandled_input(event: InputEvent) -> void:
	var point := get_global_mouse_position()
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				press(point, event.ctrl_pressed, event.shift_pressed)
			else:
				_dragging = false
				_stroke_open = false
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
		elif _stroke_open:
			_ground_stroke(point, false)
		elif _dragging and selected != "":
			move_selected(point + _drag_offset, not _drag_moved)  # one undo step per drag
			_drag_moved = true
	elif event is InputEventKey and event.pressed:
		_key(event)


## One undo step per stroke: only the first changed square of a drag is remembered.
var _stroke_remembered: bool = false


func _ground_stroke(point: Vector2, first: bool) -> void:
	if first:
		_stroke_remembered = false
	var cell := cell_at(point)
	var changed := erase_cell(cell, not _stroke_remembered) if erasing_floor else paint_tile(cell, placing_part, not _stroke_remembered)
	if changed:
		_stroke_remembered = true


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
		KEY_Y:
			if event.ctrl_pressed:
				redo()
		KEY_D:
			if event.ctrl_pressed:
				duplicate_selected()
		KEY_PAGEUP, KEY_PAGEDOWN:
			if selected != "":
				var index := LAYERS.find(String(blocks[selected]["layer"])) + (1 if event.keycode == KEY_PAGEUP else -1)
				if index >= 0 and index < LAYERS.size():
					move_selected_to_layer(LAYERS[index])
		KEY_S:
			if event.ctrl_pressed:
				save()
		KEY_1, KEY_2, KEY_3, KEY_4, KEY_5:
			var layer: String = LAYERS[event.keycode - KEY_1]
			if event.shift_pressed:
				set_layer_hidden(layer, not hidden_layers.has(layer))
			else:
				set_active_layer(layer)
		KEY_ESCAPE:
			if placing_part != "" or erasing_floor or battle_tool != "":
				placing_part = ""
				erasing_floor = false
				battle_tool = ""
				_refresh()
			elif selected != "":
				selected = ""
				_refresh()
			else:
				get_tree().change_scene_to_file(ROOM_SCENE)
