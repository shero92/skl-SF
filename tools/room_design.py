"""Design a Map Factory room in code: place, move, turn, resize and remove parts, then write one patch.

    from room_design import Design
    d = Design("hero_room_01")
    d.place("P05", "FernByArch", 610, 330, scale=0.6, rotation=12)      # decor/plant anywhere
    d.transform("BedRug", x=450, y=640, scale=2.0)                      # free-move a grid part
    d.remove("OldCrate")
    d.write_patch("why this version exists")   # then: map_factory_cli.py apply --manifest <path>

Walking stays on squares: a part that has grid_placement keeps reserving its cells; `free_transform`
only frees what is drawn (position, angle, size). Nothing is generated; history is never edited.

Execution provenance: Agent: claude (Claude Code); model: Fable 5.2.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from map_factory_cli import LAYERS, digest_json  # noqa: E402


class Design:
    def __init__(self, map_id: str, root: Path = ROOT):
        self.map_id = map_id
        self.dir = root / "map_factory/maps" / map_id
        self.latest = json.loads((self.dir / "latest.json").read_text(encoding="utf-8"))
        self.changes: list[dict] = []

    def find(self, name: str) -> dict | None:
        """The placed block with this instance_id in the latest snapshot (read-only copy)."""
        for layer in LAYERS:
            for item in self.latest.get(layer, []):
                if item.get("instance_id") == name:
                    return dict(item, layer=layer)
        return None

    def place(self, part: str, name: str, x: float, y: float, *, scale: float = 1.0, rotation: float = 0.0,
              flip: bool = False, layer: str = "objects", z: int = 0) -> "Design":
        """Add an independent piece (plant, decor, prop) at any pixel position, angle and size."""
        block = {"id": part, "instance_id": name, "x": float(x), "y": float(y), "scale": float(scale)}
        if rotation:
            block.update(rotation_degrees=float(rotation), free_transform=True)
        if flip:
            block["flip_h"] = True
        if z:
            block["z_index"] = int(z)
        self.changes.append({"op": "add_block", "layer": layer, "block": block})
        return self

    def transform(self, name: str, *, x: float | None = None, y: float | None = None, scale: float | None = None,
                  rotation: float | None = None, flip: bool | None = None, layer: str | None = None,
                  part: str | None = None, z: int | None = None) -> "Design":
        """Move, turn, resize, flip, re-layer or re-skin an existing piece. Grid cells (if any) are kept."""
        if self.find(name) is None:
            raise ValueError(f"No placed block named {name}")
        fields = {"x": x, "y": y, "scale": scale, "rotation_degrees": rotation, "flip_h": flip,
                  "layer": layer, "id": part, "z_index": z}
        updates = {k: v for k, v in fields.items() if v is not None}
        if {"x", "y", "scale", "rotation_degrees"} & set(updates):
            updates["free_transform"] = True
        self.changes.append({"op": "update_block", "instance_id": name, "set": updates})
        return self

    def remove(self, name: str) -> "Design":
        self.changes.append({"op": "remove_block", "instance_id": name})
        return self

    def write_patch(self, note: str) -> Path:
        if not self.changes:
            raise ValueError("Nothing to change")
        version = int(self.latest["version"])
        previous = json.loads((self.dir / "patches" / f"v{version:04d}.json").read_text(encoding="utf-8"))
        patch = {"manifest_version": 1, "map_id": self.map_id, "base_version": version,
                 "base_sha256": digest_json(self.latest), "note": note,
                 "source_image": previous["source_image"], "changes": self.changes}
        out = self.dir / "patches" / f"v{version + 1:04d}.json"
        out.write_text(json.dumps(patch, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        return out
