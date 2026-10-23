extends SceneTree

## Create REAL Godot screenshots: no AI simulation, no characters or HUD.
## v0004 now published: screenshot the five-level environment renderer for visual QA.
## The revised Hero Room captures the fixed integer tile override mapping.
## Use a virtual X11 display and OpenGL3 in CI; headless dummy rendering cannot screenshot.
const OUTPUT: String = "res://docs/previews/map_factory_renders/"

func _initialize() -> void:
    call_deferred("_capture_all")

func _capture_all() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
    var cases := [
        {"id": "courtyard_demo_01", "version": 1, "file": "courtyard_demo_01_v0001.png"},
        {"id": "courtyard_demo_01", "version": 2, "file": "courtyard_demo_01_v0002.png"},
        {"id": "hero_room_01", "version": 1, "file": "hero_room_01_v0001.png"},
        {"id": "hero_room_01", "version": 2, "file": "hero_room_01_v0002.png"},
        {"id": "hero_room_01", "version": 3, "file": "hero_room_01_v0003.png"},
        {"id": "hero_room_01", "version": 4, "file": "hero_room_01_v0004.png"},
        {"id": "hero_room_01", "version": 5, "file": "hero_room_01_v0005.png"},
        {"id": "hero_room_01", "version": 6, "file": "hero_room_01_v0006.png"}
    ]
    var failures := 0
    for case in cases:
        var map_id: String = case["id"]
        var version: int = case["version"]
        var path := "res://map_factory/maps/%s/versions/v%04d.json" % [map_id, version]
        if not FileAccess.file_exists(path):
            push_error("Cannot render missing snapshot " + path)
            failures += 1
            continue
        var record: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
        if typeof(record) != TYPE_DICTIONARY:
            push_error("Malformed map snapshot " + path)
            failures += 1
            continue
        var map_data: Dictionary = record
        var dim: Array = map_data.get("canvas_size", [1536, 1024])
        var size := Vector2i(int(dim[0]), int(dim[1]))
        if size.x < 100 or size.y < 100 or size.x > 4096 or size.y > 4096:
            push_error("Invalid capture canvas " + str(size))
            failures += 1
            continue

        var viewport := SubViewport.new()
        viewport.name = "OffscreenMapRender"
        viewport.size = size
        viewport.disable_3d = true
        viewport.transparent_bg = false
        viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
        root.add_child(viewport)
        var parent := Node2D.new()
        parent.name = "MapPreviewHost"
        viewport.add_child(parent)
        var factory := RoomFactory.new()
        var room := factory.build_room(path, parent)
        room.name = map_id + "_built_from_blocks"
        var camera := Camera2D.new()
        camera.name = "CaptureCamera"
        camera.position = Vector2(size) * 0.5
        camera.zoom = Vector2.ONE
        camera.enabled = true
        parent.add_child(camera)
        for _frame in range(8):
            await process_frame
        await RenderingServer.frame_post_draw

        var picture := viewport.get_texture().get_image()
        var target: String = OUTPUT + String(case["file"])
        if picture == null or picture.get_width() != size.x or picture.get_height() != size.y:
            push_error("Actual viewport screenshot unavailable: " + target)
            failures += 1
        else:
            var error := picture.save_png(target)
            if error == OK:
                print("MAP_SCREENSHOT_OK: ", target, " ", size)
            else:
                push_error("Screenshot save failed " + target + ": " + str(error))
                failures += 1
        viewport.queue_free()
        for _frame in range(3):
            await process_frame
    quit(0 if failures == 0 else 1)
