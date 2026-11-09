"""Connected wall runs from a path blueprint (TASK-0107).

A blueprint is a dict:
  {"seed": 7, "step": 64, "damage": 0.3, "inside": "right",
   "pieces": {"straight": ["W01","W02"], "broken": ["W03","W04","W10"],
              "corner_outer": "W09", "corner_inner": "W08", "cap": "W07"},
   "path": [[x, y], ...], "render_layer": "walls", "prefix": "GenWall"}

`generate` returns placement records (id, instance_id, x, y, scale, render_layer) along the
path every `step` pixels with the same seed -> same result. Turning vertices get corner
pieces (outer when the turn is away from the room interior, inner when toward it). Only
registered ids named in the blueprint are used; nothing is drawn.

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import math
import random


def _cross(a: tuple, b: tuple) -> float:
    return a[0] * b[1] - a[1] * b[0]


def _unit(a: list, b: list) -> tuple[float, float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    return (dx / length, dy / length, length) if length else (0.0, 0.0, 0.0)


def generate(blueprint: dict) -> list[dict]:
    path = blueprint["path"]
    if len(path) < 2:
        raise ValueError("path needs at least two points")
    pieces = blueprint["pieces"]
    step = float(blueprint.get("step", 64))
    damage = float(blueprint.get("damage", 0.3))
    inside = blueprint.get("inside", "right")
    layer = blueprint.get("render_layer", "walls")
    prefix = blueprint.get("prefix", "GenWall")
    rng = random.Random(int(blueprint.get("seed", 0)))
    placements: list[dict] = []
    last_key = None

    def add(asset: str, x: float, y: float, kind: str) -> None:
        nonlocal last_key
        key = (round(x, 1), round(y, 1))
        if key == last_key:
            if kind == "cap" and placements:  # the end cap replaces the last run piece
                placements[-1].update({"id": asset, "wall_kind": "cap"})
            return
        last_key = key
        placements.append({"id": asset, "instance_id": f"{prefix}_{len(placements):03d}",
                           "x": round(x, 1), "y": round(y, 1), "scale": 1.0, "render_layer": layer, "wall_kind": kind})

    for index in range(len(path) - 1):
        a, b = path[index], path[index + 1]
        ux, uy, length = _unit(a, b)
        if length == 0:
            continue
        count = max(1, int(length // step))
        for n in range(count + 1):
            x, y = a[0] + ux * step * n, a[1] + uy * step * n
            if n == 0 and index > 0:
                prev = _unit(path[index - 1], a)
                turn = _cross((prev[0], prev[1]), (ux, uy))
                if abs(turn) > 1e-6:
                    toward_inside = turn > 0 if inside == "right" else turn < 0
                    add(pieces["corner_inner" if toward_inside else "corner_outer"], x, y, "corner")
                    continue
            if n == count and length - step * count < step * 0.25 and index < len(path) - 2:
                continue  # the next segment places the corner here
            if rng.random() < damage and pieces.get("broken"):
                add(rng.choice(pieces["broken"]), x, y, "broken")
            else:
                add(rng.choice(pieces["straight"]), x, y, "straight")
    if pieces.get("cap"):
        end = path[-1]
        add(pieces["cap"], end[0], end[1], "cap")
    return placements
