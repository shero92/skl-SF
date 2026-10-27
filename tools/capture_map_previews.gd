extends SceneTree

## Create REAL Godot screenshots: no AI simulation, no characters or HUD.
## Resolve immutable map revisions from the registry or an explicit capture manifest.
## Use a virtual X11 display and OpenGL3 in CI; headless dummy rendering cannot screenshot.
const OUTPUT: String = "res://docs/previews/map_factory_renders/"

func _initialize() -> void:
    call_deferred("_capture_all")

func _capture_all() -> void:
    DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT))
    var cases: Array = []
    var capture_id: String = ""
    var args: PackedStringArray = OS.get_cmdline_user_args()
    var manifest_index: int = args.find("--capture-manifest")
    if manifest_index >= 0:
        if manifest_index + 1 >= args.size():
            push_error("Missing capture manifest path")
            quit(1)
            return
        var request: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[manifest_index + 1]))
        if not request is Dictionary or not request.get("cases", []) is Array:
            push_error("Invalid capture manifest")
            quit(1)
            return
        cases = request["cases"]
        capture_id = String(request.get("capture_id", ""))
    else:
        var registry: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://map_factory/maps/index.json"))
        if not registry is Dictionary:
            quit(1)
            return
        for map_id: String in registry.get("maps", {}):
            var version: int = int(registry["maps"][map_id]["version"])
            cases.append({"id": map_id, "version": version,
                "file": "%s_v%04d.png" % [map_id, version]})
    if cases.is_empty():
        push_error("No capture cases requested")
        quit(1)
        return
    var valid_id := RegEx.new()
    valid_id.compile("^[a-z][a-z0-9_]{2,63}$")
    var failures := 0
    for case in cases:
        if not case is Dictionary:
            failures += 1
            continue
        var map_id: String = case["id"]
        var version: int = int(case.get("version", 0))
        if valid_id.search(map_id) == null or version < 1 or String(case.get("file", "")) != "%s_v%04d.png" % [map_id, version]:
            push_error("Unsafe capture case identity or filename")
            failures += 1
            continue
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
                var proof: Dictionary = {"capture_id": capture_id, "map_id": map_id,
                    "version": version, "snapshot_sha256": case.get("snapshot_sha256", ""),
                    "canvas_size": [size.x, size.y], "camera_position": [size.x * 0.5, size.y * 0.5],
                    "camera_zoom": [1, 1], "render_sha256": FileAccess.get_sha256(target)}
                var receipt := FileAccess.open(target.get_basename() + ".json", FileAccess.WRITE)
                if receipt == null:
                    push_error("Cannot write capture receipt")
                    failures += 1
                else:
                    receipt.store_string(JSON.stringify(proof))
                    receipt.close()
                    print("MAP_SCREENSHOT_OK: ", target, " ", size)
            else:
                push_error("Screenshot save failed " + target + ": " + str(error))
                failures += 1
        viewport.queue_free()
        for _frame in range(3):
            await process_frame
    quit(0 if failures == 0 else 1)
