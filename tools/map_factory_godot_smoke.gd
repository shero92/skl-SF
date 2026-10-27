extends SceneTree

## Headless environment-only validation: build every registered map from latest JSON.
## Deliberately does not instantiate players, characters, dialogue or interface.
func _initialize() -> void:
    call_deferred("_run_smoke")

func _run_smoke() -> void:
    var background_ok: bool = _background_runtime_smoke()
    if "--background-only" in OS.get_cmdline_user_args():
        quit(0 if background_ok else 1)
        return
    var file := "res://map_factory/maps/index.json"
    if not FileAccess.file_exists(file):
        push_error("Missing registered maps JSON")
        quit(1)
        return
    var raw: Variant = JSON.parse_string(FileAccess.get_file_as_string(file))
    if typeof(raw) != TYPE_DICTIONARY:
        push_error("Malformed map registry")
        quit(1)
        return
    var maps: Dictionary = raw.get("maps", {})
    if maps.is_empty():
        push_error("No maps to validate")
        quit(1)
        return
    var ok := _depth_link_smoke() and background_ok
    for key in maps.keys():
        var id := String(key)
        var entry: Dictionary = maps[key]
        var path := "res://" + String(entry.get("latest", ""))
        if not FileAccess.file_exists(path):
            push_error("Missing map " + id)
            ok = false
            continue
        var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
        if typeof(parsed) != TYPE_DICTIONARY:
            push_error("Invalid map data: " + id)
            ok = false
            continue
        var data: Dictionary = parsed
        var host := Node2D.new()
        root.add_child(host)
        var built := RoomFactory.new().build_latest(id, host)
        var layered: bool = data.has("layer_stack")
        var ground := built.get_node_or_null("Level1_Ground/Ground" if layered else "Ground")
        var dimensions: Array = data.get("size", [0, 0])
        var expected_floor := int(dimensions[0]) * int(dimensions[1])
        var outline: Dictionary = data.get("floor_footprint", {})
        if outline.has("row_spans"):
            expected_floor = 0
            for row in outline["row_spans"]:
                for span in row:
                    expected_floor += int(span[1]) - int(span[0]) + 1
        if ground == null or ground.get_child_count() != expected_floor:
            push_error("Incorrect floor tiles: " + id)
            ok = false
        # Validate actual floor ID-to-texture mapping, not just tile count.
        for override in data.get("tile_overrides", []):
            var cx: int = int(override.get("x", -1))
            var cy: int = int(override.get("y", -1))
            var tile_id: String = String(override.get("id", ""))
            var tile_name := "Floor_%d_%d_%s" % [cx, cy, tile_id]
            var tile := ground.get_node_or_null(tile_name) as Sprite2D if ground != null else null
            if tile == null or tile.texture == null:
                push_error("Missing actual override tile: " + id + " " + tile_name)
                ok = false
            elif tile_id == "F014":
                var img := tile.texture.get_image()
                var blue_pixels := 0
                var tested_pixels := 0
                for py in range(0, img.get_height(), 4):
                    for px in range(0, img.get_width(), 4):
                        var col := img.get_pixel(px, py)
                        tested_pixels += 1
                        if col.b > col.r * 1.4 and col.b > col.g * 1.16 and col.b > 0.37:
                            blue_pixels += 1
                print("FOCAL_COMPASS_DIAGNOSTIC ", id, " ", tile_name,
                      " texture=", tile.texture.resource_path, " blue_fraction=",
                      float(blue_pixels) / float(tested_pixels))
                if tested_pixels == 0 or float(blue_pixels) / float(tested_pixels) < 0.15:
                    push_error("Compass tile is missing its blue detail")
                    ok = false
        if layered:
            var stack: Dictionary = data["layer_stack"]
            var passes: Dictionary = stack.get("passes", {})
            var layer_nodes := {
                "background": "Level0_Background",
                "ground": "Level1_Ground/GroundOverlays",
                "walls": "Level2_Walls",
                "decorations": "Level3_Decorations",
                "shadows": "Level4_Shadows"
            }
            for pass_id in layer_nodes:
                var section := built.get_node_or_null(String(layer_nodes[pass_id]))
                var records: Array = passes.get(String(pass_id), [])
                var mounted := 0
                for record in records:
                    if typeof(record.get("attachment")) == TYPE_DICTIONARY:
                        mounted += 1
                if section == null or section.get_child_count() != records.size() - mounted:
                    push_error("Five-pass wrong size: " + id + "/" + String(pass_id))
                    ok = false
                    continue
                for record in records:
                    var label: String = String(record.get("instance_id",""))
                    var node := section.get_node_or_null(label) as Node2D
                    if node == null:
                        node = built.find_child(label, true, false) as Node2D
                    if node == null:
                        push_error("Five-pass missing block "+ id + "/" +label)
                        ok=false
                        continue
                    if pass_id == "shadows":
                        if node.get_meta("owner_instance_id","") != record.get("owner_instance_id",""):
                            push_error("Incorrect independent shadow owner for "+label)
                            ok=false
                        if node.get_node_or_null("AlphaShadow") == null:
                            push_error("Missing shadow PNG for "+label)
                            ok=false
                    else:
                        var sprite := node.get_node_or_null("Visual") as Sprite2D
                        if sprite == null or sprite.texture == null:
                            push_error("Unloaded individual PNG: "+label)
                            ok=false
                    if pass_id == "decorations":
                        var attach: Variant = record.get("attachment")
                        if typeof(attach) == TYPE_DICTIONARY:
                            if node.get_meta("mount_on","") != attach.get("parent_instance_id",""):
                                push_error("Mount lost: "+label)
                                ok=false
                            if String(node.get_parent().name) != String(attach.get("parent_instance_id","")):
                                push_error("Mount not parented to host: "+label)
                                ok=false
                    var p: Array = record.get("position",[0,0])
                    var world := RoomFactory.room_transform(node, built).origin
                    if world.distance_to(Vector2(float(p[0]),float(p[1]))) > 0.5:
                        push_error("Wrong block/shadow world position: "+label)
                        ok=false
        else:
            var layer_nodes := {
                "background_objects": "DistantRuins",
                "ground_overlays": "GroundOverlays",
                "back_objects": "RearArchitecture",
                "objects": "Entities",
                "front_objects": "FrontDecorations"
            }
            for layer in layer_nodes:
                var section := built.get_node_or_null(String(layer_nodes[layer]))
                var expected_count := (data.get(String(layer), []) as Array).size()
                if section == null or section.get_child_count() != expected_count:
                    push_error("Missing/wrong " + String(layer) + " in map " + id)
                    ok = false
        var ocean_settings: Dictionary = data.get("ocean", {})
        var needs_sea := not ocean_settings.is_empty() and bool(ocean_settings.get("enabled", true))
        var has_sea := built.get_node_or_null("OceanBackground") != null
        if needs_sea != has_sea:
            push_error("Unexpected ocean layer in " + id)
            ok = false
        var expected_effects: int = (data.get("effects", []) as Array).size()
        var effect_root := built.get_node_or_null("AnimatedLighting")
        if effect_root == null or effect_root.get_child_count() != expected_effects:
            push_error("Missing effects in " + id)
            ok = false
        print("Map builder tested: ", id, " | floor=", expected_floor,
              " | ocean=", has_sea, " | blocks=", built.get_child_count())
        host.queue_free()
    if ok:
        print("All environment-only map builds passed: ", maps.size())
    quit(0 if ok else 1)


