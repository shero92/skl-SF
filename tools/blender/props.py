"""Hero Room props as grid-aligned map pieces (TASK-0067; run inside Blender).

Each builder models one prop standing on a w x d cell footprint whose front-left corner is the
origin (x 0..w east, y 0..d north, front facing south toward the camera) and returns
(objects, anchors). Specs give the footprint as "grid": [w, d]; render_part frames whole 64 px
cells with the footprint in the bottom rows. Registered into builders.BUILDERS.
"""
import math

import bmesh
import bpy
from mathutils import Vector

import builders as B
import lib

FOOT = {"footprint_front_left": Vector((0.0, 0.0, 0.0))}


# ---------------------------------------------------------------- materials

def _banded(name, a, b, scale=5.0):
    """Blue-and-white porcelain: hard horizontal bands with a soft wave."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = 0.3
    coord = lib._node(nt, "ShaderNodeTexCoord", (-700, 0))
    wave = lib._node(nt, "ShaderNodeTexWave", (-500, 0), Scale=scale, Distortion=2.0)
    wave.bands_direction = "Z"
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    ramp = lib._node(nt, "ShaderNodeValToRGB", (-300, 0))
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[0].color = 0.0, (*a, 1.0)
    ramp.color_ramp.elements[1].position, ramp.color_ramp.elements[1].color = 0.55, (*b, 1.0)
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def _glow(name, color, strength=6.0):
    mat = lib.flat(name, color, roughness=0.4)
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    bsdf.inputs["Emission Strength"].default_value = strength
    return mat


def _stone(name="stone"):
    return lib.limestone(name, base=lib.GOLDEN_STONE[0], dark=lib.GOLDEN_STONE[1], specular=0.2)


LINEN = (0.86, 0.82, 0.72)
CLOTH_BLUE = (0.025, 0.09, 0.38)
IRON = (0.05, 0.045, 0.04)


# ---------------------------------------------------------------- geometry helpers

def _active(name, mat, smooth=True):
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(mat)
    if smooth:
        for poly in o.data.polygons:
            poly.use_smooth = True
    return o


def _cyl(name, r, h, at, mat, verts=20, z=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=(at[0], at[1], z + h / 2))
    return _active(name, mat)


def _sphere(name, r, at, mat, scale=(1.0, 1.0, 1.0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=r, location=at)
    o = _active(name, mat)
    o.scale = scale
    return o


def _torus(name, major, minor, at, mat, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=32, minor_segments=8,
                                     location=at, rotation=rot)
    return _active(name, mat)


def _lathe(name, profile, at, mat, segs=24):
    """Surface of revolution from (z, radius) pairs, bottom first, closed at the bottom."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    rings = [[bm.verts.new((at[0] + r * math.cos(2 * math.pi * k / segs), at[1] + r * math.sin(2 * math.pi * k / segs),
                            (at[2] if len(at) > 2 else 0.0) + z)) for k in range(segs)] for z, r in profile]
    for lo, hi in zip(rings, rings[1:]):
        for k in range(segs):
            bm.faces.new([lo[k], lo[(k + 1) % segs], hi[(k + 1) % segs], hi[k]])
    bm.faces.new(list(reversed(rings[0])))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(mesh)
    bm.free()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat)
    for poly in o.data.polygons:
        poly.use_smooth = True
    return o


def _upright(name, outline, y0, y1, mat, at=(0.0, 0.0, 0.0)):
    """Prism standing in the x/z plane: outline (x, z) extruded from y0 to y1 (banners, voussoirs)."""
    o = B._prism(name, outline, -y0, -y1, mat)
    o.rotation_euler.x = math.pi / 2
    o.location = at
    return o


def _star(hx, hy):
    """Eight-point compass star outline (x, y) around the origin."""
    pts = []
    for k in range(16):
        a = math.pi / 2 - k * math.pi / 8
        rad = (1.0 if k % 4 == 0 else 0.55 if k % 2 == 0 else 0.22)
        pts.append((math.cos(a) * hx * rad, math.sin(a) * hy * rad))
    return list(reversed(pts))


# ---------------------------------------------------------------- props

