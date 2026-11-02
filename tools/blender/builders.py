"""Parametric Map Factory pieces (run inside Blender). Each builder returns (objects, anchors).

anchors maps names to world points (mathutils.Vector) that render_part converts to pixels.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import lib

WALL_FRONT = {"north": "south", "south": "north", "east": "west", "west": "east"}


def _prism(name, outline, z_top, z_bottom, material):
    """Vertical prism from a 2D outline (counter-clockwise), top at z_top."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    top = [bm.verts.new((x, y, z_top)) for x, y in outline]
    face = bm.faces.new(top)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    down = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=down, vec=(0, 0, z_bottom - z_top))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width, mod.segments, mod.limit_method = 0.012, 2, "ANGLE"
    return obj


def calibration_tile(spec, facing):
    """A flat 1x1 tile at z=0: must render exactly tile_px x tile_px (projection check)."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(0.5, 0.5, 0.0))
    tile = bpy.context.active_object
    tile.data.materials.append(lib.flat("calib", (0.8, 0.6, 0.35), roughness=1.0))
    return [tile], {"tile_top_left": Vector((0.0, 1.0, 0.0))}


def wall_run(spec, facing):
    """A modular straight run of the Hero Room's golden limestone wall.

    facing = the wall's position in the room (north wall shows its face to the camera)."""
    p = spec.get("params", {})
    length, height, thick = p.get("length", 1.0), p.get("height", 2.25), p.get("thickness", 0.5)
    row_h = p.get("row_height", 0.28)
    gap = p.get("joint", 0.022)
    r = lib.rng(p.get("seed", 7))
    stone = lib.limestone("wall_stone", seed=r.random() * 10)
    cap_stone = lib.limestone("cap_stone", base=(0.74, 0.56, 0.32), dark=(0.44, 0.30, 0.14), seed=r.random() * 10)
    mortar = lib.flat("mortar", (0.30, 0.22, 0.14), roughness=1.0)
    gold = lib.flat("gold_trim", (0.83, 0.62, 0.22), roughness=0.32, metallic=1.0)
    objs = [lib.block("core", (length - 0.002, thick - 0.06, height - 0.04), (0, thick / 2, (height - 0.04) / 2), mortar, bevel=0.0)]
    rows = max(1, int((height - 0.14) / row_h))
    z = 0.0
    for row in range(rows):
        x = -length / 2 - (r.uniform(0.1, 0.3) if row % 2 else 0.0)
        while x < length / 2 - 0.02:
            w = r.uniform(0.32, 0.58)
            x0, x1 = max(x, -length / 2), min(x + w, length / 2)
            if x1 - x0 > 0.05:
                size = (x1 - x0 - gap, thick + r.uniform(-0.015, 0.012), row_h - gap)
                loc = ((x0 + x1) / 2, thick / 2 - r.uniform(-0.008, 0.012), z + row_h / 2)
                objs.append(lib.block("stone", size, loc, stone, bevel=r.uniform(0.018, 0.034),
                                      rotation_z=r.uniform(-0.006, 0.006)))
            x += w
        z += row_h
    band_h = 0.035
    objs.append(lib.block("gold_band", (length, 0.03, band_h), (0, -0.012, z + band_h / 2), gold, bevel=0.006))
    z += band_h
    cap_h = height - z
    # connect_caps: the coping is cut at fixed half-tile joints so adjacent runs share one continuous course.
    connect = p.get("connect_caps", False)
    x = -length / 2
    while x < length / 2 - 0.02:
        w = 0.5 if connect else r.uniform(0.45, 0.7)
        x0, x1 = x, min(x + w, length / 2)
        objs.append(lib.block("cap", (x1 - x0 - gap * 0.6, thick + 0.07, cap_h), ((x0 + x1) / 2, thick / 2, z + cap_h / 2),
                              cap_stone, bevel=0.03))
        x += w
    # Corner quoins: alternating long/short blocks at the run ends, flush with the coping.
    for end in (-1, 1) if p.get("quoins", False) else ():
        for row in range(rows):
            qw = 0.26 if row % 2 else 0.18
            objs.append(lib.block("quoin", (qw, thick + 0.03, row_h - gap), (end * (length / 2 - qw / 2), thick / 2,
                                  row * row_h + row_h / 2), cap_stone, bevel=0.03))
    if p.get("ivy", True):
        objs += lib.ivy("ivy", (-length / 2, length / 2), -0.03, height, r, density=p.get("ivy_density", 1.0),
                        hang=p.get("ivy_hang", 0.9), flowers=p.get("ivy_flowers", 0.12))
    anchors = {"foot_center_front": Vector((0.0, 0.0, 0.0)), "foot_left": Vector((-length / 2, 0.0, 0.0)),
               "foot_right": Vector((length / 2, 0.0, 0.0)), "top_center_front": Vector((0.0, 0.0, height))}
    lib.rotate_group(objs, WALL_FRONT[facing], pivot=(0.0, thick / 2))
    from mathutils import Matrix
    import math
    rot = (Matrix.Translation(Vector((0, thick / 2, 0))) @ Matrix.Rotation(math.radians(lib.FRONT_ROTATION[WALL_FRONT[facing]]), 4, "Z")
           @ Matrix.Translation(Vector((0, -thick / 2, 0))))
    # Side walls lean (foot fixed on the floor edge, top shifted outward) so their inner face shows.
    k = p.get("lean", 0.0)
    if k:
        lib.lean(objs, k)
        rot = lib.lean_matrix(k) @ rot
    return objs, {k_: rot @ v for k_, v in anchors.items()}


