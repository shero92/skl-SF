extends Node2D
class_name BackgroundFactory

## Drives registered layer-0 sprites only; it never creates or substitutes art.
var _motions: Array[Dictionary] = []
var _elapsed: float = 0.0
var _canvas_size: Vector2 = Vector2.ZERO

func configure(entries: Array, source: AssetCatalog, canvas_size: Vector2) -> void:
    for previous: Dictionary in _motions:
        if is_instance_valid(previous["node"]):
            var previous_node: Node2D = previous["node"]
            for key: String in ["background_frame_ids", "background_fps", "background_velocity"]:
                if previous_node.has_meta(key):
                    previous_node.remove_meta(key)
    _motions.clear()
    _elapsed = 0.0
    _canvas_size = canvas_size
    for value: Variant in entries:
        if not value is Dictionary:
            continue
        var record: Dictionary = value
        if not record.has("animation") and not record.has("scroll"):
            continue
        var label: String = String(record.get("instance_id", record.get("asset_id", record.get("id", ""))))
        var node: Node2D = get_node_or_null(NodePath(label)) as Node2D
        if node == null:
            continue
        var visual: Sprite2D = node.get_node_or_null("Visual") as Sprite2D
        if visual == null or visual.texture == null:
            continue
        var state: Dictionary = {"node": node, "visual": visual, "start": node.position,
            "velocity": Vector2.ZERO, "textures": [], "origins": [], "ids": [],
            "fps": 0.0, "frame": -1}
        var animation: Dictionary = record.get("animation", {})
        var ids: Array = animation.get("frames", [])
        var fps: float = float(animation.get("fps", 0.0))
        if not ids.is_empty() and is_finite(fps) and fps > 0.0:
            var textures: Array[Texture2D] = []
            var origins: Array[Vector2] = []
            for id: Variant in ids:
                var frame: Dictionary = source.get_asset(String(id))
                var texture: Texture2D = _load_frame(frame)
                if texture == null:
                    # Never skip a missing frame and silently change the clip timing.
                    textures.clear()
                    break
                var origin: Array = frame.get("origin", [0, 0])
                textures.append(texture)
                origins.append(Vector2(float(origin[0]), float(origin[1])))
            if textures.size() == ids.size():
                state["textures"] = textures
                state["origins"] = origins
                state["ids"] = ids.duplicate()
                state["fps"] = fps
                node.set_meta("background_frame_ids", ids.duplicate())
                node.set_meta("background_fps", fps)
        var scroll: Dictionary = record.get("scroll", {})
        var velocity: Vector2 = Vector2(float(scroll.get("vx", 0.0)), float(scroll.get("vy", 0.0)))
        if velocity.is_finite():
            state["velocity"] = velocity
        if not (state["textures"] as Array).is_empty() or state["velocity"] != Vector2.ZERO:
            node.set_meta("background_velocity", state["velocity"])
            _motions.append(state)
    set_process(not _motions.is_empty())
    _update_sprites()

func _load_frame(record: Dictionary) -> Texture2D:
    if record.is_empty() or String(record.get("category", "")) in ["characters", "ui", "shadows"]:
        push_warning("Layer-0 animation references an invalid environment frame")
        return null
    var path: String = String(record.get("texture_path", ""))
    if path.is_empty() or not ResourceLoader.exists(path):
        push_warning("Layer-0 animation texture is unavailable: " + path)
        return null
    return load(path) as Texture2D

func _process(delta: float) -> void:
    if not is_finite(delta) or delta < 0.0:
        return
    _elapsed += delta
    _update_sprites()

func _update_sprites() -> void:
    for state: Dictionary in _motions:
        if not is_instance_valid(state["node"]) or not is_instance_valid(state["visual"]):
            continue
        var node: Node2D = state["node"]
        var visual: Sprite2D = state["visual"]
        var textures: Array = state["textures"]
        if not textures.is_empty():
            var frame: int = int(floor(_elapsed * float(state["fps"]))) % textures.size()
            if frame != int(state["frame"]):
                visual.texture = textures[frame] as Texture2D
                visual.position = -(state["origins"][frame] as Vector2)
                visual.set_meta("background_frame_index", frame)
                visual.set_meta("background_frame_id", state["ids"][frame])
                state["frame"] = frame
        var velocity: Vector2 = state["velocity"]
        if velocity == Vector2.ZERO:
            continue
        var point: Vector2 = (state["start"] as Vector2) + velocity * _elapsed
        # Wrap only moving axes, after the full sprite leaves the canvas. This
        # preserves stationary coordinates and supports either scroll direction.
        var extent: Vector2 = visual.texture.get_size() * node.scale.abs()
        var origin: Vector2 = -visual.position * node.scale.abs()
        if velocity.x != 0.0 and _canvas_size.x > 0.0:
            var left: float = origin.x - extent.x
            point.x = left + fposmod(point.x - left, _canvas_size.x + extent.x)
        if velocity.y != 0.0 and _canvas_size.y > 0.0:
            var top: float = origin.y - extent.y
            point.y = top + fposmod(point.y - top, _canvas_size.y + extent.y)
        node.position = point
