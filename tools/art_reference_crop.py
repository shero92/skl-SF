"""Cut the reference crop that every art request must carry, plus a target-vs-game comparison.

    python tools/art_reference_crop.py --id ART-0042 --box 150,130,620,330 \
        --target map_factory/references/hero_room_01_target_20261103.png \
        --game docs/previews/map_factory_renders/t0148_v0026/hero_room_01_v0026.png

Writes .agents/graphics/requests/reference_crops/<id>_target.png (the exact piece to draw, cut from the
owner's picture) and <id>_compare.png (left: target, right: the game today at the same place), and prints
their SHA-256. Cropping a reference is not art generation; nothing here is a game asset.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(".agents/graphics/requests/reference_crops")


def crop_reference(request_id: str, box: tuple[int, int, int, int], target: Path, game: Path | None,
                   root: Path = ROOT, suffix: str = "") -> dict[str, str]:
    """Returns {relative path: sha256} of the files written (target crop first, then the comparison)."""
    out_dir = root / OUT
    out_dir.mkdir(parents=True, exist_ok=True)
    source = Image.open(root / target).convert("RGB")
    piece = source.crop(box)
    written = [out_dir / f"{request_id}{suffix}_target.png"]
    piece.save(written[0])
    if game is not None:
        now = Image.open(root / game).convert("RGB")
        if now.size != source.size:
            raise ValueError("target and game capture must have the same pixel size")
        sheet = Image.new("RGB", (piece.width * 2 + 8, piece.height), (255, 0, 255))
        sheet.paste(piece, (0, 0))
        sheet.paste(now.crop(box), (piece.width + 8, 0))
        written.append(out_dir / f"{request_id}{suffix}_compare.png")
        sheet.save(written[1])
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in written}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True)
    ap.add_argument("--box", required=True, help="left,top,right,bottom in target pixels")
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument("--game", type=Path)
    ap.add_argument("--suffix", default="")
    args = ap.parse_args()
    box = tuple(int(v) for v in args.box.split(","))
    if len(box) != 4 or box[0] >= box[2] or box[1] >= box[3]:
        raise SystemExit("--box needs left,top,right,bottom")
    for path, digest in crop_reference(args.id, box, args.target, args.game, suffix=args.suffix).items():
        print(digest, path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