def bed(spec, facing):
    """Wooden bed, head against the north wall, blue blanket with a gold compass (grid 2x3)."""
    p = spec.get("params", {})
    wood = lib.wood("bed_wood", seed=p.get("seed", 1))
    linen, blue, gold = lib.flat("linen", LINEN, 0.8), lib.flat("blanket", CLOTH_BLUE, 0.85), lib.gold()
    o = []
    for x, y, h in ((0.1, 0.12, 0.72), (1.9, 0.12, 0.72), (0.1, 2.86, 1.3), (1.9, 2.86, 1.3)):
        o.append(lib.block("post", (0.13, 0.13, h), (x, y, h / 2), wood, bevel=0.02))
        o.append(_sphere("knob", 0.07, (x, y, h + 0.04), gold))
    for x in (0.1, 1.9):
        o.append(lib.block("rail", (0.08, 2.7, 0.2), (x, 1.49, 0.32), wood, bevel=0.015))
    o.append(lib.block("footboard", (1.7, 0.07, 0.36), (1.0, 0.12, 0.42), wood, bevel=0.015))
    o.append(lib.block("headboard", (1.7, 0.08, 0.78), (1.0, 2.86, 0.8), wood, bevel=0.02))
    o.append(lib.block("head_trim", (1.72, 0.1, 0.04), (1.0, 2.86, 1.2), gold, bevel=0.01))
    o.append(lib.block("mattress", (1.7, 2.62, 0.24), (1.0, 1.5, 0.52), linen, bevel=0.06))
    o.append(lib.block("blanket", (1.84, 1.86, 0.07), (1.0, 1.03, 0.67), blue, bevel=0.03))
    for x in (0.08, 1.92):
        o.append(lib.block("drape", (0.035, 1.86, 0.3), (x, 1.03, 0.52), blue, bevel=0.012))
    o.append(lib.block("drape_front", (1.84, 0.035, 0.3), (1.0, 0.1, 0.52), blue, bevel=0.012))
    o.append(lib.block("fold", (1.84, 0.2, 0.09), (1.0, 2.02, 0.67), linen, bevel=0.035))
    for y in (0.24, 1.84):
        o.append(lib.block("border", (1.6, 0.025, 0.012), (1.0, y, 0.71), gold, bevel=0.0))
    for x in (0.24, 1.76):
        o.append(lib.block("border", (0.025, 1.62, 0.012), (x, 1.04, 0.71), gold, bevel=0.0))
    star = B._flat_poly("compass", _star(0.5, 0.5), 0.72, gold)
    star.location = (1.0, 1.04, 0.0)
    o.append(star)
    o.append(_torus("compass_ring", 0.3, 0.012, (1.0, 1.04, 0.715), gold))
    for x in (0.56, 1.44):
        o.append(lib.block("pillow", (0.72, 0.36, 0.17), (x, 2.56, 0.73), linen, bevel=0.075))
    o.append(lib.block("cushion", (0.42, 0.24, 0.15), (1.0, 2.33, 0.75), blue, bevel=0.06))
    return o, dict(FOOT)


def _stool(at, wood):
    o = [lib.block("seat", (0.4, 0.4, 0.07), (at[0], at[1], 0.42), wood, bevel=0.02)]
    for dx in (-0.15, 0.15):
        for dy in (-0.15, 0.15):
            o.append(lib.block("leg", (0.06, 0.06, 0.4), (at[0] + dx, at[1] + dy, 0.2), wood, bevel=0.01))
    return o


