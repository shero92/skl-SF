extends Node2D

## Standalone F6 preview scene, intentionally excludes characters and user interface.
@export var map_id: String = "hero_room_01"

func _ready() -> void:
    var map_node := RoomFactory.new().build_latest(map_id, self)
    map_node.name = "RenderedLatestMap"
    var manifest_path := "res://map_factory/maps/" + map_id + "/latest.json"
    if not FileAccess.file_exists(manifest_path):
        push_error("Map preview missing last snapshot for " + map_id)
        return
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(manifest_path))
    if typeof(raw) != TYPE_DICTIONARY:
        push_error("Invalid map snapshot")
        return
    var canvas: Array = raw.get("canvas_size", [1536,1024])
    var camera := Camera2D.new()
    camera.name = "MapPreviewCamera"
    camera.position = Vector2(float(canvas[0])*0.5, float(canvas[1])*0.5)
    camera.enabled = true
    add_child(camera)