def broken_floor_edge(spec, facing):
    """Golden limestone floor tile (2x2 pavers) whose front edge breaks off above the cliff.

    params.kind: edge | corner_left | corner_right; params.seed picks the variation."""
    p = spec.get("params", {})
    kind, depth = p.get("kind", "edge"), p.get("thickness", 0.22)
    r = lib.rng(p.get("seed", 3))
    stone = lib.limestone("floor_stone", base=(0.70, 0.52, 0.30), dark=(0.42, 0.28, 0.13), seed=r.random() * 10)
    rubble = lib.limestone("rubble", base=(0.58, 0.42, 0.24), dark=(0.32, 0.21, 0.10), seed=r.random() * 10)
    gap, n = 0.02, 2
    size = 1.0 / n
    broken_front = True
    broken_left, broken_right = kind == "corner_left", kind == "corner_right"
    objs = []

    def ragged(a, b, steps, inward, axis):
        pts = []
        for i in range(steps + 1):
            t = i / steps
            bite = 0.0 if i in (0, steps) else r.uniform(0.02, inward)
            pts.append((a + (b - a) * t, bite) if axis == "x" else (bite, a + (b - a) * t))
        return pts

    for ix in range(n):
        for iy in range(n):
            x0, y0 = ix * size + gap / 2, iy * size + gap / 2
            x1, y1 = (ix + 1) * size - gap / 2, (iy + 1) * size - gap / 2
            south = broken_front and iy == 0
            west = broken_left and ix == 0
            east = broken_right and ix == n - 1
            outline = []
            if south:
                for x, bite in ragged(x0, x1, 6, 0.16, "x"):
                    outline.append((x, y0 + bite))
            else:
                outline += [(x0, y0), (x1, y0)]
            if east:
                for bite, y in ragged(y0, y1, 6, 0.16, "y")[1:]:
                    outline.append((x1 - bite, y))
            else:
                outline.append((x1, y1))
            outline.append((x0, y1))
            if west:
                for bite, y in reversed(ragged(y0, y1, 6, 0.16, "y")[1:-1]):
                    outline.append((x0 + bite, y))
            dedup = []
            for pt in outline:
                if not dedup or (abs(dedup[-1][0] - pt[0]) > 1e-4 or abs(dedup[-1][1] - pt[1]) > 1e-4):
                    dedup.append(pt)
            top = r.uniform(-0.006, 0.006)
            objs.append(_prism("paver", dedup, top, -depth, stone))
    for i in range(p.get("chips", 3)):
        cx = r.uniform(0.1, 0.9)
        cy = r.uniform(0.02, 0.12)
        s = r.uniform(0.05, 0.1)
        chip = [(cx - s, cy - s * 0.6), (cx + s * 0.9, cy - s * 0.7), (cx + s, cy + s * 0.5), (cx - s * 0.7, cy + s * 0.8)]
        objs.append(_prism("chip", chip, 0.03 + r.uniform(0, 0.02), -0.02, rubble))
    # Terrace cliff contact: ragged rock courses below the broken edge(s), `cliff` tiles deep (0.8 / 1.0 variants).
    cliff = p.get("cliff", 0.0)
    sides = ["south"] + (["west"] if broken_left else []) + (["east"] if broken_right else [])
    for side in sides if cliff else []:
        z = -depth
        while z > -depth - cliff + 1e-3:
            h = min(r.uniform(0.14, 0.24), z + depth + cliff)
            t = 0.0
            while t < 1.0 - 1e-3:
                w = min(r.uniform(0.18, 0.34), 1.0 - t)
                inset = 0.04 + (-z - depth) * 0.12 + r.uniform(0.0, 0.05)
                c = t + w / 2
                loc = {"south": (c, inset + 0.08), "west": (inset + 0.08, c), "east": (1.0 - inset - 0.08, c)}[side]
                size = (w - 0.015, 0.16, h - 0.015) if side == "south" else (0.16, w - 0.015, h - 0.015)
                objs.append(lib.block("cliff", size, (*loc, z - h / 2), rubble, bevel=r.uniform(0.02, 0.04),
                                      rotation_z=r.uniform(-0.05, 0.05)))
                t += w
            z -= h
    anchors = {"tile_top_left": Vector((0.0, 1.0, 0.0)), "tile_top_right": Vector((1.0, 1.0, 0.0)),
               "tile_bottom_left": Vector((0.0, 0.0, 0.0)), "tile_bottom_right": Vector((1.0, 0.0, 0.0))}
    return objs, anchors


