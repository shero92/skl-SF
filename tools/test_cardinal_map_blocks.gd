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
        if obj.get_node_or_null("SolidFootprint/CollisionShape2D") == null:
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
    if errors==0:
        print("CARDINAL_MAP_BLOCKS_OK: four 90-degree rotations, collision transforms, four drawn variant references")
    quit(0 if errors==0 else 1)
