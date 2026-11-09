"""Irregular terrace edge from the floor boundary (TASK-0108).

Usage: python tools/map_terrace_edge.py --map hero_room_01 [--version 14] --pieces RUBBLE_ID[,ID] --seed 3

The floor footprint (`floor_footprint.row_spans`, inclusive cell spans per row) is scanned
for boundary cells (floor cells with an empty neighbour in the four directions). `edge_notches`
returns seeded notch/rubble placement records just outside the boundary; it never changes the
walkable cells. Output is a JSON list of placements for a ground overlay patch.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import sys

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from map_data import load_map

DIRECTIONS = {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}


def floor_cells(footprint: dict) -> set[tuple[int, int]]:
    cells = set()
    for row, spans in enumerate(footprint["row_spans"]):
        for start, end in spans:
            for col in range(int(start), int(end) + 1):
                cells.add((col, row))
    return cells


def boundary(cells: set[tuple[int, int]]) -> list[tuple[int, int, str]]:
    found = []
    for col, row in sorted(cells, key=lambda c: (c[1], c[0])):
        for name, (dx, dy) in DIRECTIONS.items():
            if (col + dx, row + dy) not in cells:
                found.append((col, row, name))
    return found


def edge_notches(data: dict, pieces: list[str], seed: int, density: float = 0.55, prefix: str = "EdgeRubble") -> list[dict]:
    tile = int(data.get("tile_size", 64))
    offset = data.get("ground_offset", [0, 0])
    cells = floor_cells(data["floor_footprint"])
    rng = random.Random(seed)
    placements = []
    for col, row, side in boundary(cells):
        if rng.random() > density:
            continue
        dx, dy = DIRECTIONS[side]
        jitter_along = rng.uniform(-0.3, 0.3) * tile
        jitter_out = rng.uniform(0.0, 0.25) * tile
        cx = offset[0] + (col + 0.5) * tile + dx * (tile * 0.5 + jitter_out) + (jitter_along if dx == 0 else 0)
        cy = offset[1] + (row + 0.5) * tile + dy * (tile * 0.5 + jitter_out) + (jitter_along if dy == 0 else 0)
        placements.append({"id": rng.choice(pieces), "instance_id": f"{prefix}_{len(placements):03d}",
                           "x": round(cx, 1), "y": round(cy, 1), "scale": round(rng.uniform(0.7, 1.0), 2),
                           "edge_side": side, "cell": [col, row]})
    return placements


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--map", required=True)
    parser.add_argument("--version", type=int)
    parser.add_argument("--pieces", required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    result = edge_notches(load_map(args.map, args.version), args.pieces.split(","), args.seed)
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8", newline="\n")
    print(f"{len(result)} edge placements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