def study_table(spec, facing):
    """Study table with a blue runner, jug, fruit bowl and chart; two stools in front (grid 2x2)."""
    p = spec.get("params", {})
    r = lib.rng(p.get("seed", 2))
    wood = lib.wood("table_wood", seed=p.get("seed", 2))
    blue, linen = lib.flat("runner", CLOTH_BLUE, 0.85), lib.flat("jug", LINEN, 0.35)
    o = [lib.block("top", (1.84, 1.0, 0.08), (1.0, 1.2, 0.74), wood, bevel=0.02)]
    for x in (0.18, 1.82):
        for y in (0.8, 1.6):
            o.append(lib.block("leg", (0.09, 0.09, 0.7), (x, y, 0.35), wood, bevel=0.015))
    o.append(lib.block("runner", (0.5, 1.06, 0.012), (1.0, 1.2, 0.785), blue, bevel=0.0))
    for y in (0.67, 1.73):
        o.append(lib.block("runner_end", (0.5, 0.012, 0.2), (1.0, y, 0.69), blue, bevel=0.0))
    o.append(_lathe("jug", [(0, 0.07), (0.06, 0.1), (0.16, 0.09), (0.24, 0.05), (0.28, 0.06)], (0.45, 1.4, 0.78), linen))
    o.append(_lathe("bowl", [(0, 0.05), (0.03, 0.12), (0.08, 0.16)], (1.0, 1.3, 0.79), wood))
    for i, col in enumerate(((0.5, 0.04, 0.02), (0.2, 0.4, 0.05), (0.7, 0.3, 0.02), (0.55, 0.06, 0.03))):
        a = i * 1.6
        o.append(_sphere("fruit", 0.055, (1.0 + math.cos(a) * 0.06, 1.3 + math.sin(a) * 0.06, 0.88 + (i == 3) * 0.05),
                         lib.flat("fruit_%d" % i, col, 0.4)))
    chart = lib.block("chart", (0.5, 0.36, 0.01), (1.45, 1.05, 0.79), lib.flat("parchment", (0.72, 0.56, 0.32), 0.9), bevel=0.0)
    chart.rotation_euler.z = r.uniform(-0.25, -0.1)
    o.append(chart)
    for x in (0.55, 1.45):
        o += _stool((x, 0.32), wood)
    return o, dict(FOOT)


def bookshelf(spec, facing):
    """Open wooden bookshelf against the north wall, filled with books (grid 2x1)."""
    p = spec.get("params", {})
    r = lib.rng(p.get("seed", 3))
    wood = lib.wood("shelf_wood", seed=p.get("seed", 3))
    covers = [lib.flat("book_%d" % i, c, 0.6) for i, c in enumerate(
        ((0.03, 0.09, 0.36), (0.38, 0.05, 0.03), (0.33, 0.18, 0.06), (0.07, 0.18, 0.07), (0.6, 0.42, 0.18)))]
    y0, depth, height = 0.5, 0.45, p.get("height", 1.5)
    yc = y0 + depth / 2
    o = []
    for x in (0.05, 1.95):
        o.append(lib.block("side", (0.07, depth, height), (x, yc, height / 2), wood, bevel=0.012))
    o.append(lib.block("back", (1.86, 0.03, height), (1.0, y0 + depth - 0.015, height / 2), wood, bevel=0.0))
    o.append(lib.block("crown", (2.04, depth + 0.05, 0.07), (1.0, yc, height + 0.035), wood, bevel=0.015))
    levels = [0.04, 0.52, 1.0]
    for z in levels + [height - 0.04]:
        o.append(lib.block("board", (1.86, depth - 0.02, 0.045), (1.0, yc, z), wood, bevel=0.008))
    for z in levels:
        x = 0.1
        while x < 1.85:
            w = r.uniform(0.05, 0.1)
            if r.random() < 0.08:
                x += w * 2
                continue
            h = r.uniform(0.28, 0.4)
            b = lib.block("book", (w - 0.006, 0.3, h), (x + w / 2, yc - 0.03, z + 0.023 + h / 2), covers[r.randrange(5)], bevel=0.008)
            if r.random() < 0.1:
                b.rotation_euler.y = r.uniform(0.15, 0.3)
            o.append(b)
            x += w
    vase = _lathe("top_vase", [(0, 0.06), (0.08, 0.11), (0.16, 0.08), (0.2, 0.05), (0.23, 0.06)], (1.6, yc, height + 0.07),
                  _banded("shelf_vase", CLOTH_BLUE, (0.85, 0.85, 0.82)))
    o.append(vase)
    return o, dict(FOOT)


