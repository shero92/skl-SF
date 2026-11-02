extends Node

## Renders the explicit reference-room layout. Capture all five construction stages:
## godot --path . --scene res://scenes/original_room_rebuilt.tscn -- --capture --scale=2
var layout_path := "res://map_factory/rooms/reference_room_layout.json"
const STAGES := [
    ["stage1_background_empty_ground", 1],
    ["stage2_ground_structures", 2],
    ["stage3_ground_furniture", 3],
    ["stage4_ground_decorations", 4],
    ["original_room_rebuilt", 5],
]

func _ready() -> void:
    var capture := false
    var scale_px := 2
    var suffix := ""
    for arg in OS.get_cmdline_user_args():
        if arg == "--capture":
            capture = true
        elif arg.begins_with("--layout="):
            layout_path = arg.substr(9)
            suffix = "_procedural"
        elif arg.begins_with("--scale="):
            scale_px = int(arg.substr(8))
    if not capture:
        await _build_view(5, 1)
        return
    for stage in STAGES:
        var image := await _build_view(stage[1], scale_px)
        var path := ProjectSettings.globalize_path("res://room_previews/%s%s.png" % [stage[0], suffix])
        image.save_png(path)
        print("saved ", path, " ", image.get_size())
    get_tree().quit()

func _build_view(stage: int, scale_px: int) -> Image:
    for child in get_children():
        child.queue_free()
    await get_tree().process_frame
    var builder := ModularRoomBuilder.new()
    var viewport := SubViewport.new()
    add_child(viewport)
    builder.build(layout_path, viewport, stage)
    viewport.size = Vector2i(builder.canvas_size) * scale_px
    viewport.canvas_transform = Transform2D().scaled(Vector2.ONE * scale_px)
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    for issue in builder.issues:
        print("ISSUE[stage%d]: %s" % [stage, issue])
    if stage >= 2 and builder.layout.has("_report"):
        print("REPORT[stage%d]: %s" % [stage, builder.layout["_report"]])
    await RenderingServer.frame_post_draw
    await RenderingServer.frame_post_draw
    var image := viewport.get_texture().get_image()
    var shown := Sprite2D.new()
    shown.texture = viewport.get_texture()
    shown.centered = false
    add_child(shown)
    return image
