# skl-SF — project charter

- **Product:** Godot 4 pixel-art coastal fantasy RPG inspired by classic tactical JRPG presentation.
- **Current development scope:** reusable environment/map factory and Hero Room visual fidelity. **No edits to characters, NPC behavior, dialogue, portraits, player movement or game UI** in this workstream.
- **Canonical map implementation:** `map_factory/` and `tools/map_factory_*.py`, compiled versions in `map_factory/maps/`, map-only preview in `scenes/map_factory_preview.tscn`.
- **Reference style:** `docs/REFERENCE_ART_DIRECTION.md` and the actual user-provided image. Do not invent missing reference inputs; preserve a source file and hash before claiming visual fidelity.
- **Core invariant:** the runtime constructs rooms from reusable, individually indexed assets and layered JSON; never flatten a room screenshot into a fake assembled map.
- **Scope boundary:** map metadata may describe navigation constraints; character movement, flight, swimming and abilities belong to separate gameplay systems.
- **Current known quality gap:** real Godot room render differs from the desired image; no reviewed final art claimed. See `docs/MAP_FACTORY_REFERENCE_DIAGNOSIS.md`.
- **How to find code:** use `INDEX.md`, then the relevant folder `INDEX.md`; `FILES.md` lists all direct entries.
- **Project state:** `STATUS.md`. **Roadmap:** `PLAN.md`. **Agent rules:** `AGENTS.md`.