def path_segments(path, inside):
    """Per segment of a floor-edge polyline: (origin, angle, length, outward normal).

    Pieces are built in a local frame (x along 0..length, front face at y = 0 facing -y, body toward +y);
    origin/angle place that frame so the front faces the room (`inside` = left | right of the path)."""
    segs = []
    for (x0, y0), (x1, y1) in zip(path, path[1:]):
        dx, dy = x1 - x0, y1 - y0
        length = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)
        left = (-dy / length, dx / length)
        if inside == "left":
            segs.append(((x1, y1), theta + math.pi, length, (-left[0], -left[1])))
        else:
            segs.append(((x0, y0), theta, length, left))
    return segs


def floor_side_region(path, inside, depth):
    """Ground polygon on the room side of a mostly north-south floor-edge path, `depth` tiles wide.

    Used as the shadow catcher of a side wall: its shadow lands on the floor, never on the sea outside."""
    out = path_segments(path, inside)[0][3]
    sign = -1.0 if out[0] > 0 else 1.0
    xs = [x for x, _ in path]
    edge = (max(xs) if sign > 0 else min(xs)) + sign * depth
    return [list(v) for v in path] + [[edge, path[-1][1]], [edge, path[0][1]]]


def side_wall_path(spec, facing):
    """One continuous ruined side wall following the floor edge steps (Hero Room v3).

    params.path: floor-edge vertices in tiles (x = column, y = -row, grid top-left = origin);
    params.inside: which side of the path the room is on; the inner face stands on the edge and the
    body extends outward. Low masonry body with broken crenellations, corner pillars, foot rubble and
    ivy, joined into one mesh and leaned (x += lean * z) so the inner face shows."""
    p = spec.get("params", {})
    path = [tuple(v) for v in p["path"]]
    height, thick = p.get("height", 1.1), p.get("thickness", 0.45)
    row_h, gap = p.get("row_height", 0.26), p.get("joint", 0.022)
    r = lib.rng(p.get("seed", 5))
    # Colours (linear RGB) default to the v3 render; v4 specs pass the golden palette (lib.GOLDEN_*).
    spec_level = p.get("specular")
    stone = lib.limestone("wall_stone", base=tuple(p.get("stone_base", (0.70, 0.49, 0.25))),
                          dark=tuple(p.get("stone_dark", (0.38, 0.24, 0.10))), seed=r.random() * 10, specular=spec_level)
    cap_stone = lib.limestone("cap_stone", base=tuple(p.get("cap_base", (0.76, 0.57, 0.31))),
                              dark=tuple(p.get("cap_dark", (0.45, 0.30, 0.13))), seed=r.random() * 10, specular=spec_level)
    mortar = lib.flat("mortar", tuple(p.get("mortar", (0.28, 0.20, 0.12))), roughness=1.0)
    if p.get("shadow_inside"):
        spec["shadow_region"] = floor_side_region(path, p.get("inside", "left"), p["shadow_inside"])
    objs = []
    segs = path_segments(path, p.get("inside", "left"))
    for origin, angle, length, _out in segs:
        local = [lib.block("core", (length, thick - 0.06, height - 0.06), (length / 2, thick / 2, (height - 0.06) / 2),
                           mortar, bevel=0.0)]
        # Ruined top line: the body top dips in places, so the course count varies along the run.
        top = []
        x = 0.0
        while x < length - 1e-3:
            w = min(r.uniform(0.3, 0.42), length - x)
            top.append((x, x + w, height - (r.uniform(0.0, 0.28) if r.random() < 0.3 else 0.0)))
            x += w
        rows = max(1, int(height / row_h))
        for row in range(rows):
            z = row * row_h
            x = -(r.uniform(0.1, 0.25) if row % 2 else 0.0)
            while x < length - 0.02:
                w = r.uniform(0.3, 0.55)
                x0, x1 = max(x, 0.0), min(x + w, length)
                limit = min(h for a, b, h in top if a < x1 and b > x0)
                if x1 - x0 > 0.05 and z + row_h <= limit + 1e-3:
                    size = (x1 - x0 - gap, thick + r.uniform(-0.015, 0.012), row_h - gap)
                    loc = ((x0 + x1) / 2, thick / 2 - r.uniform(-0.008, 0.012), z + row_h / 2)
                    local.append(lib.block("stone", size, loc, stone, bevel=r.uniform(0.02, 0.038),
                                           rotation_z=r.uniform(-0.008, 0.008)))
                x += w
        body_top = rows * row_h
        if p.get("coping", False):
            # Continuous coping course over the intact stretches, so the segments read as one connected wall.
            for a, b, h in top:
                if h >= height - 1e-3:
                    local.append(lib.block("coping", (b - a + 0.01, thick + 0.06, 0.07), ((a + b) / 2, thick / 2, body_top + 0.035),
                                           cap_stone, bevel=0.025))
            body_top += 0.07
        # Broken crenellations: merlons on the intact stretches, some missing or snapped short.
        for a, b, h in top:
            if h < height - 1e-3 or r.random() < 0.3:
                continue
            mh = r.uniform(0.12, 0.3)
            local.append(lib.block("merlon", (b - a - gap * 2, thick + 0.05, mh), ((a + b) / 2, thick / 2, body_top + mh / 2),
                                   cap_stone, bevel=0.03, rotation_z=r.uniform(-0.03, 0.03)))
        for _ in range(int(length * p.get("rubble", 2))):
            s = r.uniform(0.07, 0.14)
            local.append(lib.block("rubble", (s, s * 0.9, s * 0.7), (r.uniform(0.1, length - 0.1), -r.uniform(0.02, 0.1), s * 0.3),
                                   stone, bevel=0.025, rotation_z=r.uniform(0, 3.1)))
        if p.get("ivy", True):
            local += lib.ivy("ivy", (0.0, length), -0.03, body_top, r, density=p.get("ivy_density", 2.0),
                             hang=p.get("ivy_hang", 0.8), flowers=p.get("ivy_flowers", 0.3),
                             leaf_scale=p.get("ivy_leaf_scale", 2.0))
        m = Matrix.Translation(Vector((origin[0], origin[1], 0.0))) @ Matrix.Rotation(angle, 4, "Z")
        bpy.context.view_layer.update()
        for obj in local:
            obj.matrix_world = m @ obj.matrix_world
        objs += local
    # Corner pillars fill the joints where the path steps in or out.
    for i in range(1, len(path) - 1):
        oa, ob = segs[i - 1][3], segs[i][3]
        cx, cy = path[i][0] + thick / 2 * (oa[0] + ob[0]), path[i][1] + thick / 2 * (oa[1] + ob[1])
        ph = height + r.uniform(0.05, 0.25)
        objs.append(lib.block("pillar", (thick + 0.04, thick + 0.04, ph), (cx, cy, ph / 2), cap_stone, bevel=0.035))
        if p.get("coping", False):
            objs.append(lib.block("pillar_cap", (thick + 0.1, thick + 0.1, 0.06), (cx, cy, ph + 0.03), cap_stone, bevel=0.02))
    lib.lean(objs, p.get("lean", 0.0))
    joined = lib.join(objs, "side_wall")
    return [joined], {"grid_origin": Vector((0.0, 0.0, 0.0))}


