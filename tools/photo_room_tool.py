"""Author a photo room: a Map Factory map whose picture is one painting, with walk squares, depth objects and life.

    python tools/photo_room_tool.py new --map-id sunset_hall --image map_factory/references/sunset_hall.png
    python tools/photo_room_tool.py check --map-id sunset_hall
    python tools/photo_room_tool.py preview --map-id sunset_hall [--out preview.png]

A photo room lives in map_factory/photo_rooms/<map_id>.json and is played by scenes/main.gd (set
Main.next_map_id) with Shining Force style one-square steps, the high-resolution hero, objects the hero walks
behind, height shadows and the sea / cloud / mist / lantern touches. See map_factory/PHOTO_ROOMS.md.

`new` creates the Map Factory map from a preset when the id is not registered yet and writes a starting file.
`check` validates the file and prints PHOTO_ROOM_OK <id> or one PHOTO_ROOM_ERROR line per problem.
`preview` draws walk squares (green), depth objects (red outline, blue base line), shadows (purple), the hero's
step squares (white dots) and lanterns (orange) over the painting so the numbers can be judged by eye.
No painting is created or changed.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

PHOTO_DIR = Path("map_factory/photo_rooms")
KNOWN_KEYS = {"schema_version", "map_id", "note", "image", "spawn", "navigation", "moves", "hero_only", "hero_height", "hero_step",
              "hero_step_offset", "patches", "sea", "clouds", "lanterns", "petals", "mist", "depth_objects"}


def photo_path(map_id: str, root: Path = ROOT) -> Path:
    return root / PHOTO_DIR / f"{map_id}.json"


def starting_file(map_id: str, image: str, size: tuple[int, int]) -> dict:
    cols, rows = size[0] // 32, size[1] // 32
    return {
        "schema_version": 1,
        "map_id": map_id,
        "note": "Photo room. Fill in navigation.regions (walk squares of 32 px, [x, y, w, h] in squares), depth_objects, sea, lanterns; "
                "run tools/photo_room_tool.py preview to see them over the painting.",
        "image": "res://" + image.replace("\\", "/"),
        "spawn": [size[0] // 2, size[1] // 2],
        "navigation": {"schema_version": 1, "origin": [0, 0], "cell_size": 32, "grid_size": [cols, rows],
                       "default": {"walk": False}, "regions": []},
        "hero_only": True,
        "hero_height": 128,
        "hero_step": 64,
        "hero_step_offset": [-16, 16],
        "mist": {"strength": 0.32, "shadow": 0.2, "speed": 1.0},
        "petals": {"amount": 16, "area": [0, 0, size[0], size[1]]},
        "depth_objects": [],
        "sea": [],
        "lanterns": [],
        "patches": [],
        "moves": {},
    }


def new_room(map_id: str, image: str, root: Path = ROOT, create_map: bool = True) -> Path:
    from PIL import Image
    import map_factory_cli as cli
    source = root / image
    if not source.is_file():
        raise ValueError(f"Painting not found: {image}")
    target = photo_path(map_id, root)
    if target.exists():
        raise ValueError(f"Photo room already exists: {target.relative_to(root)}")
    if create_map and map_id not in cli.registry(root)["maps"]:
        cli.create_map(root, map_id, "indoor_room", note="Created for a photo room by tools/photo_room_tool.py")
    with Image.open(source) as picture:
        size = picture.size
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(starting_file(map_id, image, size), indent=2) + "\n", encoding="utf-8", newline="\n")
    return target


def check_room(data: dict, root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for key in data:
        if key not in KNOWN_KEYS:
            problems.append(f"unknown key: {key}")
    image = str(data.get("image", ""))
    if not image.startswith("res://") or not (root / image[len("res://"):]).is_file():
        problems.append(f"image not found: {image}")
        size = (0, 0)
    else:
        from PIL import Image
        with Image.open(root / image[len("res://"):]) as picture:
            size = picture.size
    nav = data.get("navigation", {})
    grid = nav.get("grid_size", [0, 0])
    if not nav.get("regions"):
        problems.append("navigation.regions is empty: nobody can walk")
    for region in nav.get("regions", []):
        x, y, w, h = region.get("rect", [0, 0, 0, 0])
        if w <= 0 or h <= 0 or x < 0 or y < 0 or x + w > grid[0] or y + h > grid[1]:
            problems.append(f"walk region outside the grid: {region.get('rect')}")
    step = float(data.get("hero_step", 0))
    if step < 0:
        problems.append("hero_step must be 0 (free walking) or a square size")
    seen = set()
    for obj in data.get("depth_objects", []):
        name = str(obj.get("id", ""))
        if not name or name in seen:
            problems.append(f"depth object id missing or repeated: {name!r}")
        seen.add(name)
        poly = obj.get("poly", [])
        if len(poly) < 3:
            problems.append(f"depth object {name}: outline needs at least 3 points")
        for point in poly:
            if len(point) != 2 or not (0 <= point[0] <= size[0] and 0 <= point[1] <= size[1]):
                problems.append(f"depth object {name}: point outside the painting {point}")
                break
        if poly and not (min(p[1] for p in poly) <= float(obj.get("base_y", -1)) <= max(p[1] for p in poly) + 400):
            problems.append(f"depth object {name}: base_y {obj.get('base_y')} is far from its outline")
        for edge in obj.get("shadow", []):
            if len(edge) not in (4, 5):
                problems.append(f"depth object {name}: a shadow is [x1, x2, y, height] or [x1, y1, x2, y2, height]")
    for polygon in data.get("sea", []):
        if len(polygon) < 3:
            problems.append("a sea polygon needs at least 3 points")
    return problems


def preview(data: dict, out: Path, root: Path = ROOT) -> Path:
    from PIL import Image, ImageDraw
    image = Image.open(root / str(data["image"])[len("res://"):]).convert("RGBA")
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    nav = data.get("navigation", {})
    cell = float(nav.get("cell_size", 32))
    for region in nav.get("regions", []):
        x, y, w, h = region["rect"]
        draw.rectangle([x * cell, y * cell, (x + w) * cell - 1, (y + h) * cell - 1], fill=(0, 255, 0, 60), outline=(0, 120, 0, 200))
    for obj in data.get("depth_objects", []):
        poly = [tuple(p) for p in obj["poly"]]
        draw.polygon(poly, fill=(255, 0, 0, 35), outline=(255, 0, 0, 255))
        xs = [p[0] for p in poly]
        draw.line([(min(xs), obj["base_y"]), (max(xs), obj["base_y"])], fill=(0, 90, 255, 255), width=2)
        draw.text((min(xs) + 3, min(p[1] for p in poly) + 3), str(obj["id"]), fill=(255, 255, 0, 255))
        for edge in obj.get("shadow", []):
            if len(edge) == 4:
                x1, x2, y, height = edge
                a, b = (x1, y), (x2, y)
            else:
                x1, y1, x2, y2, height = edge
                a, b = (x1, y1), (x2, y2)
            rx, ry = height * 0.62, height * 0.3
            draw.polygon([a, b, (b[0] + rx, b[1] + ry), (a[0] + rx, a[1] + ry)], fill=(120, 0, 200, 70))
    step = float(data.get("hero_step", 0))
    if step > 0:
        ox, oy = data.get("hero_step_offset", [0, 0])
        for row in range(int(image.height / step) + 1):
            for col in range(int(image.width / step) + 1):
                px, py = ox + col * step + step / 2, oy + row * step + step / 2
                draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255, 160))
    for light in data.get("lanterns", []):
        draw.ellipse([light[0] - 6, light[1] - 6, light[0] + 6, light[1] + 6], outline=(255, 150, 0, 255), width=2)
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.alpha_composite(image, layer).convert("RGB").save(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["new", "check", "preview"])
    ap.add_argument("--map-id", required=True)
    ap.add_argument("--image", help="project-relative painting for `new`")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    try:
        if args.command == "new":
            if not args.image:
                raise ValueError("--image is required")
            print(f"PHOTO_ROOM_CREATED {new_room(args.map_id, args.image).relative_to(ROOT)}")
            return 0
        data = json.loads(photo_path(args.map_id).read_text(encoding="utf-8"))
        if args.command == "check":
            problems = check_room(data)
            for line in problems:
                print("PHOTO_ROOM_ERROR " + line)
            if not problems:
                print(f"PHOTO_ROOM_OK {args.map_id}")
            return 1 if problems else 0
        out = args.out or ROOT / "docs" / "previews" / "photo_rooms" / f"{args.map_id}_overlay.png"
        print(f"PHOTO_ROOM_PREVIEW {preview(data, out)}")
        return 0
    except Exception as error:
        print(f"PHOTO_ROOM_ERROR {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
