extends RefCounted
class_name NavigationGrid
## Shared movement validator over a Map Factory snapshot's `navigation` block (schema_version 1).
## Agent: claude (Claude Code); model: Sonnet 5.5.
##
## Regions, links and the default come straight from the snapshot; cells that no region or link opens are
## closed (the snapshot default is respected). Only the "walk" mode is wired into gameplay today:
## "fly" and "swim" are parsed and queryable but no character uses them yet, so they are not claimed complete.
## Furniture and wall obstacles are still enforced by the room's StaticBody2D collision, not here.

const DEFAULT_FOOT_OFFSETS: Array[Vector2] = [Vector2(-10, -4), Vector2(10, -4), Vector2(-10, 4), Vector2(10, 4)]

var origin: Vector2 = Vector2.ZERO
var cell_size: float = 64.0
var grid_size: Vector2i = Vector2i.ZERO
var links: Array = []
var _modes_by_cell: Dictionary = {} # Vector2i -> Array of mode names
var _default_modes: Array = []


## Returns null for an empty/invalid block so maps without navigation keep unrestricted movement.
static func from_navigation(nav: Variant, world_offset: Vector2 = Vector2.ZERO) -> NavigationGrid:
    if typeof(nav) != TYPE_DICTIONARY or nav.is_empty() or int(nav.get("schema_version", 0)) != 1:
        return null
    var grid := NavigationGrid.new()
    var o: Array = nav.get("origin", [0, 0])
    grid.origin = world_offset + Vector2(float(o[0]), float(o[1]))
    grid.cell_size = float(nav.get("cell_size", 64))
    if grid.cell_size <= 0.0:
        return null
    var size: Array = nav.get("grid_size", [0, 0])
    grid.grid_size = Vector2i(int(size[0]), int(size[1]))
    var defaults: Dictionary = nav.get("default", {})
    for mode: String in ["walk", "fly", "swim"]:
        if bool(defaults.get(mode, false)):
            grid._default_modes.append(mode)
    for region: Dictionary in nav.get("regions", []):
        var rect: Array = region.get("rect", [0, 0, 0, 0])
        for y in range(int(rect[1]), int(rect[1]) + int(rect[3])):
            for x in range(int(rect[0]), int(rect[0]) + int(rect[2])):
                grid._open(Vector2i(x, y), region.get("allow", []))
    grid.links = nav.get("links", []).duplicate(true)
    for link: Dictionary in grid.links:
        for key: String in ["from", "to"]:
            var cell: Array = link.get(key, [])
            if cell.size() == 2:
                grid._open(Vector2i(int(cell[0]), int(cell[1])), link.get("modes", []))
    return grid


func _open(cell: Vector2i, modes: Array) -> void:
    var current: Array = _modes_by_cell.get(cell, [])
    for mode in modes:
        if not current.has(mode):
            current.append(mode)
    _modes_by_cell[cell] = current


func world_to_cell(point: Vector2) -> Vector2i:
    var local := point - origin
    return Vector2i(floori(local.x / cell_size), floori(local.y / cell_size))


func cell_center(cell: Vector2i) -> Vector2:
    return origin + (Vector2(cell) + Vector2(0.5, 0.5)) * cell_size


func is_cell_open(cell: Vector2i, mode: String = "walk") -> bool:
    if _modes_by_cell.has(cell):
        return _modes_by_cell[cell].has(mode)
    var inside := cell.x >= 0 and cell.y >= 0 and cell.x < grid_size.x and cell.y < grid_size.y
    return inside and _default_modes.has(mode) # unknown or outside cells are closed unless the snapshot opens them


func point_open(point: Vector2, mode: String = "walk") -> bool:
    return is_cell_open(world_to_cell(point), mode)


## True when every foot-footprint point stands on an open cell.
func footprint_open(position: Vector2, offsets: Array = DEFAULT_FOOT_OFFSETS, mode: String = "walk") -> bool:
    for offset: Vector2 in offsets:
        if not point_open(position + offset, mode):
            return false
    return true


## Motion that may actually be applied this step: the full motion when the footprint stays open,
## otherwise the axis that still works (slide along an edge), otherwise zero. Never lets the feet
## enter a closed cell, including on diagonals.
func allowed_motion(position: Vector2, motion: Vector2, offsets: Array = DEFAULT_FOOT_OFFSETS, mode: String = "walk") -> Vector2:
    if footprint_open(position + motion, offsets, mode):
        return motion
    var horizontal := Vector2(motion.x, 0.0)
    if motion.x != 0.0 and footprint_open(position + horizontal, offsets, mode):
        return horizontal
    var vertical := Vector2(0.0, motion.y)
    if motion.y != 0.0 and footprint_open(position + vertical, offsets, mode):
        return vertical
    return Vector2.ZERO