def _golden(p, r, name="stone", cap=False):
    base, dark = lib.GOLDEN_CAP if cap else lib.GOLDEN_STONE
    return lib.limestone(name, base=tuple(p.get(name + "_base", base)), dark=tuple(p.get(name + "_dark", dark)),
                         seed=r.random() * 10, specular=p.get("specular", 0.2))


def entrance_stairs(spec, facing):
    """Carved limestone stairs descending south from the floor front edge (ART-0025).

    Local frame: the floor front edge is y = 0, z = 0; steps go toward the camera (-y) and down. Each
    tread is two or three worn blocks; stepped cheek walls flank the treads. Anchor top_center = the
    middle of the floor front edge, so the piece hangs below the last floor row."""
    p = spec.get("params", {})
    n, width = p.get("steps", 3), p.get("tread_width", 2.42)
    run, rise = p.get("run", 0.34), p.get("rise", 0.2)
    cheek, cheek_h = p.get("cheek_width", 0.5), p.get("cheek_height", 0.22)
    r = lib.rng(p.get("seed", 9))
    stone, cap = _golden(p, r), _golden(p, r, "cap", cap=True)
    joint = lib.flat("joint", (0.16, 0.09, 0.035), roughness=1.0)
    bottom = -(n * rise + p.get("foundation", 0.35))
    objs = []
    # Nosing slab: hides the joint with the floor tile above.
    objs.append(lib.block("nosing", (width + 0.04, 0.09, 0.06), (0, -0.04, -0.03), cap, bevel=0.02))
    for i in range(1, n + 1):
        y0, y1, top = -i * run, -(i - 1) * run, -i * rise
        objs.append(lib.block("core", (width - 0.02, run - 0.01, top - bottom - 0.01), (0, (y0 + y1) / 2, (top + bottom) / 2),
                              joint, bevel=0.0))
        x = -width / 2
        while x < width / 2 - 0.05:
            w = min(r.uniform(0.6, 1.1), width / 2 - x)
            if width / 2 - (x + w) < 0.3:
                w = width / 2 - x
            wear = r.uniform(0.0, 0.02)
            objs.append(lib.block("tread", (w - 0.02, run + 0.02, top - bottom - wear), (x + w / 2, (y0 + y1) / 2 - 0.01,
                                  (top - wear + bottom) / 2), stone, bevel=r.uniform(0.03, 0.05), rotation_z=r.uniform(-0.01, 0.01)))
            x += w
        for side in (-1, 1):
            cx = side * (width / 2 + cheek / 2)
            ct = -(i - 1) * rise + cheek_h
            objs.append(lib.block("cheek", (cheek, run + 0.01, ct - bottom), (cx, (y0 + y1) / 2, (ct + bottom) / 2), stone,
                                  bevel=0.035, rotation_z=r.uniform(-0.01, 0.01)))
            objs.append(lib.block("cheek_cap", (cheek + 0.05, run + 0.03, 0.08), (cx, (y0 + y1) / 2, ct + 0.03), cap,
                                  bevel=0.03))
    for _ in range(p.get("chips", 4)):
        s = r.uniform(0.05, 0.09)
        i = r.randint(1, n)
        objs.append(lib.block("chip", (s, s * 0.8, s * 0.6), (r.uniform(-width / 2 + 0.1, width / 2 - 0.1),
                              -i * run + r.uniform(0.03, 0.1), -i * rise + s * 0.3), stone, bevel=0.02, rotation_z=r.uniform(0, 3)))
    total = width / 2 + cheek
    anchors = {"top_center": Vector((0.0, 0.0, 0.0)), "top_left": Vector((-total, 0.0, 0.0)),
               "top_right": Vector((total, 0.0, 0.0))}
    # Newel plinths on the bottom cheek caps: the rope posts (ART-0024) stand on these anchors.
    newel = p.get("newel", 0.0)
    for side, key in ((-1, "post_left"), (1, "post_right")) if newel else ():
        cx, cy, ct = side * (width / 2 + cheek / 2), -(n - 0.5) * run, -(n - 1) * rise + cheek_h + 0.07
        objs.append(lib.block("newel", (newel, newel, 0.1), (cx, cy, ct + 0.05), cap, bevel=0.03))
        anchors[key] = Vector((cx, cy, ct + 0.1))
    return objs, anchors


