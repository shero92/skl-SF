extends SceneTree
## Measurement only (no assertions): node counts, texture uses and build time of a map build.
## Usage: godot --headless --path . --script res://tools/measure_room_build.gd -- [map_id] [runs]
## Agent: claude (Claude Code); model: Sonnet 5.5. Headless timings exclude GPU cost.


func _count(node: Node, stats: Dictionary, textures: Dictionary) -> void:
	stats.nodes += 1
	if node is Sprite2D:
		stats.sprites += 1
		var texture := (node as Sprite2D).texture
		if texture != null:
			textures[texture.get_instance_id()] = texture
	elif node is Polygon2D:
		stats.polygons += 1
	elif node is StaticBody2D:
		stats.bodies += 1
	for child in node.get_children():
		_count(child, stats, textures)


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var map_id: String = args[0] if args.size() > 0 else "hero_room_01"
	var runs: int = int(args[1]) if args.size() > 1 else 5
	for run in runs:
		var holder := Node2D.new()
		root.add_child(holder)
		var started := Time.get_ticks_usec()
		var room := RoomFactory.new().build_latest(map_id, holder)
		var elapsed_ms := (Time.get_ticks_usec() - started) / 1000.0
		var stats := {"nodes": 0, "sprites": 0, "polygons": 0, "bodies": 0}
		var textures := {}
		_count(room, stats, textures)
		var bytes := 0
		for texture: Texture2D in textures.values():
			var image := texture.get_image()
			if image != null:
				bytes += image.get_data().size()
		print("RUN %d map=%s build_ms=%.1f nodes=%d sprites=%d polygons=%d bodies=%d unique_textures=%d texture_mb=%.1f catalog_parses=%d" % [
			run, map_id, elapsed_ms, stats.nodes, stats.sprites, stats.polygons, stats.bodies, textures.size(),
			bytes / 1048576.0, AssetCatalog.load_count])
		holder.free()
	quit(0)
