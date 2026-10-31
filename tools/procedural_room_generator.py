#!/usr/bin/env python3
"""B. PROCEDURAL ROOM GENERATOR (separate from the exact reference reconstruction).

Uses the same corrected registry (v2), architecture blueprints and furniture
composites, but picks furniture zones / wall chains from a deterministic seed.
Usage: python tools/procedural_room_generator.py [seed] -> map_factory/rooms/procedural_room_<seed>.json
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from room_assembly import (T, ROOT, expand_blueprint, expand_composite, load_blueprints,  # noqa: E402
                           load_composites, load_registry, make_object)

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 1
rng = random.Random(seed)
reg, bps, comps = load_registry(), load_blueprints(), load_composites()
objs = []
objs += expand_blueprint(reg, bps, "rear_wall_left", "rwl", anchor_cell=(2, 3))
objs += expand_blueprint(reg, bps, "rear_wall_right", "rwr", anchor_cell=(12, 3))
objs += expand_blueprint(reg, bps, "central_arch", "arch", anchor_px=(10 * T, 5 * T))
objs += expand_blueprint(reg, bps, "side_wall_left", "swl", anchor_cell=(2, 4))
objs += expand_blueprint(reg, bps, "side_wall_right", "swr", anchor_cell=(17, 4))
objs += expand_blueprint(reg, bps, "front_wall_left", "fwl", anchor_cell=(2, 10))
objs += expand_blueprint(reg, bps, "front_wall_right", "fwr", anchor_cell=(12, 10))
objs += expand_blueprint(reg, bps, "entrance_stairs", "stairs", anchor_px=(10 * T, 11 * T))
left_zone, right_zone = rng.sample(["bed_area", "table_area"], 2)
origins = {"bed_area": (5, 5), "table_area": (12, 6)}
objs += expand_composite(reg, comps, left_zone, "zoneL", origins[left_zone] if left_zone == "bed_area" else (4, 6))
objs += expand_composite(reg, comps, right_zone, "zoneR", (12, 6) if right_zone == "table_area" else (11, 5))
objs += expand_composite(reg, comps, "bookcase_left_area", "bcl", (3, 4))
objs += expand_composite(reg, comps, "bookcase_right_area", "bcr", (13, 4))
objs.append(make_object(reg, "compass", "D03", ground_anchor_px=(9.75 * T, 8.1 * T), level=1))
for i in range(rng.randint(4, 8)):
    objs.append(make_object(reg, f"flowers_{i}", rng.choice(["P04", "P05", "P06", "P14"]), None,
                            cell=(rng.randint(3, 16), 9), level=3))
ref = json.loads((ROOT / "map_factory/rooms/reference_room_layout.json").read_text(encoding="utf-8"))
ref.update({"map_id": f"procedural_room_{seed}", "title": f"Procedural room seed {seed}", "seed": seed, "objects": objs})
ref["shadows"]["glow_owners"] = [o["object_id"] for o in objs if o["asset_id"] in ("L01", "L04", "L03")]
out = ROOT / f"map_factory/rooms/procedural_room_{seed}.json"
out.write_text(json.dumps(ref, indent=1) + "\n", encoding="utf-8")
print("wrote", out, len(objs), "objects")