def _flat_poly(name, pts, z, material, depth=0.004):
    return _prism(name, pts, z, z - depth, material)


def _rhombus(hx, hy, s=1.0):
    return [(0.0, -hy * s), (hx * s, 0.0), (0.0, hy * s), (-hx * s, 0.0)]


def compass_inlay(spec, facing):
    """Flat sapphire-and-gold compass rose set into the floor as a 45-degree rhombus (ART-0022).

    params.half_x/half_y: half diagonals in tiles (current 64 px grid: 267x259 px -> 2.086/2.023).
    Stacked flat layers (a few mm apart) render as one inlay with crisp metal edges; anchor center."""
    p = spec.get("params", {})
    hx, hy = p.get("half_x", 2.086), p.get("half_y", 2.023)
    r = lib.rng(p.get("seed", 4))
    gold, gold_dark = lib.gold("gold"), lib.flat("gold_dark", (0.45, 0.26, 0.05), roughness=0.4, metallic=1.0)
    deep = lib.sapphire("sapphire_deep", (0.01, 0.04, 0.20))
    field = lib.sapphire("sapphire", tuple(p.get("field", (0.03, 0.13, 0.48))))
    ivory = lib.flat("ivory", (0.80, 0.70, 0.52), roughness=0.4)
    ivory_dark = lib.flat("ivory_dark", (0.48, 0.38, 0.24), roughness=0.45)
    stone = _golden(p, r)
    objs = [_flat_poly("rim", _rhombus(hx, hy), 0.004, gold),
            _flat_poly("band", _rhombus(hx, hy, 0.95), 0.006, deep),
            _flat_poly("bead", _rhombus(hx, hy, 0.885), 0.008, gold),
            _flat_poly("field", _rhombus(hx, hy, 0.86), 0.010, field)]
    # Gold studs along the dark band.
    for k in range(4):
        (ax, ay), (bx, by) = _rhombus(hx, hy, 0.915)[k], _rhombus(hx, hy, 0.915)[(k + 1) % 4]
        for t in (0.25, 0.5, 0.75):
            cx, cy = ax + (bx - ax) * t, ay + (by - ay) * t
            objs.append(_flat_poly("stud", [(cx, cy - 0.035), (cx + 0.035, cy), (cx, cy + 0.035), (cx - 0.035, cy)], 0.009, gold))
    # Inner ring of golden stone around the rose.
    ring = p.get("ring", 0.62)
    circle = [(math.cos(a) * hx * ring, math.sin(a) * hy * ring) for a in (i * math.tau / 48 for i in range(48))]
    inner = [(x * 0.9, y * 0.9) for x, y in circle]
    objs += [_flat_poly("ring_gold", circle, 0.012, gold), _flat_poly("ring_stone", [(x * 0.96, y * 0.96) for x, y in circle], 0.013, stone),
             _flat_poly("ring_field", inner, 0.014, deep)]

    def point(angle, length, half_w, z, light, dark):
        # One faceted star point: two triangles (lit / shaded half), tip toward `angle`.
        ux, uy = math.cos(angle), math.sin(angle)
        vx, vy = -uy, ux
        tip = (ux * length * hx, uy * length * hy)
        side_a = (vx * half_w * hx, vy * half_w * hy)
        side_b = (-vx * half_w * hx, -vy * half_w * hy)
        return [_flat_poly("pt_a", [(0.0, 0.0), side_a, tip], z, light), _flat_poly("pt_b", [(0.0, 0.0), tip, side_b], z, dark)]

    for k in range(4):   # short diagonal points (ivory), then the long cardinal points (gold) on top
        objs += point(math.pi / 4 + k * math.pi / 2, p.get("short_point", 0.5), 0.09, 0.016, ivory, ivory_dark)
    for k in range(4):   # cardinal points aim at the rhombus vertices
        objs += point(k * math.pi / 2, p.get("long_point", 0.84), 0.12, 0.018, gold, gold_dark)
    if p.get("cobalt_ticks", False):
        # Cobalt-gold dial: 16 gold ticks on the ring, cardinal ones longer, over a cobalt band inset.
        objs.append(_flat_poly("cobalt_band", [(x * 0.93, y * 0.93) for x, y in circle], 0.0135, deep))
        for i in range(16):
            a = i * math.tau / 16
            l0, l1, w = (0.80, 0.96, 0.03) if i % 4 == 0 else (0.86, 0.95, 0.018)
            ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a) * w, math.cos(a) * w
            pts = [(ux * l0 * ring * hx + vx, uy * l0 * ring * hy + vy), (ux * l0 * ring * hx - vx, uy * l0 * ring * hy - vy),
                   (ux * l1 * ring * hx - vx, uy * l1 * ring * hy - vy), (ux * l1 * ring * hx + vx, uy * l1 * ring * hy + vy)]
            objs.append(_flat_poly("tick", pts, 0.0145, gold))
    hub = [(math.cos(a) * 0.16, math.sin(a) * 0.16) for a in (i * math.tau / 24 for i in range(24))]
    objs += [_flat_poly("hub", hub, 0.020, gold), _flat_poly("gem", [(x * 0.55, y * 0.55) for x, y in hub], 0.022, field)]
    return objs, {"center": Vector((0.0, 0.0, 0.0)), "north": Vector((0.0, hy, 0.0)), "south": Vector((0.0, -hy, 0.0)),
                  "west": Vector((-hx, 0.0, 0.0)), "east": Vector((hx, 0.0, 0.0))}


