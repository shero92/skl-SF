extends Node2D

## Environment-only preview: run F6 or start this scene with
## godot --path . --scene res://scenes/map_factory_preview.tscn -- --map-id=courtyard_demo_01
@export var map_id: String = "hero_room_01"
@export var fit_canvas_to_window: bool = true
var rendered_map: Node2D
var camera: Camera2D

func _ready() -> void:
    for arg in OS.get_cmdline_user_args():
        if arg.begins_with("--map-id="):
            map_id = arg.substr(9)
    var registry_path := "res://map_factory/maps/index.json"
    if not FileAccess.file_exists(registry_path):
        push_error("Map registry missing")
        return
    var registry: Variant = JSON.parse_string(FileAccess.get_file_as_string(registry_path))
    if typeof(registry) != TYPE_DICTIONARY:
        push_error("Map registry is malformed")
        return
    var maps: Dictionary = registry.get("maps", {})
    if not maps.has(map_id):
        push_error("Unregistered map in preview: " + map_id)
        return
    var reference: Dictionary = maps[map_id]
    var path := "res://" + String(reference.get("latest", ""))
    if not FileAccess.file_exists(path):
        push_error("Latest snapshot missing: " + path)
        return
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
    if typeof(raw) != TYPE_DICTIONARY:
        push_error("Invalid map snapshot " + map_id)
        return
    var room_data: Dictionary = raw
    rendered_map = RoomFactory.new().build_latest(map_id, self)
    rendered_map.name = "Map_" + map_id

    var dimensions: Array = room_data.get("canvas_size", [1536, 1024])
    var bounds := Vector2(float(dimensions[0]), float(dimensions[1]))
    camera = Camera2D.new()
    camera.name = "MapPreviewCamera"
    camera.position = bounds * 0.5
    camera.enabled = true
    add_child(camera)
    get_viewport().size_changed.connect(_update_zoom.bind(bounds))
    _update_zoom(bounds)

func _update_zoom(bounds: Vector2) -> void:
    if not fit_canvas_to_window or camera == null:
        return
    var view := get_viewport_rect().size
    if view.x <= 0 or view.y <= 0 or bounds.x <= 0 or bounds.y <= 0:
        return
    var ratio := minf(view.x / bounds.x, view.y / bounds.y)
    camera.zoom = Vector2.ONE * clampf(ratio, 0.05, 4.0)
