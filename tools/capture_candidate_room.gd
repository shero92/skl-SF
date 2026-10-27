extends SceneTree

## Real Godot capture of a review-only candidate layout (TASK-0047): builds the published base
## map version, hides the instances/floor cells the candidate replaces, adds the candidate PNGs
## straight from .agents/graphics/deliveries (no import, no catalog entry) and saves two PNGs:
##   godot --path . --script res://tools/capture_candidate_room.gd -- <resolved.json> <base.png> <candidate.png>
## resolved.json is written by tools/candidate_room.py. Needs a real display (no --headless).

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() < 3:
        push_error("usage: -- <resolved.json> <base.png> <candidate.png>")
        quit(2)
        return
    var spec: Variant = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
    if typeof(spec) != TYPE_DICTIONARY:
        push_error("Malformed resolved layout " + args[0])
        quit(2)
        return
    var ok := await _capture(spec, false, args[1])
    ok = await _capture(spec, true, args[2]) and ok
    quit(0 if ok else 1)

func _capture(spec: Dictionary, with_candidate: bool, target: String) -> bool:
    var dim: Array = spec.get("canvas_size", [1536, 1024])
    var size := Vector2i(int(dim[0]), int(dim[1]))
    var viewport := SubViewport.new()
    viewport.size = size
    viewport.disable_3d = true
    viewport.transparent_bg = false
    viewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
    root.add_child(viewport)
    var host := Node2D.new()
    viewport.add_child(host)
    var room := RoomFactory.new().build_room(String(spec["base_path"]), host)
    var missing := 0
    if with_candidate:
        missing = _apply(room, spec)
    var camera := Camera2D.new()
    camera.position = Vector2(size) * 0.5
    camera.enabled = true
    host.add_child(camera)
    for _frame in range(8):
        await process_frame
    await RenderingServer.frame_post_draw
    var picture := viewport.get_texture().get_image()
    var ok := picture != null and picture.get_width() == size.x and picture.get_height() == size.y
    if ok:
        ok = picture.save_png(target) == OK
    print(("CANDIDATE_CAPTURE_OK: " if ok else "CANDIDATE_CAPTURE_FAILED: ") + target + " missing=" + str(missing))
    viewport.queue_free()
    for _frame in range(3):
        await process_frame
    return ok and missing == 0

func _apply(room: Node, spec: Dictionary) -> int:
    var missing := 0
    var hidden := {}
    for name in spec.get("hide_instances", []):
        var node := room.find_child(String(name), true, false)
        if node == null:
            push_error("Candidate hides unknown instance " + String(name))
            missing += 1
        else:
            (node as CanvasItem).visible = false
            hidden[String(name)] = true
    # Shadows are separate instances that remember their owner.
    for node in room.find_children("*", "", true, false):
        if node.has_meta("owner_instance_id") and hidden.has(String(node.get_meta("owner_instance_id"))):
            (node as CanvasItem).visible = false
    for cell in spec.get("hide_floor_cells", []):
        var prefix := "Floor_%d_%d_" % [int(cell[0]), int(cell[1])]
        var found := false
        for node in room.find_children(prefix + "*", "", true, false):
            (node as CanvasItem).visible = false
            found = true
        if not found:
            push_error("No floor sprite for candidate cell " + prefix)
            missing += 1
    # Re-floor: a cell shows the plain tile of another cell (texture, rotation), offset by whole cells.
    var tile := float(spec.get("tile_size", 64))
    for cell in spec.get("refloor_cells", []):
        var targets := room.find_children("Floor_%d_%d_*" % [int(cell[0]), int(cell[1])], "", true, false)
        var sources := room.find_children("Floor_%d_%d_*" % [int(cell[2]), int(cell[3])], "", true, false)
        if targets.is_empty() or sources.is_empty():
            push_error("Cannot re-floor candidate cell " + str(cell))
            missing += 1
            continue
        var src := sources[0] as Sprite2D
        var dst := targets[0] as Sprite2D
        dst.texture = src.texture
        dst.centered = src.centered
        dst.rotation = src.rotation
        dst.scale = src.scale
        dst.offset = src.offset
        dst.region_enabled = src.region_enabled
        dst.region_rect = src.region_rect
        dst.position = src.position + Vector2(float(int(cell[0]) - int(cell[2])), float(int(cell[1]) - int(cell[3]))) * tile
    var layers := {"ground": _group(room, "CandidateGround", 11), "walls": _group(room, "CandidateWalls", 30),
        "shadows": _group(room, "CandidateShadows", 20)}
    (layers["walls"] as Node2D).y_sort_enabled = true
    # "props": y-sorted together with the base furniture by ground contact (e.g. a fence in front of a chest).
    var decor := room.find_child("Level3_Decorations", true, false) as Node2D
    layers["props"] = decor if decor != null else _group(room, "CandidateProps", 40)
    (layers["props"] as Node2D).y_sort_enabled = true
    for piece in spec.get("placements", []):
        var at := Vector2(float(piece["position"][0]), float(piece["position"][1]))
        var anchor := Vector2(float(piece["anchor_px"][0]), float(piece["anchor_px"][1]))
        var holder := Node2D.new()
        holder.name = String(piece["name"])
        holder.position = at
        var sprite := _sprite(String(piece["texture"]), anchor)
        if sprite == null:
            missing += 1
            continue
        holder.add_child(sprite)
        (layers[String(piece["layer"])] as Node2D).add_child(holder)
        if String(piece.get("shadow", "")) != "":
            var shadow := _sprite(String(piece["shadow"]), anchor)
            if shadow != null:
                shadow.position = at
                (layers["shadows"] as Node2D).add_child(shadow)
    return missing

func _group(room: Node, name: String, z: int) -> Node2D:
    var group := Node2D.new()
    group.name = name
    group.z_index = z
    room.add_child(group)
    return group

func _sprite(path: String, anchor: Vector2) -> Sprite2D:
    var image := Image.load_from_file(path)
    if image == null or image.is_empty():
        push_error("Cannot load candidate texture " + path)
        return null
    var sprite := Sprite2D.new()
    sprite.texture = ImageTexture.create_from_image(image)
    sprite.centered = false
    sprite.offset = -anchor
    return sprite