def chest(spec, facing):
    """Wooden chest with gold bands and lock (grid 1x1)."""
    p = spec.get("params", {})
    wood, gold = lib.wood("chest_wood", seed=p.get("seed", 4)), lib.gold()
    lid = lib.wood("chest_lid", light=(0.3, 0.15, 0.05), seed=p.get("seed", 4) + 1)
    o = [lib.block("body", (0.8, 0.55, 0.4), (0.5, 0.45, 0.2), wood, bevel=0.02),
         lib.block("lid", (0.84, 0.59, 0.15), (0.5, 0.45, 0.475), lid, bevel=0.05)]
    for x in (0.24, 0.76):
        o.append(lib.block("band", (0.05, 0.6, 0.57), (x, 0.45, 0.28), gold, bevel=0.008))
    o.append(lib.block("lock", (0.1, 0.03, 0.13), (0.5, 0.165, 0.38), gold, bevel=0.01))
    return o, dict(FOOT)


def vase(spec, facing):
    """Blue-and-white porcelain vase (grid 1x1)."""
    prof = [(0, 0.1), (0.04, 0.15), (0.18, 0.2), (0.32, 0.18), (0.42, 0.11), (0.5, 0.08), (0.55, 0.1)]
    return [_lathe("vase", prof, (0.5, 0.5, 0.0), _banded("porcelain", CLOTH_BLUE, (0.86, 0.86, 0.84)))], dict(FOOT)


def planter(spec, facing):
    """Blue-and-white planter with a fan palm and white flowers (grid 1x1)."""
    p = spec.get("params", {})
    r = lib.rng(p.get("seed", 6))
    pot = [(0, 0.15), (0.08, 0.24), (0.28, 0.28), (0.4, 0.23), (0.45, 0.26)]
    o = [_lathe("pot", pot, (0.5, 0.5, 0.0), _banded("planter", CLOTH_BLUE, (0.86, 0.86, 0.84), scale=4.0)),
         _cyl("soil", 0.24, 0.02, (0.5, 0.5), lib.flat("soil", (0.08, 0.04, 0.02), 1.0), z=0.41)]
    greens = [lib.flat("frond_a", (0.08, 0.25, 0.05), 0.55), lib.flat("frond_b", (0.04, 0.14, 0.03), 0.6),
              lib.flat("frond_c", (0.2, 0.38, 0.07), 0.5)]
    leaves = []
    for k in range(p.get("fronds", 11)):
        a = k * 2 * math.pi / p.get("fronds", 11) + r.uniform(-0.2, 0.2)
        leaves.append((0.5, 0.5, 0.44, a, r.uniform(0.38, 0.5), r.uniform(0.07, 0.1), r.uniform(0.15, 0.4), k % 3))
    for k in range(5):
        a = r.uniform(0, 6.3)
        leaves.append((0.5, 0.5, 0.46, a, 0.3, 0.06, 0.45, 2))
    o.append(B._leaf_mesh("palm", leaves, greens))
    spots = [(0.5 + math.cos(a) * 0.2, 0.5 + math.sin(a) * 0.2, 0.62, 0.035) for a in (0.4, 2.3, 4.2)]
    o.append(B._flowers("flowers", spots, lib.flat("petal", (0.92, 0.9, 0.82), 0.45), lib.flat("heart", (0.85, 0.55, 0.08), 0.5)))
    return o, dict(FOOT)


def globe(spec, facing):
    """Brass globe on a wooden stand (grid 1x1)."""
    wood, gold = lib.wood("globe_wood", seed=7), lib.gold()
    earth = lib.periodic_material("earth", [(0.45, (0.02, 0.12, 0.42)), (0.52, (0.62, 0.45, 0.2))], scale=3.0, bump=0.0, roughness=0.35)
    o = [_lathe("base", [(0, 0.2), (0.05, 0.19), (0.08, 0.08), (0.36, 0.05), (0.42, 0.08)], (0.5, 0.5, 0.0), wood),
         _sphere("globe", 0.22, (0.5, 0.5, 0.68), earth),
         _torus("meridian", 0.26, 0.016, (0.5, 0.5, 0.68), gold, rot=(math.pi / 2, 0.0, 0.4)),
         _torus("horizon", 0.27, 0.014, (0.5, 0.5, 0.66), gold)]
    return o, dict(FOOT)


