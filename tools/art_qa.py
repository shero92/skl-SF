"""Technical PNG QA for an ART delivery (never an artistic verdict).

    py -3 tools/art_qa.py <delivery_dir> <file>...

Checks RGBA transparency, backing/halo, canvas clipping and whether files are mirrored or
rotated copies of each other (forbidden for distinct facings).
"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageOps


def _pixels(im):
    flat = getattr(im, "get_flattened_data", None)
    return list(flat() if flat else im.getdata())


def _seam(px, w, h, axis):
    """Mean RGB step across the wrap edge divided by the mean step between neighbouring
    columns (axis x) or rows (axis y): about 1 for a seamless tile, much more for a visible seam."""
    def diff(a, b):
        return sum(abs(px[a][c] - px[b][c]) for c in range(3))
    if axis == "x":
        edge = sum(diff(y * w, y * w + w - 1) for y in range(h)) / h
        inner = sum(diff(y * w + x, y * w + x + 1) for y in range(h) for x in range(w - 1)) / (h * (w - 1))
    else:
        edge = sum(diff(x, (h - 1) * w + x) for x in range(w)) / w
        inner = sum(diff(y * w + x, (y + 1) * w + x) for y in range(h - 1) for x in range(w)) / ((h - 1) * w)
    return round(edge / max(inner, 1e-6), 2)


def stats(path, tile=False, grid=False):
    im = Image.open(path)
    info = {"path": Path(path).as_posix(), "mode": im.mode, "pixel_size": list(im.size),
            "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(), "problems": []}
    if im.mode != "RGBA":
        info["problems"].append("not RGBA (" + im.mode + ")")
        im = im.convert("RGBA")
    a = im.getchannel("A")
    w, h = im.size
    hist = a.histogram()
    total = w * h
    transparent, opaque = hist[0] / total, hist[255] / total
    partial = 1 - transparent - opaque
    info.update(transparent_fraction=round(transparent, 4), opaque_fraction=round(opaque, 4),
                partial_alpha_fraction=round(partial, 4))
    bbox = a.point(lambda v: 255 if v > 16 else 0).getbbox()
    info["content_bbox"] = list(bbox) if bbox else None
    if tile:
        # Map tiles fill the whole cell: opaque everywhere, measured for seams instead of edges.
        if opaque < 1.0:
            info["problems"].append("tile not fully opaque")
        px = _pixels(im.convert("RGB"))
        info["seam_x"], info["seam_y"] = _seam(px, w, h, "x"), _seam(px, w, h, "y")
        return info, im
    corners = [a.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    if grid:
        # Grid-aligned props fill their cells: corners and edges may be covered by the footprint.
        corners = []
    if corners and max(int(c) for c in corners) > 16:
        info["problems"].append("corners not transparent (backing or full-frame image)")
    if transparent < 0.05:
        info["problems"].append("almost no transparency")
    alpha = _pixels(a)
    edge = alpha[:w] + alpha[-w:] + alpha[::w] + alpha[w - 1::w]
    if not grid and sum(v > 200 for v in edge) / len(edge) > 0.25:
        info["problems"].append("content touches/clips the canvas edge")
    if partial > 0.15:
        info["problems"].append("large semi-transparent area (possible halo/fringe)")
    # A halo is a soft edge pixel whose brightness contrasts strongly with the opaque pixels it borders;
    # dark edges next to dark (shaded) geometry are not a halo.
    rgb = _pixels(im.convert("RGB"))
    luma = [(r * 299 + g * 587 + b * 114) // 1000 for r, g, b in rgb]
    soft = halo = 0
    for y in range(1, h - 1):
        row = y * w
        for x in range(1, w - 1):
            i = row + x
            if not 32 <= alpha[i] < 200:
                continue
            near = [luma[j] for j in (i - w - 1, i - w, i - w + 1, i - 1, i + 1, i + w - 1, i + w, i + w + 1) if alpha[j] >= 250]
            if near:
                soft += 1
                halo += abs(luma[i] - sum(near) / len(near)) > 120
    info["soft_edge_pixels"], info["halo_fraction"] = soft, round(halo / soft, 3) if soft else 0.0
    if soft and halo / soft > 0.15:
        info["problems"].append("halo: soft edge pixels contrast with the opaque pixels they border")
    return info, im


def similarity(a, b):
    """Mean absolute RGBA difference (0-255) after resizing both to 128x128; 0 means identical."""
    size = (128, 128)
    diff = ImageChops.difference(a.convert("RGBA").resize(size), b.convert("RGBA").resize(size)).convert("L")
    return round(sum(_pixels(diff)) / (size[0] * size[1]), 2)


def check(folder, names, tiles=(), grid=()):
    """QA report for files in folder: per-file stats, pairwise comparison, problems and warnings."""
    report, images = {"files": [], "problems": [], "warnings": []}, {}
    for name in names:
        path = Path(folder) / name
        if not path.is_file():
            report["files"].append({"path": path.as_posix(), "problems": ["missing"]})
            continue
        info, im = stats(path, tile=name in tiles, grid=name in grid)
        report["files"].append(info)
        images[name] = im
    keys = list(images)
    report["pairs"] = []
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            A, B = images[a], images[b]
            pair = {"a": a, "b": b, "same": similarity(A, B), "mirror": similarity(ImageOps.mirror(A), B),
                    "rot90": min(similarity(A.rotate(r, expand=True), B) for r in (90, 180, 270))}
            report["pairs"].append(pair)
            if min(pair["mirror"], pair["rot90"]) < 6 <= pair["same"]:
                report["problems"].append(f"{a} vs {b}: mirrored/rotated copy (mirror {pair['mirror']}, rot {pair['rot90']})")
            elif pair["same"] < 6:
                report["warnings"].append(f"{a} vs {b}: nearly identical (score {pair['same']}); "
                                          "fine for variants, a defect if they must be distinct facings")
    report["problems"] += [f"{f['path']}: {p}" for f in report["files"] for p in f["problems"]]
    return report


if __name__ == "__main__":
    print(json.dumps(check(sys.argv[1], sys.argv[2:]), indent=2))
