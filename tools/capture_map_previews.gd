extends SceneTree

## Create REAL Godot screenshots: no AI simulation, no characters or HUD.
## Resolve immutable map revisions from the registry or an explicit capture manifest.
## Use a virtual X11 display and OpenGL3 in CI; headless dummy rendering cannot screenshot.
const OUTPUT: String = "res://docs/previews/map_factory_renders/"
const CaptureChecks = preload("res://tools/capture_checks.gd")

var capture_request: Dictionary = {}
var resolved_assets: Array = []
var source_errors: Array = []

func _sprite_bounds(node: Sprite2D) -> Array:
    var transform: Transform2D = node.get_global_transform_with_canvas()
    var rect: Rect2 = node.get_rect()
    var corners := [
        transform * rect.position,
        transform * Vector2(rect.end.x, rect.position.y),
        transform * rect.end,
        transform * Vector2(rect.position.x, rect.end.y)]
    var bounds := Rect2(corners[0], Vector2.ZERO)
    for corner in corners:
        bounds = bounds.expand(corner)
    return [bounds.position.x, bounds.position.y, bounds.size.x, bounds.size.y]

func _runtime_texture_hash(texture: Texture2D) -> String:
    var image: Image = texture.get_image()
    if image == null:
        return ""
    var hashing := HashingContext.new()
    hashing.start(HashingContext.HASH_SHA256)
    hashing.update(image.get_data())
    return hashing.finish().hex_encode()

func _collect_sources(node: Node, allowed: Array) -> void:
    if node is Sprite2D and node.texture != null:
        var texture_path: String = node.texture.resource_path
        var relative := texture_path.trim_prefix("res://")
        if texture_path == "":
            # Painted shadows and light pools are generated at runtime from registered sprites.
            var digest := _runtime_texture_hash(node.texture)
            if digest == "":
                source_errors.append("Unreadable runtime texture on " + String(node.name))
            else:
                resolved_assets.append({
                    "node": String(node.get_path()),
                    "texture_path": "runtime:" + digest,
                    "texture_sha256": digest,
                    "runtime_generated": true,
                    "bounds": _sprite_bounds(node)})
        elif not relative in allowed or not FileAccess.file_exists(texture_path):
            source_errors.append(texture_path)
        else:
            resolved_assets.append({
                "node": String(node.get_path()),
                "texture_path": texture_path,
                "texture_sha256": FileAccess.get_sha256(texture_path),
                "bounds": _sprite_bounds(node)})
    elif node is CanvasItem and not node is Node2D:
        source_errors.append("Unsupported drawable: " + String(node.get_class()))
    for child in node.get_children():
        _collect_sources(child, allowed)

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
        capture_request = request
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
        var map_id: String = String(case.get("id", ""))
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
        var output_dir: String = OUTPUT
        if not capture_request.is_empty():
            output_dir = String(capture_request.get("output_dir", ""))
            if valid_id.search(capture_id) == null or output_dir != OUTPUT + capture_id + "/" or version <= 13:
                push_error("Unsafe evidence output directory or historic version")
                failures += 1
                continue
            if FileAccess.get_sha256(path) != String(case.get("snapshot_sha256", "")):
                push_error("Snapshot hash mismatch")
                failures += 1
                continue
            var evidence_canvas: Array = map_data.get("canvas_size", [1536, 1024])
            # JSON numbers parse as floats; compare as ints (Array == is type-strict).
            if evidence_canvas.size() != 2 or int(evidence_canvas[0]) != 1536 or int(evidence_canvas[1]) != 1024:
                push_error("Evidence capture requires the reference canvas")
                failures += 1
                continue
        var target: String = output_dir + String(case["file"])
        var receipt_path: String = target.get_basename() + ".json"
        if FileAccess.file_exists(target) or FileAccess.file_exists(receipt_path):
            push_error("Refusing to overwrite an existing capture")
            failures += 1
            continue
        DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output_dir))
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
        if room == null:
            push_error("Room Factory did not build the snapshot")
            failures += 1
            viewport.queue_free()
            continue
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

        resolved_assets = []
        source_errors = []
        if not capture_request.is_empty():
            _collect_sources(room, capture_request.get("allowed_textures", []))
            for draft in CaptureChecks.find_drafts(room):
                source_errors.append("Draft placeholder: " + String(draft))
            if not source_errors.is_empty() or resolved_assets.is_empty():
                push_error("Unregistered, missing or unsupported environment sources: " + str(source_errors))
                failures += 1
                viewport.queue_free()
                for _frame in range(3):
                    await process_frame
                continue
        var picture := viewport.get_texture().get_image()
        if picture == null or picture.get_width() != size.x or picture.get_height() != size.y:
            push_error("Actual viewport screenshot unavailable: " + target)
            failures += 1
        else:
            var error := picture.save_png(target)
            if error == OK:
                var proof: Dictionary = {"capture_id": capture_id, "map_id": map_id,
                    "version": version, "snapshot_sha256": FileAccess.get_sha256(path),
                    "canvas_size": [size.x, size.y], "camera_position": [size.x * 0.5, size.y * 0.5],
                    "camera_zoom": [1, 1], "render_sha256": FileAccess.get_sha256(target)}
                proof["commit"] = capture_request.get("commit", "")
                proof["target_sha256"] = capture_request.get("target_sha256", "")
                proof["resolved_assets"] = resolved_assets
                proof["draft_placeholder_count"] = 0
                proof["environment_only"] = not capture_request.is_empty()
                proof["visual_approval"] = false
                var receipt := FileAccess.open(receipt_path, FileAccess.WRITE)
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