func _background_check(passed: bool, message: String) -> bool:
    if not passed:
        push_error("Background runtime: " + message)
    return passed


func _link_check(passed: bool, message: String) -> bool:
    if not passed:
        push_error("Depth/mount runtime: " + message)
    return passed


func _shadow_for(shadows: Node, owner_id: String) -> Node2D:
    return shadows.get_node_or_null(owner_id + "__shadow") as Node2D


func _depth_link_smoke() -> bool:
    # Registered catalog IDs only; textures come from the same image-free
    # placeholders as the background fixture. No fallback art is synthesized.
    var factory := RoomFactory.new()
    var host := Node2D.new()
    get_root().add_child(host)
    var contact := {"type": "contact", "opacity": 0.3}
    var walls: Array = [{"instance_id": "LinkWall", "asset_id": "W021", "position": [100, 200], "shadow": contact}]
    var decorations: Array = [
        {"instance_id": "HungDecor", "asset_id": "D019", "position": [110, 150], "shadow": contact,
            "attachment": {"parent_instance_id": "LinkWall", "mount_offset": [10, -50]}},
        {"instance_id": "FrontDecor", "asset_id": "D019", "position": [100, 260], "shadow": contact},
        {"instance_id": "BackDecor", "asset_id": "D019", "position": [100, 120]}
    ]
    var shadow_records: Array = []
    for owner in ["LinkWall", "HungDecor", "FrontDecor"]:
        var source: Dictionary = (walls + decorations).filter(func(e): return e["instance_id"] == owner)[0]
        shadow_records.append({"instance_id": owner + "__shadow", "owner_instance_id": owner,
            "position": source["position"], "scale": 1.0, "sprite_pixel_size": [64, 64], "settings": contact})
    factory._build_five_levels({"canvas_size": [400, 400], "size": [0, 0], "occlusion_mode": "world_y_sort"},
        {"passes": {"walls": walls, "decorations": decorations, "shadows": shadow_records}}, host)
    var depth := host.get_node_or_null("WorldDepthSort") as Node2D
    var wall := host.get_node_or_null("WorldDepthSort/Level2_Walls/LinkWall") as Node2D
    var decor := host.get_node_or_null("WorldDepthSort/Level3_Decorations") as Node2D
    var shadows := host.get_node_or_null("Level4_Shadows") as Node2D
    var ok := _link_check(depth != null and wall != null and decor != null and shadows != null, "missing pass nodes")
    if not ok:
        host.free()
        return false
    var hung := wall.get_node_or_null("HungDecor") as Node2D
    var front := decor.get_node_or_null("FrontDecor") as Node2D
    var back := decor.get_node_or_null("BackDecor") as Node2D
    ok = _link_check(hung != null and front != null and back != null, "mounted/free decor missing")
    if not ok:
        host.free()
        return false
    # Mounted offsets: child of its host at the compiled local offset.
    ok = _link_check(decor.get_child_count() == 2, "mounted decor still in free decor pass") and ok
    ok = _link_check(hung.position.is_equal_approx(Vector2(10, -50)), "wrong mounted offset") and ok
    # Front/back occlusion: walls and decor share one Y-sort at equal z, so the
    # contact Y alone decides order; the mount draws after (in front of) its host.
    var levels := [depth.get_node("Level2_Walls"), decor]
    ok = _link_check(depth.y_sort_enabled and levels.all(func(n): return n.y_sort_enabled and n.z_index == 0),
        "walls/decor not in one world Y-sort") and ok
    ok = _link_check(back.position.y < wall.position.y and wall.position.y < front.position.y
        and back.z_index == wall.z_index and front.z_index == wall.z_index, "front/back sort keys wrong") and ok
    ok = _link_check(hung.get_index() > wall.get_node("Visual").get_index(), "mount drawn behind host") and ok
    ok = _link_check(shadows.z_index < depth.z_index, "shadows above casting objects") and ok
    for owner in ["LinkWall", "HungDecor", "FrontDecor"]:
        var shadow := _shadow_for(shadows, owner)
        ok = _link_check(shadow != null and shadow.get_node_or_null("AlphaShadow") != null
            and shadow.get_node_or_null("Polygon2D") == null, "missing registered shadow for " + owner) and ok
    if not ok:
        host.free()
        return false
    # Host move: the mount follows and each shadow tracks only its own owner.
    wall.position = Vector2(300, 200)
    RoomFactory.sync_links(host)
    ok = _link_check(RoomFactory.room_transform(hung, host).origin.is_equal_approx(Vector2(310, 150)),
        "mount did not follow host") and ok
    ok = _link_check(_shadow_for(shadows, "LinkWall").position.is_equal_approx(Vector2(300, 200)), "host shadow stale") and ok
    ok = _link_check(_shadow_for(shadows, "HungDecor").position.is_equal_approx(Vector2(310, 150)), "mount shadow stale") and ok
    ok = _link_check(_shadow_for(shadows, "FrontDecor").position.is_equal_approx(Vector2(100, 260)),
        "independent shadow moved with another owner") and ok
    front.position = Vector2(50, 270)
    RoomFactory.sync_links(host)
    ok = _link_check(_shadow_for(shadows, "FrontDecor").position.is_equal_approx(Vector2(50, 270))
        and _shadow_for(shadows, "LinkWall").position.is_equal_approx(Vector2(300, 200)), "owner shadows not independent") and ok
    # Host remove: mount and both linked shadows go; unrelated owners stay.
    wall.free()
    RoomFactory.sync_links(host)
    ok = _link_check(not is_instance_valid(hung), "mount survived host removal") and ok
    ok = _link_check(_shadow_for(shadows, "LinkWall") == null and _shadow_for(shadows, "HungDecor") == null,
        "removed owner left a shadow") and ok
    ok = _link_check(_shadow_for(shadows, "FrontDecor") != null and shadows.get_child_count() == 1,
        "unrelated shadow removed") and ok
    host.free()
    if ok:
        print("Depth/mount runtime passed: host move/remove, mounted offsets, owner shadows, front/back occlusion")
    return ok


