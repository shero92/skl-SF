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
    x = -length / 2
    while x < length / 2 - 0.02:
        w = r.uniform(0.45, 0.7)
        x0, x1 = x, min(x + w, length / 2)
        objs.append(lib.block("cap", (x1 - x0 - gap * 0.6, thick + 0.07, cap_h), ((x0 + x1) / 2, thick / 2, z + cap_h / 2),
                              cap_stone, bevel=0.03))
        x += w
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
    stone = lib.limestone("wall_stone", base=(0.70, 0.49, 0.25), dark=(0.38, 0.24, 0.10), seed=r.random() * 10)
    cap_stone = lib.limestone("cap_stone", base=(0.76, 0.57, 0.31), dark=(0.45, 0.30, 0.13), seed=r.random() * 10)
    mortar = lib.flat("mortar", (0.28, 0.20, 0.12), roughness=1.0)
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
    lib.lean(objs, p.get("lean", 0.0))
    joined = lib.join(objs, "side_wall")
    return [joined], {"grid_origin": Vector((0.0, 0.0, 0.0))}


BUILDERS = {"calibration_tile": calibration_tile, "wall_run": wall_run, "broken_floor_edge": broken_floor_edge,
            "side_wall_path": side_wall_path}