def rug(spec, facing):
    """Blue rug with gold borders, corner diamonds and a compass medallion (grid 3x2)."""
    blue, gold, ivory = lib.flat("rug", CLOTH_BLUE, 0.9), lib.gold(), lib.flat("fringe", LINEN, 0.9)
    o = [lib.block("rug", (2.7, 1.8, 0.02), (1.5, 1.0, 0.01), blue, bevel=0.005)]
    for inset in (0.1, 0.2):
        w, d = 2.7 - 2 * inset, 1.8 - 2 * inset
        for y in (1.0 - d / 2, 1.0 + d / 2):
            o.append(lib.block("border", (w, 0.035, 0.008), (1.5, y, 0.024), gold, bevel=0.0))
        for x in (1.5 - w / 2, 1.5 + w / 2):
            o.append(lib.block("border", (0.035, d, 0.008), (x, 1.0, 0.024), gold, bevel=0.0))
    for x in (0.45, 2.55):
        for y in (0.45, 1.55):
            d = B._flat_poly("corner", B._rhombus(0.09, 0.09), 0.03, gold)
            d.location = (x, y, 0.0)
            o.append(d)
    med = B._flat_poly("medallion", B._rhombus(0.55, 0.45), 0.028, gold)
    med.location = (1.5, 1.0, 0.0)
    inner = B._flat_poly("medallion_field", B._rhombus(0.48, 0.38), 0.032, blue)
    inner.location = (1.5, 1.0, 0.0)
    star = B._flat_poly("medallion_star", _star(0.36, 0.3), 0.036, gold)
    star.location = (1.5, 1.0, 0.0)
    o += [med, inner, star]
    for x in (0.12, 2.88):
        for k in range(14):
            o.append(lib.block("tassel", (0.06, 0.025, 0.01), (x + (0.03 if x > 1 else -0.03), 0.18 + k * 0.118, 0.012), ivory, bevel=0.0))
    return o, dict(FOOT)


def banner(spec, facing):
    """Blue banner with gold border and compass, hanging on the north wall of its cell (grid 1x1)."""
    blue, gold = lib.flat("banner", CLOTH_BLUE, 0.85), lib.gold()
    y, top, bottom = 0.9, 1.75, 0.55
    cloth = [(-0.27, top), (0.27, top), (0.27, bottom + 0.12), (0.0, bottom), (-0.27, bottom + 0.12)]
    rim = [(-0.3, top + 0.02), (0.3, top + 0.02), (0.3, bottom + 0.1), (0.0, bottom - 0.04), (-0.3, bottom + 0.1)]
    o = [_upright("rim", rim, y + 0.01, y + 0.025, gold, at=(0.5, 0.0, 0.0)),
         _upright("cloth", cloth, y - 0.01, y + 0.01, blue, at=(0.5, 0.0, 0.0)),
         _upright("star", [(sx, sz + 1.2) for sx, sz in _star(0.17, 0.17)], y - 0.02, y - 0.01, gold, at=(0.5, 0.0, 0.0))]
    rod = _cyl("rod", 0.025, 0.72, (0.5, y - 0.02), gold, verts=12, z=0.0)
    rod.rotation_euler.y = math.pi / 2
    rod.location = (0.5, y - 0.02, top + 0.04)
    o.append(rod)
    o.append(_torus("ring", 0.12, 0.01, (0.5, y - 0.02, 1.2), gold, rot=(math.pi / 2, 0.0, 0.0)))
    return o, dict(FOOT)