def _post(name, at, height, radius, wood, iron, r):
    x, y = at
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=radius, depth=height, location=(x, y, height / 2))
    post = bpy.context.active_object
    post.name = name
    post.rotation_euler.z = r.uniform(0, 1)
    post.data.materials.append(wood)
    mod = post.modifiers.new("bevel", "BEVEL")
    mod.width, mod.segments, mod.limit_method = 0.02, 2, "ANGLE"
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=radius * 1.05, location=(x, y, height))
    knob = bpy.context.active_object
    knob.scale.z = 0.7
    knob.data.materials.append(wood)
    bpy.ops.mesh.primitive_torus_add(major_radius=radius * 1.02, minor_radius=0.022, location=(x, y, height * 0.8))
    band = bpy.context.active_object
    band.data.materials.append(iron)
    for obj in (post, knob, band):
        for poly in obj.data.polygons:
            poly.use_smooth = True
    return [post, knob, band]


def _swag(name, a, b, sag, thickness, material):
    """Hanging rope between two 3D points: a sampled catenary-like curve with a round bevel."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth, curve.bevel_resolution = thickness, 3
    spline = curve.splines.new("POLY")
    pts = 16
    spline.points.add(pts - 1)
    for i in range(pts):
        t = i / (pts - 1)
        co = a.lerp(b, t)
        co.z -= sag * 4 * t * (1 - t)
        spline.points[i].co = (co.x, co.y, co.z, 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    # As a curve its bound box is padded by a tile on every side, which would bloat the camera frame.
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.convert(target="MESH")
    return bpy.context.view_layer.objects.active


def rope_fence(spec, facing):
    """Wooden posts linked by a sagging rope (ART-0024).

    params.posts: post feet in tiles relative to the anchor post (first = front_post_foot); one post
    renders a lone post (anchor foot). Rope runs between consecutive post tops."""
    p = spec.get("params", {})
    posts = [tuple(v) for v in p.get("posts", [[0.0, 0.0]])]
    height, radius = p.get("height", 0.82), p.get("radius", 0.17)
    r = lib.rng(p.get("seed", 6))
    wood = lib.wood("post_wood", seed=r.random() * 10)
    iron = lib.flat("iron", (0.10, 0.09, 0.08), roughness=0.5, metallic=0.8)
    hemp = lib.rope("rope")
    objs = []
    plinth = p.get("plinth", 0.0)
    stone = _golden(p, r, cap=True) if plinth else None
    for i, at in enumerate(posts):
        objs += _post("post", at, height + r.uniform(-0.04, 0.04), radius, wood, iron, r)
        if plinth:   # low limestone footing so the post seats on the terrace instead of floating
            objs.append(lib.block("plinth", (plinth, plinth, 0.08), (at[0], at[1], 0.04), stone, bevel=0.025))
    for (ax, ay), (bx, by) in zip(posts, posts[1:]):
        za = zb = height * 0.8
        objs.append(_swag("rope", Vector((ax, ay, za)), Vector((bx, by, zb)), p.get("sag", 0.22), p.get("rope", 0.028), hemp))
        # Rope wraps at both posts.
        for x, y in ((ax, ay), (bx, by)):
            bpy.ops.mesh.primitive_torus_add(major_radius=radius * 1.08, minor_radius=0.03, location=(x, y, za))
            wrap = bpy.context.active_object
            wrap.data.materials.append(hemp)
            objs.append(wrap)
    anchors = {"foot": Vector((posts[0][0], posts[0][1], 0.0)), "front_post_foot": Vector((posts[0][0], posts[0][1], 0.0))}
    if len(posts) > 1:
        anchors["back_post_foot"] = Vector((posts[-1][0], posts[-1][1], 0.0))
    return objs, anchors


BUILDERS = {"calibration_tile": calibration_tile, "wall_run": wall_run, "broken_floor_edge": broken_floor_edge,
            "side_wall_path": side_wall_path, "entrance_stairs": entrance_stairs, "compass_inlay": compass_inlay,
            "rope_fence": rope_fence}
