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


def stats(path):
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
    corners = [a.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    if max(int(c) for c in corners) > 16:
        info["problems"].append("corners not transparent (backing or full-frame image)")
    if transparent < 0.05:
        info["problems"].append("almost no transparency")
    alpha = _pixels(a)
    edge = alpha[:w] + alpha[-w:] + alpha[::w] + alpha[w - 1::w]
    if sum(v > 200 for v in edge) / len(edge) > 0.25:
        info["problems"].append("content touches/clips the canvas edge")
    if partial > 0.15:
        info["problems"].append("large semi-transparent area (possible halo/fringe)")
    soft = [p for p, v in zip(_pixels(im.convert("RGB")), alpha) if 0 < v < 200]
    if soft:
        light = sum(min(p) > 235 for p in soft) / len(soft)
        dark = sum(max(p) < 20 for p in soft) / len(soft)
        info["fringe_white_fraction"], info["fringe_black_fraction"] = round(light, 3), round(dark, 3)
        if light > 0.3 or dark > 0.3:
            info["problems"].append("white/black halo on soft edges")
    return info, im


def similarity(a, b):
    """Mean absolute RGBA difference (0-255) after resizing both to 128x128; 0 means identical."""
    size = (128, 128)
    diff = ImageChops.difference(a.convert("RGBA").resize(size), b.convert("RGBA").resize(size)).convert("L")
    return round(sum(_pixels(diff)) / (size[0] * size[1]), 2)


def check(folder, names):
    """QA report for files in folder: per-file stats, pairwise comparison, problems and warnings."""
    report, images = {"files": [], "problems": [], "warnings": []}, {}
    for name in names:
        path = Path(folder) / name
        if not path.is_file():
            report["files"].append({"path": path.as_posix(), "problems": ["missing"]})
            continue
        info, im = stats(path)
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
