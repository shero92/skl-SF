extends Node2D
class_name OceanBackground

## Reusable procedural-art ocean. E010 is seamlessly repeated and E011-E014
## form a four-frame translucent waves loop. E018 supplies the static cloud sky.
## The art itself remains flagged needs_cleanup until artist review.
var wave_tiles: Array[Sprite2D] = []
var wave_textures: Array[Texture2D] = []
var elapsed: float = 0.0
var frame_duration: float = 0.25
var last_frame: int = -1

func configure(info: Dictionary, catalog: AssetCatalog) -> void:
    var dimensions: Array = info.get("canvas_size", [1536, 1024])
    var w := float(dimensions[0])
    var h := float(dimensions[1])
    var tile_size := int(info.get("tile_size", 256))
    var frame_rate := maxf(0.5, float(info.get("fps", 5)))
    frame_duration = 1.0 / frame_rate

    var base_record: Dictionary = catalog.get_asset("E010")
    var base_path := String(base_record.get("texture_path", ""))
    if not ResourceLoader.exists(base_path):
        push_warning("Ocean base E010 missing; background falls back to room color")
        return
    var sea := load(base_path) as Texture2D
    for i in range(11, 15):
        var record: Dictionary = catalog.get_asset("E%03d" % i)
        var path := String(record.get("texture_path", ""))
        if ResourceLoader.exists(path):
            wave_textures.append(load(path) as Texture2D)

    var width_cells := int(ceil(w / tile_size))
    var height_cells := int(ceil(h / tile_size))
    for y in height_cells:
        for x in width_cells:
            var point := Vector2(x * tile_size, y * tile_size)
            var water := Sprite2D.new()
            water.name = "Water"
            water.texture = sea
            water.centered = false
            water.position = point
            water.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
            water.scale = Vector2(
                float(tile_size) / sea.get_width(),
                float(tile_size) / sea.get_height()
            )
            add_child(water)
            if not wave_textures.is_empty():
                var wave := Sprite2D.new()
                wave.name = "Waves"
                wave.texture = wave_textures[0]
                wave.centered = false
                wave.position = point
                wave.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
                wave.scale = Vector2(
                    float(tile_size) / wave.texture.get_width(),
                    float(tile_size) / wave.texture.get_height()
                )
                add_child(wave)
                wave_tiles.append(wave)

    var sky_record: Dictionary = catalog.get_asset("E018")
    var sky_path := String(sky_record.get("texture_path", ""))
    if ResourceLoader.exists(sky_path):
        var sky_texture := load(sky_path) as Texture2D
        var sky := Sprite2D.new()
        sky.name = "CloudSky"
        sky.centered = false
        sky.texture = sky_texture
        sky.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
        sky.scale = Vector2(
            w / sky_texture.get_width(),
            float(info.get("sky_height", 230)) / sky_texture.get_height()
        )
        add_child(sky)

func _process(delta: float) -> void:
    if wave_textures.is_empty():
        return
    elapsed += delta
    var now := int(elapsed / frame_duration) % wave_textures.size()
    if now == last_frame:
        return
    last_frame = now
    for sprite in wave_tiles:
        sprite.texture = wave_textures[now]
