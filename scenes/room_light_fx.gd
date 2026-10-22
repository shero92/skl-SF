extends Node2D
class_name RoomLightFX

## Reusable animated flame + alpha glow, using individually indexed PNGs.
var candle: Sprite2D
var glow: Sprite2D
var flame_frames: Array[Texture2D] = []
var phase: float = 0.0
var flame_fps: float = 6.0
var _last_frame: int = -1

func configure(info: Dictionary, catalog: AssetCatalog) -> void:
    var kind := String(info.get("kind", "lantern"))
    position = Vector2(float(info.get("x", 0)), float(info.get("y", 0)))
    var s := float(info.get("scale", 1.0))
    var glow_id := "D015" if kind == "lantern" else "D016"
    var glow_rec: Dictionary = catalog.get_asset(glow_id)
    var glow_path := String(glow_rec.get("texture_path", ""))
    if ResourceLoader.exists(glow_path):
        glow = Sprite2D.new()
        glow.texture = load(glow_path) as Texture2D
        glow.name = "Glow"
        glow.centered = true
        glow.modulate.a = float(info.get("glow_alpha", 0.65))
        glow.scale = Vector2.ONE * s
        glow.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
        add_child(glow)
    for i in range(12, 15):
        var rec: Dictionary = catalog.get_asset("D%03d" % i)
        var path := String(rec.get("texture_path", ""))
        if ResourceLoader.exists(path):
            flame_frames.append(load(path) as Texture2D)
    if not flame_frames.is_empty():
        candle = Sprite2D.new()
        candle.name = "AnimatedFlame"
        candle.centered = true
        candle.position = Vector2(0, -5.0 * s)
        candle.scale = Vector2.ONE * s * 0.45
        candle.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        candle.texture = flame_frames[0]
        add_child(candle)

func _process(delta: float) -> void:
    if candle == null or flame_frames.is_empty():
        return
    phase += delta
    var which := int(phase * flame_fps) % flame_frames.size()
    if which != _last_frame:
        candle.texture = flame_frames[which]
        _last_frame = which
    if glow != null:
        glow.modulate.a = 0.56 + 0.10 * sin(phase * 6.0)
