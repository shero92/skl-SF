"""Shared loaders for Map Factory data tools (audit, diff, generators).

Execution provenance: Agent: claude (Claude Code); model: Sonnet 5.5.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTANCE_LISTS = ("background_objects", "ground_overlays", "back_objects", "objects", "front_objects")


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def map_path(map_id: str, version: int | None = None, root: Path = ROOT) -> Path:
    base = root / "map_factory" / "maps" / map_id
    if version is None:
        return base / "latest.json"
    return base / "versions" / f"v{version:04d}.json"


def load_map(map_id: str, version: int | None = None, root: Path = ROOT) -> dict:
    return load_json(map_path(map_id, version, root))


def iter_instances(data: dict):
    """Yield (list_name, record) for every placed instance in a map snapshot."""
    for name in INSTANCE_LISTS:
        for record in data.get(name, []) or []:
            if isinstance(record, dict):
                yield name, record


def load_catalog(root: Path = ROOT) -> dict[str, dict]:
    """Catalog of placeable assets keyed by asset id (assets_generated manifest)."""
    manifest = load_json(root / "assets_generated" / "manifest.json")
    catalog = {item["asset_id"]: item for item in manifest.get("assets", []) if "asset_id" in item}
    # Parts registered later (Blender and HD pack deliveries) live only in the asset index.
    index = root / "map_factory" / "metadata" / "asset_index.json"
    if index.is_file():
        for item in load_json(index).get("assets", []):
            catalog.setdefault(item["id"], {"asset_id": item["id"], "footprint_tiles_x": 1, "footprint_tiles_y": 1})
    return catalog
