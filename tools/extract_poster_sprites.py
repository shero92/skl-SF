"""Cut the map-sprite grid out of an approved character design poster.

Usage: python tools/extract_poster_sprites.py --slug cely [--check]

The design posters (assets/characters/<slug>/references or map_factory/references/characters)
contain a 4 direction x 3 frame map sprite grid drawn on parchment. This tool crops each sprite,
turns the parchment into transparency (colour distance from the panel background, connected component
mask, no repainting of pixels) and writes:
  assets/characters/<slug>/map/<dir>/<slug>_map_<dir>_NN.png   (NN = 01..03, canvas 144x144)
  assets/characters/<slug>/map/<slug>_map_<dir>.png             (3-frame horizontal sheet)
The sprite pixels are copied as they are; only the background is made transparent and the frame is
placed bottom-centred on a common canvas. Visual review of the result is still required.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CANVAS = 144
DIRECTIONS = ("down", "left", "right", "up")
# Map-sprite panel box (left, top, right, bottom) on each poster, measured on the supplied files.
PANELS = {
    "cely": (710, 100, 1062, 578),
    "neru": (735, 105, 1052, 590),
    "old_father": (765, 90, 1095, 595),
    "reef_friend": (750, 100, 1095, 572),
    "temple_archer": (760, 95, 1100, 585),
}
POSTER_SOURCES = ("assets/characters/{slug}/references/{slug}_design_reference.png",
                  "map_factory/references/characters/{slug}.png.png")


def find_poster(slug: str) -> Path:
    for pattern in POSTER_SOURCES:
        path = ROOT / pattern.format(slug=slug)
        if path.is_file():
            return path
    raise FileNotFoundError(f"no poster for {slug}")


def components(mask: np.ndarray) -> list[tuple[int, int, int, int, np.ndarray]]:
    """4-connected components of a boolean mask: (x0, y0, x1, y1, local mask)."""
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    found = []
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or seen[y, x]:
                continue
            queue = deque([(y, x)])
            seen[y, x] = True
            points = []
            while queue:
                cy, cx = queue.popleft()
                points.append((cy, cx))
                for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1),
                               (cy + 1, cx + 1), (cy - 1, cx - 1), (cy + 1, cx - 1), (cy - 1, cx + 1)):
                    if 0 <= ny < height and 0 <= nx < width and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
            ys = [p[0] for p in points]
            xs = [p[1] for p in points]
            local = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1), dtype=bool)
            for py, px in points:
                local[py - min(ys), px - min(xs)] = True
            found.append((min(xs), min(ys), max(xs) + 1, max(ys) + 1, local))
    return found


def extract(slug: str) -> dict[str, list[Image.Image]]:
    poster = Image.open(find_poster(slug)).convert("RGB")
    left, top, right, bottom = PANELS[slug]
    panel = np.asarray(poster.crop((left, top, right, bottom))).astype(int)
    background = np.median(panel.reshape(-1, 3), axis=0)
    distance = np.sqrt(((panel - background) ** 2).sum(axis=2))
    mask = distance > 38
    # Merge nearby specks (shadow edge, hair strands) before labelling.
    found = [c for c in components(mask) if 18 <= (c[2] - c[0]) <= 140 and 30 <= (c[3] - c[1]) <= 140]
    # Sprites are the largest blobs; text labels and ornaments are small.
    found = sorted(found, key=lambda c: -(c[2] - c[0]) * (c[3] - c[1]))[:12]
    if len(found) != 12:
        raise ValueError(f"{slug}: expected 12 sprites, found {len(found)}")
    found.sort(key=lambda c: (c[1] + c[3]) / 2)
    rows = [sorted(found[i * 3:(i + 1) * 3], key=lambda c: c[0]) for i in range(4)]
    result: dict[str, list[Image.Image]] = {}
    for direction, row in zip(DIRECTIONS, rows):
        frames = []
        for x0, y0, x1, y1, local in row:
            patch = panel[y0:y1, x0:x1]
            alpha = (local * 255).astype(np.uint8)
            rgba = np.dstack([patch.astype(np.uint8), alpha])
            frames.append(Image.fromarray(rgba, "RGBA"))
        result[direction] = frames
    return result


def place(frame: Image.Image) -> Image.Image:
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    width, height = frame.size
    if width > CANVAS or height > CANVAS:
        raise ValueError(f"sprite {width}x{height} does not fit {CANVAS}")
    canvas.paste(frame, ((CANVAS - width) // 2, CANVAS - 6 - height), frame)
    return canvas


def save(slug: str, sprites: dict[str, list[Image.Image]]) -> list[Path]:
    base = ROOT / "assets" / "characters" / slug / "map"
    written = []
    for direction, frames in sprites.items():
        folder = base / direction
        folder.mkdir(parents=True, exist_ok=True)
        sheet = Image.new("RGBA", (CANVAS * len(frames), CANVAS), (0, 0, 0, 0))
        for number, frame in enumerate(frames, 1):
            placed = place(frame)
            path = folder / f"{slug}_map_{direction}_{number:02d}.png"
            placed.save(path)
            written.append(path)
            sheet.paste(placed, (CANVAS * (number - 1), 0))
        sheet_path = base / f"{slug}_map_{direction}.png"
        sheet.save(sheet_path)
        written.append(sheet_path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slug", required=True, choices=sorted(PANELS))
    parser.add_argument("--check", action="store_true", help="extract and report sizes without writing files")
    args = parser.parse_args()
    sprites = extract(args.slug)
    for direction, frames in sprites.items():
        print(direction, [f.size for f in frames])
    if not args.check:
        print(f"wrote {len(save(args.slug, sprites))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
