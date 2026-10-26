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
    var ok := background_ok
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
                if section == null or section.get_child_count() != records.size():
                    push_error("Five-pass wrong size: " + id + "/" + String(pass_id))
                    ok = false
                    continue
                for record in records:
                    var label: String = String(record.get("instance_id",""))
                    var node := section.get_node_or_null(label)
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
                    var p: Array = record.get("position",[0,0])
                    if node.position.distance_to(Vector2(float(p[0]),float(p[1]))) > 0.5:
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
