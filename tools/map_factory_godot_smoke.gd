extends SceneTree

## Headless environment-only validation: build every registered map from latest JSON.
## Deliberately does not instantiate players, characters, dialogue or interface.
func _initialize() -> void:
    call_deferred("_run_smoke")

func _run_smoke() -> void:
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
    var ok := true
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
        var ground := built.get_node_or_null("Ground")
        var dimensions: Array = data.get("size", [0, 0])
        var expected_floor := int(dimensions[0]) * int(dimensions[1])
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
