extends "res://scenes/battle/tactical_battle_scene.gd"
## Rendering-only preview override; Session, moves, turns and damage remain base-scene code.
const ART_BASE := "res://game_factory/environment/ART-0041/v001/"
var art_textures: Dictionary = {}
func _ready() -> void:
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(ART_BASE+"manifest.json"))
	for item: Dictionary in manifest.items:
		art_textures[str(item.id)] = ImageTexture.create_from_image(Image.load_from_file("res://"+str(item.native_review_path)))
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	super._ready()
func marker(name: String, rect: Rect2) -> void:
	_board.draw_texture_rect(art_textures[name],rect,false,Color(1,1,1,0.75))
func _draw_board() -> void:
	if session == null:
		return
	_board.draw_rect(Rect2(Vector2.ZERO,Vector2(1536,1024)),Color("182330"))
	for y: int in range(session.size.y):
		for x: int in range(session.size.x):
			var cell := Vector2i(x,y)
			_board.draw_texture_rect(art_textures["field_grass_a" if (x+y)%2==0 else "field_grass_b"],cell_rect(cell),false)
	for cell: Vector2i in session.manager.blocked:
		var rect := cell_rect(cell)
		_board.draw_texture_rect(art_textures.field_rock_block,Rect2(rect.position+Vector2(0,-32),Vector2(64,96)),false)
	for cell: Vector2i in session.move_cells():
		marker("marker_move",cell_rect(cell))
	var acting = session.current()
	var target_demo_done := false
	for c: Dictionary in session.manager.combatants:
		var id := String(c.id)
		if int(_shown_hp.get(id,0))<=0:
			continue
		var rect := cell_rect(c.cell)
		var centre := rect.get_center()
		# Reuse existing shape stand-ins: this request does not create character art.
		_board.draw_circle(centre,22,TEAM_COLOR[c.team])
		_board.draw_string(_font,centre+Vector2(-20,5),session.display_name(id).left(4),HORIZONTAL_ALIGNMENT_LEFT,44,14,Color.WHITE)
		var ratio := float(_shown_hp[id])/float(session.max_hp(id))
		_board.draw_rect(Rect2(rect.position+Vector2(8,54),Vector2(48,5)),Color("222222"))
		_board.draw_rect(Rect2(rect.position+Vector2(8,54),Vector2(48*ratio,5)),Color("55cc55"))
		if acting != null and acting.id == c.id:
			marker("marker_active",rect)
		if c.team=="enemy" and not target_demo_done:
			marker("marker_target",rect)
			target_demo_done=true
	_board.draw_string(_font,Vector2(24,40),"ART-0041 | Existing tactical battle scene + rendering-only art preview",HORIZONTAL_ALIGNMENT_LEFT,1450,24,Color.WHITE)
	_board.draw_string(_font,Vector2(24,78),"Frozen Session. Existing unit shapes retained. Red marker is a visual demo, NOT attack-range logic.",HORIZONTAL_ALIGNMENT_LEFT,1450,18,Color.WHITE)
	_board.draw_string(_font,Vector2(24,110),"Native64px cells; nearest filter; marker opacity0.75. Production scene unchanged.",HORIZONTAL_ALIGNMENT_LEFT,1450,18,Color.WHITE)
	for row: int in range(3):
		var key: String = ["marker_move","marker_target","marker_active"][row]
		_board.draw_string(_font,Vector2(24,250+row*110),key+" on A / B",HORIZONTAL_ALIGNMENT_LEFT,300,16,Color.WHITE)
		for col: int in range(2):
			var rect := Rect2(Vector2(24+col*90,262+row*110),Vector2(64,64))
			_board.draw_texture_rect(art_textures["field_grass_a" if col==0 else "field_grass_b"],rect,false)
			marker(key,rect)
	_board.draw_string(_font,Vector2(24,740),"Source/native hashes and exact2px marker core checks are recorded in the ART manifest.",HORIZONTAL_ALIGNMENT_LEFT,1450,18,Color.WHITE)
