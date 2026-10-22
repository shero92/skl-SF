extends RefCounted
class_name ShadowFactory

static func create_shadow(config: Dictionary, sprite_size: Vector2) -> Node2D:
    var root := Node2D.new()
    root.name = "Shadow"
    if String(config.get("type", "none")) == "none":
        return root
    var shape := Polygon2D.new()
    var radius := Vector2(maxf(8.0, sprite_size.x * 0.33), maxf(4.0, sprite_size.y * 0.08))
    var points := PackedVector2Array()
    for i in 24:
        var a := TAU * float(i) / 24.0
        points.append(Vector2(cos(a) * radius.x, sin(a) * radius.y))
    shape.polygon = points
    shape.color = Color(0.07, 0.12, 0.23, float(config.get("opacity", 0.30)))
    shape.position = Vector2(float(config.get("offset_x", 4)), float(config.get("offset_y", 3)))
    shape.z_index = -1
    root.add_child(shape)
    return root
