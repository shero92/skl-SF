extends SceneTree

## Four orientations are an environment-only rendering contract.
## No player, actor, NPC or dialogue scenes are loaded.
func _initialize() -> void:
    call_deferred("_test")

func _test() -> void:
    var builder := RoomFactory.new()
    var holder := Node2D.new()
    root.add_child(holder)
    var faces := ["north","east","south","west"]
    var expected_angles := [0.0,90.0,180.0,270.0]
    var entries: Array = []
    for i in range(4):
        var face: String = faces[i]
        entries.append({
            "instance_id":"Rotated_"+face,"asset_id":"P001",
            "position":[float(190+i*130),270.0],"scale":0.65,
            "collision":{"enabled":true,"size":[60,34],"offset":[0,-8]},
            "orientation":{"facing":face,"orientation_mode":"rotate",
                "turn_quarters":i,"resolved_asset_id":"P001"},
            "shadow":{"type":"none"}
        })
    var variants := ["P001","P002","P008","P014"]
    for i in range(4):
        entries.append({
            "instance_id":"Variant_"+faces[i],"asset_id":"P001",
            "position":[float(190+i*130),580.0],"scale":0.65,
            "collision":{"enabled":false},
            "orientation":{"facing":faces[i],"orientation_mode":"variants",
                "turn_quarters":i,"resolved_asset_id":variants[i]},
            "shadow":{"type":"none"}
        })
    builder._place_compiled_entries(entries,holder)
    var errors := 0
    for i in range(4):
        var obj := holder.get_node_or_null("Rotated_"+faces[i]) as Node2D
        if obj == null:
            push_error("Missing cardinal block "+faces[i])
            errors+=1
            continue
        var diff := absf(obj.rotation_degrees-expected_angles[i])
        if diff>0.02:
            push_error("Incorrect cardinal sprite rotation "+faces[i]+": "+str(obj.rotation_degrees))
            errors+=1
        if obj.get_node_or_null("SolidFootprint/FootprintShape") == null:
            push_error("Collision not attached to rotated node "+faces[i])
            errors+=1
        if obj.get_meta("facing","")!=faces[i]:
            push_error("Runtime facing metadata missing "+faces[i])
            errors+=1
        var variant := holder.get_node_or_null("Variant_"+faces[i]) as Node2D
        if variant == null or variant.get_meta("asset_id","")!=variants[i] or absf(variant.rotation_degrees)>0.001:
            push_error("Perspective variant not upright/correctly selected "+faces[i])
            errors+=1
        elif variant.get_node_or_null("Visual") == null or (variant.get_node("Visual") as Sprite2D).texture == null:
            push_error("Missing perspective variant PNG "+faces[i])
            errors+=1
    # Floor tile orientation is a separate pivot problem. Every 90° turn
    # must be around the TILE CENTER or the floor loses its grid alignment.
    for i in range(4):
        var tray := Node2D.new()
        holder.add_child(tray)
        var floor_data := {
            "size":[1,1],"ground_offset":[0,0],"tile_size":64,
            "floor_ids":["F014"],"tile_overrides":[{
                "x":0,"y":0,"id":"F014","facing":faces[i]}]
        }
        builder._paint_ground(floor_data,tray)
        var tile := tray.get_node_or_null("Floor_0_0_F014") as Sprite2D
        if tile == null or tile.position.distance_to(Vector2(32,32))>0.01 or absf(tile.rotation_degrees-expected_angles[i])>0.01:
            push_error("A rotated floor tile moved off its cell: "+faces[i])
            errors+=1
    # Depth sorting must allow rear walls to pass behind furniture and
    # nearby walls to occlude furniture in an angled/top-down scene.
    var raw: Variant=JSON.parse_string(FileAccess.get_file_as_string(
        "res://map_factory/maps/hero_room_01/latest.json"))
    if typeof(raw)==TYPE_DICTIONARY:
        var map_data: Dictionary=raw
        map_data["occlusion_mode"]="world_y_sort"
        var stage := Node2D.new()
        holder.add_child(stage)
        builder._build_five_levels(map_data,map_data["layer_stack"],stage)
        var depth := stage.get_node_or_null("WorldDepthSort") as Node2D
        if depth==null or not depth.y_sort_enabled:
            push_error("Unified wall/furniture depth sorting not created")
            errors+=1
        else:
            var walls := depth.get_node_or_null("Level2_Walls") as Node2D
            var decor := depth.get_node_or_null("Level3_Decorations") as Node2D
            if walls==null or decor==null or not walls.y_sort_enabled or not decor.y_sort_enabled or walls.z_index!=0 or decor.z_index!=0:
                push_error("World y-sort groups not sharing sorting depth")
                errors+=1
    else:
        push_error("Real map fixture missing")
        errors+=1
    if errors==0:
        print("CARDINAL_MAP_BLOCKS_OK: four 90-degree rotations, collision transforms, four drawn variant references")
    quit(0 if errors==0 else 1)