def lantern(spec, facing):
    """Wall lantern with a warm glowing glass on an iron bracket, on the north wall (grid 1x1)."""
    iron, gold = lib.flat("iron", IRON, 0.5, metallic=0.6), lib.gold()
    glass = _glow("glass", (1.0, 0.62, 0.22), 8.0)
    y, z = 0.78, 1.15
    o = [lib.block("plate", (0.12, 0.03, 0.22), (0.5, 0.96, z + 0.25), iron, bevel=0.01),
         lib.block("arm", (0.04, 0.2, 0.04), (0.5, 0.86, z + 0.3), iron, bevel=0.005),
         lib.block("glass", (0.16, 0.16, 0.22), (0.5, y, z), glass, bevel=0.01),
         lib.block("floor", (0.22, 0.22, 0.03), (0.5, y, z - 0.12), gold, bevel=0.008)]
    for dx in (-0.09, 0.09):
        for dy in (-0.09, 0.09):
            o.append(lib.block("bar", (0.025, 0.025, 0.24), (0.5 + dx, y + dy, z), iron, bevel=0.004))
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.17, depth=0.12, location=(0.5, y, z + 0.17), rotation=(0, 0, math.pi / 4))
    o.append(_active("roof", gold, smooth=False))
    o.append(_sphere("finial", 0.03, (0.5, y, z + 0.25), gold))
    return o, dict(FOOT)


def _column(at, height, stone, r_):
    x, y = at
    return [lib.block("plinth", (0.6, 0.6, 0.22), (x, y, 0.11), stone, bevel=0.03),
            _cyl("torus_base", 0.27, 0.08, at, stone, verts=24, z=0.22),
            _cyl("shaft", 0.22, height - 0.48, at, stone, verts=24, z=0.3),
            _cyl("necking", 0.26, 0.06, at, stone, verts=24, z=height - 0.18),
            lib.block("abacus", (0.62, 0.62, 0.14), (x, y, height - 0.06), stone, bevel=0.03)]


def column(spec, facing):
    """Free-standing limestone column with ivy (grid 1x1); params.height in tiles."""
    p = spec.get("params", {})
    r = lib.rng(p.get("seed", 9))
    h = p.get("height", 2.6)
    o = _column((0.5, 0.5), h, _stone("column_stone"), r)
    if p.get("ivy", True):
        o += lib.ivy("col_ivy", (0.3, 0.7), 0.27, h, r, density=1.6, hang=p.get("ivy_hang", 1.2), flowers=0.2)
    return o, dict(FOOT)


def arch(spec, facing):
    """Ruined limestone arch on two columns with ivy, the room's north opening (grid 3x1)."""
    p = spec.get("params", {})
    r = lib.rng(p.get("seed", 10))
    stone = _stone("arch_stone")
    ch, y0, y1 = p.get("column_height", 2.4), 0.25, 0.75
    o = _column((0.5, 0.5), ch, stone, r) + _column((2.5, 0.5), ch, stone, r)
    cx, rin, rout, n = 1.5, 0.78, 1.18, 9
    for k in range(n):
        a0, a1 = math.pi * k / n + 0.008, math.pi * (k + 1) / n - 0.008
        pts = [(cx + math.cos(a) * rad, ch + math.sin(a) * rad) for a, rad in ((a0, rin), (a1, rin), (a1, rout), (a0, rout))]
        o.append(_upright("voussoir", list(reversed(pts)), y0, y1, stone))
    top = ch + rout + 0.12
    for x in (0.4, 2.6):
        # Haunches over the columns stop short of the opening (inner radius) so the arch ring reads.
        o.append(lib.block("haunch", (0.5, 0.5, top - ch - 0.02), (x, 0.5, (ch + top) / 2), stone, bevel=0.03))
    x = 0.17
    while x < 2.83:
        w = min(r.uniform(0.4, 0.62), 2.83 - x)
        o.append(lib.block("cap", (w - 0.02, 0.56, 0.24), (x + w / 2, 0.5, top + 0.12), stone, bevel=0.035))
        x += w
    if p.get("ivy", True):
        o += lib.ivy("arch_ivy", (0.2, 2.8), y0 - 0.03, top + 0.24, r, density=p.get("ivy_density", 1.3),
                     hang=p.get("ivy_hang", 1.4), flowers=0.2)
    return o, dict(FOOT)


BUILDERS = {"bed": bed, "study_table": study_table, "bookshelf": bookshelf, "chest": chest, "vase": vase,
            "planter": planter, "globe": globe, "rug": rug, "banner": banner, "lantern": lantern,
            "column": column, "arch": arch}