func _background_runtime_smoke() -> bool:
    # The fixture exercises the same compiled-pass builder used by real maps.
    # Local image-free tests provide PlaceholderTexture2D resources; hosted smoke
    # uses the registered textures. Neither path synthesizes production graphics.
    var factory := RoomFactory.new()
    var host := Node2D.new()
    get_root().add_child(host)
    var frames: Array = ["E010", "E011", "E012", "E013", "E014"]
    var entries: Array = [
        {"instance_id": "RuntimeSea", "asset_id": "E010", "position": [25, 30],
            "animation": {"frames": frames, "fps": 4.0}},
        {"instance_id": "RuntimeCloud", "asset_id": "E018", "position": [10, 20],
            "scroll": {"vx": -10.0, "vy": 0.0}, "scale": 1.5, "flip_h": true},
        {"instance_id": "RuntimeFoam", "asset_id": "E009", "position": [40, 50],
            "animation": {"frames": ["E009", "E009"], "fps": 2.0}},
        {"instance_id": "StaticBackground", "asset_id": "E015", "position": [75, 80]},
        {"instance_id": "RuntimeCombined", "asset_id": "E010", "position": [100, 20],
            "animation": {"frames": frames, "fps": 4.0}, "scroll": {"vx": 0.0, "vy": 3.0}}
    ]
    factory._build_five_levels({"canvas_size": [200, 100], "size": [0, 0]},
        {"passes": {"background": entries}}, host)
    var background := host.get_node_or_null("Level0_Background") as BackgroundFactory
    if background == null:
        host.free()
        return _background_check(false, "compiled layer-0 controller missing")
    var sea := background.get_node("RuntimeSea/Visual") as Sprite2D
    var cloud := background.get_node("RuntimeCloud") as Node2D
    var foam := background.get_node("RuntimeFoam/Visual") as Sprite2D
    var combined := background.get_node("RuntimeCombined") as Node2D
    var still := background.get_node("StaticBackground") as Node2D
    var cloud_visual := cloud.get_node("Visual") as Sprite2D
    var ok: bool = _background_check(background.z_index == 0, "wrong background depth")
    ok = _background_check(background.get_child_count() == entries.size(), "changed pass count") and ok
    ok = _background_check(sea != null and cloud_visual != null and foam != null,
        "missing sprite visual") and ok
    if not ok:
        host.free()
        return false
    ok = _background_check(sea.get_meta("background_frame_id", "") == "E010", "wrong first frame") and ok
    ok = _background_check(not still.has_meta("background_fps"), "static block was animated") and ok
    ok = _background_check(cloud.scale == Vector2.ONE * 1.5 and cloud_visual.flip_h,
        "placement scale/flip lost") and ok
    background._process(0.25)
    ok = _background_check(sea.get_meta("background_frame_id", "") == "E011", "JSON fps ignored") and ok
    var next_origin: Array = factory.catalog.get_asset("E011").get("origin", [0, 0])
    ok = _background_check(sea.position == -Vector2(float(next_origin[0]), float(next_origin[1])),
        "animation frame origin ignored") and ok
    ok = _background_check(cloud.position.is_equal_approx(Vector2(7.5, 20)), "scroll velocity ignored") and ok
    ok = _background_check(combined.position.is_equal_approx(Vector2(100, 20.75)),
        "combined animation/scroll lost a stationary axis") and ok
    ok = _background_check(still.position == Vector2(75, 80), "static placement moved") and ok
    background._process(1.0)
    ok = _background_check(sea.get_meta("background_frame_id", "") == "E010", "clip did not loop") and ok
    ok = _background_check(int(foam.get_meta("background_frame_index", -1)) == 0,
        "independent foam cadence incorrect") and ok
    background._process(0.25)
    ok = _background_check(int(foam.get_meta("background_frame_index", -1)) == 1,
        "foam frame did not advance") and ok
    background._process(1000.0)
    var width: float = cloud_visual.texture.get_width() * cloud.scale.x
    var left: float = (-cloud_visual.position.x * cloud.scale.x) - width
    ok = _background_check(cloud.position.x >= left and cloud.position.x < 200.0 + left + width,
        "negative scroll escaped the canvas wrap range") and ok
    ok = _background_check(cloud.position.y == 20.0, "wrapping changed stationary Y") and ok
    cloud.free()
    background._process(0.25) # A removed placement must not leave a dangling runtime reference.
    background.configure([], factory.catalog, Vector2(200, 100))
    ok = _background_check(not background.is_processing(), "empty controller kept processing") and ok
    ok = _background_check(not combined.has_meta("background_fps"), "reconfigure left stale metadata") and ok
    # Legacy background groups consume the same JSON fields without a compiled pass.
    factory._place_group([{"id": "E010", "instance_id": "LegacySea", "x": 5, "y": 6,
        "animation": {"frames": frames, "fps": 2.0}}], host, "DistantRuins", false, Vector2(200, 100))
    var legacy := host.get_node("DistantRuins") as BackgroundFactory
    legacy._process(0.5)
    var legacy_visual := legacy.get_node("LegacySea/Visual") as Sprite2D
    ok = _background_check(legacy_visual.get_meta("background_frame_id", "") == "E011",
        "legacy background animation missing") and ok
    host.free()
    if ok:
        print("Background runtime passed: fps, sea/foam loops, scroll/wrap, origins, static compatibility, removal and legacy JSON")
    return ok
