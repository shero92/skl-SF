#!/usr/bin/env python3
"""Blender part factory for Map Factory environment pieces (owner decision 2026-10-26).

    py -3 tools/blender_factory.py calibrate               # 1x1 tile must render tile_px x tile_px
    py -3 tools/blender_factory.py render <spec> --out DIR  # raw Blender render (masters, shadows, metadata)
    py -3 tools/blender_factory.py deliver ART-0004         # render tools/blender/specs/ART-0004.json into
                                                            # .agents/graphics/deliveries/ART-0004/ + manifest
    py -3 tools/blender_factory.py stage <spec> --out DIR   # same outputs for candidate-only pieces (no ART id)

deliver writes native-scale PNGs at exactly the request's output_paths, 4x masters and separate shadows,
technical QA (tools/art_qa.py) and a manifest with measured SHA-256. It never changes the ART/TASK status,
never writes map_factory/parts and never approves art: visual review happens on the final Godot capture.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BLENDER_DIR = ROOT / "tools/blender"
SPECS = BLENDER_DIR / "specs"
CONFIG = ROOT / ".agents/planner/config.json"
DELIVERIES = ROOT / ".agents/graphics/deliveries"
REFERENCE = ROOT / ".agents/planner/goals/GOAL-0001/references/hero_room_reference.png"
DEFAULT_BLENDER = [r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe", "blender"]

sys.path.insert(0, str(ROOT / "tools"))


def blender_executable(override: str | None = None) -> str | None:
    """--blender, BLENDER_EXECUTABLE, config blender_executable, then known install paths."""
    candidates = [override, os.environ.get("BLENDER_EXECUTABLE")]
    if CONFIG.is_file():
        candidates.append(json.loads(CONFIG.read_text(encoding="utf-8")).get("blender_executable"))
    candidates += DEFAULT_BLENDER
    for c in candidates:
        if c and (Path(c).is_file() or shutil.which(c)):
            return c
    return None


def load_spec(path: Path) -> dict:
    spec = json.loads(Path(path).read_text(encoding="utf-8"))
    if "builder" not in spec or not isinstance(spec.get("outputs"), list) or not spec["outputs"]:
        raise ValueError("spec needs a builder and a non-empty outputs list")
    names = [o.get("name") for o in spec["outputs"]]
    if any(not isinstance(n, str) or not re.fullmatch(r"[a-z0-9_]+", n) for n in names) or len(set(names)) != len(names):
        raise ValueError("output names must be unique lowercase snake_case")
    for o in spec["outputs"]:
        if o.get("facing", "south") not in ("north", "east", "south", "west"):
            raise ValueError("unknown facing " + str(o.get("facing")))
    for entry in spec.get("expected_similar", []):
        pair = entry.get("pair") if isinstance(entry, dict) else None
        if not (isinstance(pair, list) and len(pair) == 2 and set(pair) <= set(names) and entry.get("reason")):
            raise ValueError("expected_similar entries need a pair of output names and a reason")
    return spec


def split_expected(qa: dict, spec: dict) -> tuple[list[str], list[dict]]:
    """Owner-accepted look-alike pairs (spec expected_similar) leave the warnings with their reason recorded."""
    expected = {frozenset(n + ".png" for n in e["pair"]): e["reason"] for e in spec.get("expected_similar", [])}
    warnings, accepted = [], []
    for text in qa["warnings"]:
        pair = frozenset(text.split(":")[0].split(" vs "))
        if pair in expected:
            accepted.append({"warning": text, "reason": expected[pair]})
        else:
            warnings.append(text)
    return warnings, accepted


def render(spec_path: Path, out_dir: Path, blender: str | None = None, timeout: int = 3600) -> list[dict]:
    exe = blender_executable(blender)
    if exe is None:
        raise RuntimeError("Blender not found: set blender_executable in .agents/planner/config.json or BLENDER_EXECUTABLE")
    load_spec(spec_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run([exe, "-b", "--factory-startup", "--python", str(BLENDER_DIR / "render_part.py"), "--",
                           str(spec_path), str(out_dir)], capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    if proc.returncode or "DONE" not in proc.stdout:
        tail = "\n".join((proc.stdout + proc.stderr).strip().splitlines()[-15:])
        raise RuntimeError("Blender render failed:\n" + tail)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    return [json.loads((out_dir / (o["name"] + ".json")).read_text(encoding="utf-8")) for o in spec["outputs"]]


def downscale(src: Path, dst: Path, factor: int) -> list[int]:
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    if factor > 1:
        # Pillow premultiplies RGBA while resampling, so transparent black pixels do not bleed into edges.
        im = im.resize((max(1, round(im.width / factor)), max(1, round(im.height / factor))), Image.Resampling.LANCZOS)
    im.save(dst)
    return list(im.size)


def palette(path: Path) -> dict:
    """Mean colour of the opaque pixels (alpha > 200): RGB, hue in degrees, HLS lightness and saturation.

    Scripted colour QA: agents never open piece images, so 'reads grey' is measured, not looked at."""
    import colorsys
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    px = [p for p in getattr(im, "get_flattened_data", im.getdata)() if p[3] > 200]  # getdata: Pillow < 12
    if not px:
        return {"opaque_px": 0}
    mean = [round(sum(p[i] for p in px) / len(px)) for i in range(3)]
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in mean))
    # Multi-colour pieces (blue + gold) can average to grey; the mean per-pixel saturation does not.
    pixel_sat = sum(colorsys.rgb_to_hls(*(v / 255 for v in p[:3]))[2] for p in px) / len(px)
    box = im.getchannel("A").point(lambda v: 255 if v > 24 else 0).getbbox()
    return {"opaque_px": len(px), "mean_rgb": mean, "hue_deg": round(h * 360), "lightness": round(l, 3),
            "saturation": round(s, 3), "pixel_saturation": round(pixel_sat, 3),
            "opaque_size": [box[2] - box[0], box[3] - box[1]] if box else None}


def palette_problems(name: str, stats: dict, check: dict | None) -> list[str]:
    """spec palette_check {min_saturation, min_pixel_saturation, hue_deg: [lo, hi]} turns a grey or off-hue
    piece into a QA problem."""
    if not check or not stats.get("opaque_px"):
        return []
    problems = []
    for key, label in (("saturation", "mean colour saturation"), ("pixel_saturation", "mean pixel saturation")):
        floor = check.get("min_" + key)
        if floor is not None and stats[key] < floor:
            problems.append(f"{name}: {label} {stats[key]} < {floor} (reads grey)")
    lo, hi = check.get("hue_deg", [0, 360])
    if not lo <= stats["hue_deg"] <= hi:
        problems.append(f"{name}: mean hue {stats['hue_deg']} outside {lo}-{hi} degrees")
    return problems


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def request_outputs(art_id: str) -> list[str]:
    req = next((ROOT / ".agents/graphics/requests").glob(art_id + "_*.md"))
    m = re.search(r"(?m)^output_paths: (.+)$", req.read_text(encoding="utf-8"))
    return [p.strip() for p in m.group(1).split(",")] if m else []


def git_head() -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    return proc.stdout.strip() or "unknown"


def blender_version(exe: str) -> str:
    proc = subprocess.run([exe, "-b", "--factory-startup", "--version"], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return (proc.stdout.strip().splitlines() or ["unknown"])[0]


def deliver(art_id: str, blender: str | None = None, agent: str = "claude") -> dict:
    spec_path = SPECS / (art_id + ".json")
    spec = load_spec(spec_path)
    expected = request_outputs(art_id)
    wanted = [f".agents/graphics/deliveries/{art_id}/{o['name']}.png" for o in spec["outputs"]]
    if sorted(wanted) != sorted(expected):
        raise ValueError(f"{art_id}: spec outputs {wanted} differ from request output_paths {expected}")
    return produce(spec_path, spec, DELIVERIES / art_id, art_id, blender, agent)


def stage(spec_path: Path, out_dir: Path, blender: str | None = None, agent: str = "claude") -> dict:
    """Render a candidate-only spec (pieces built for one map candidate, no ART request) into out_dir."""
    spec = load_spec(spec_path)
    return produce(spec_path, spec, out_dir, spec.get("candidate", spec_path.stem), blender, agent)


def produce(spec_path: Path, spec: dict, target: Path, request_id: str, blender: str | None, agent: str) -> dict:
    """Render, downscale to native, keep masters and shadows, run QA and write manifest.json into target."""
    import art_qa
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="blender-" + request_id + "-") as tmp:
        metas = render(spec_path, Path(tmp), blender)
        files, extra = [], []
        for meta in metas:
            name, ss = meta["name"], int(meta["supersample"])
            native = target / (name + ".png")
            size = downscale(Path(tmp) / meta["color"], native, ss)
            master = target / (name + "@" + str(ss) + "x.png")
            shutil.copyfile(Path(tmp) / meta["color"], master)
            item = {"path": native.relative_to(ROOT).as_posix(), "sha256": sha256(native), "pixel_size": size,
                    "facing": meta["facing"], "anchors_px": meta["anchors_px"], "builder": meta["builder"],
                    "params": meta["params"], "master": master.relative_to(ROOT).as_posix(), "master_sha256": sha256(master),
                    "palette": palette(native)}
            extra.append({"path": item["master"], "sha256": item["master_sha256"], "role": "4x master"})
            if meta.get("shadow"):
                shadow = target / (name + "_shadow.png")
                downscale(Path(tmp) / meta["shadow"], shadow, ss)
                item["shadow"] = shadow.relative_to(ROOT).as_posix()
                extra.append({"path": item["shadow"], "sha256": sha256(shadow), "role": "separate cast shadow"})
            files.append(item)
        qa = art_qa.check(target, [Path(f["path"]).name for f in files])
        for f in files:
            qa["problems"] += palette_problems(Path(f["path"]).name, f["palette"], spec.get("palette_check"))
    exe = blender_executable(blender) or "unknown"
    warnings, accepted = split_expected(qa, spec)
    manifest = {
        "request_id": request_id, "task_id": spec.get("task"), "status": "rendered_unreviewed",
        "files": files, "extra_files": extra, "qa": {"problems": qa["problems"], "warnings": warnings,
                                                     "expected_warnings": accepted, "pairs": qa["pairs"]},
        "provenance": {"tool": "blender", "blender": blender_version(exe), "spec": spec_path.resolve().relative_to(ROOT).as_posix(),
                       "toolkit_commit": git_head(), "producing_agent": agent, "ai_image_generation": False},
        "reference": {"path": REFERENCE.relative_to(ROOT).as_posix(),
                      "sha256": sha256(REFERENCE) if REFERENCE.is_file() else None, "owner_confirmed": False},
        "review": {"visual_approval": None, "note": "Checked only on the final Godot capture of the assembled room; "
                                                    "pieces are improved and re-rendered from the spec, never hand-edited."},
        "cost": "unknown",
    }
    (target / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return manifest


def calibrate(blender: str | None = None) -> dict:
    """A flat 1x1 tile must cover exactly tile_px x tile_px pixels (square floor grid)."""
    from PIL import Image
    proj = json.loads((BLENDER_DIR / "projection.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="blender-calibrate-") as tmp:
        spec = Path(tmp) / "spec.json"
        spec.write_text(json.dumps({"builder": "calibration_tile", "projection": {"supersample": 1, "samples": 8},
                                    "outputs": [{"name": "calib", "shadow": False}]}), encoding="utf-8", newline="\n")
        meta = render(spec, Path(tmp) / "out", blender)[0]
        alpha = Image.open(Path(tmp) / "out" / meta["color"]).getchannel("A")
        bbox = alpha.point(lambda v: 255 if v > 127 else 0).getbbox()
    size = [bbox[2] - bbox[0], bbox[3] - bbox[1]] if bbox else None
    return {"tile_px": proj["tile_px"], "measured": size, "ok": size == [proj["tile_px"]] * 2,
            "anchor": meta["anchors_px"]["tile_top_left"], "bbox": list(bbox) if bbox else None}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("calibrate")
    r = sub.add_parser("render")
    r.add_argument("spec", type=Path)
    r.add_argument("--out", type=Path, required=True)
    d = sub.add_parser("deliver")
    d.add_argument("art_id")
    d.add_argument("--agent", choices=("claude", "codex"), default="claude")
    st = sub.add_parser("stage")
    st.add_argument("spec", type=Path)
    st.add_argument("--out", type=Path, required=True)
    st.add_argument("--agent", choices=("claude", "codex"), default="claude")
    for p in sub.choices.values():
        p.add_argument("--blender")
    args = parser.parse_args(argv)
    try:
        if args.cmd == "calibrate":
            result = calibrate(args.blender)
            print(json.dumps(result))
            return 0 if result["ok"] else 1
        if args.cmd == "render":
            print(json.dumps(render(args.spec, args.out, args.blender), indent=2))
            return 0
        if args.cmd == "stage":
            manifest = stage(args.spec, args.out.resolve(), args.blender, args.agent)
        else:
            manifest = deliver(args.art_id, args.blender, args.agent)
        print(json.dumps({k: manifest[k] for k in ("request_id", "status")} | {"files": len(manifest["files"]),
              "problems": manifest["qa"]["problems"], "warnings": manifest["qa"]["warnings"]}, indent=2))
        return 1 if manifest["qa"]["problems"] else 0
    except (OSError, RuntimeError, ValueError) as exc:
        print("blender factory:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
