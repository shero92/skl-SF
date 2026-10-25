# skl-SF — project charter

- **Engine:** Godot 4, coastal fantasy RPG, high-detail pixel art.
- **Current workstream:** environment maps/rooms only. No actors, gameplay AI, dialogue or UI.
- **Factory:** versioned room JSON + registry + individually addressable PNG block assets; the game assembles elements in Godot rather than painting a static screenshot.
- **Art direction:** `docs/REFERENCE_ART_DIRECTION.md`; genuine user source references must be present in `map_factory/references/` before visual fidelity can be verified.
- **Quality policy:** existing parts are not production-approved solely because PNG files exist; avoid duplicate generation, keep stable IDs and per-revision provenance.
- **Development model:** independent coding agents on separate branches + a separate specialist graphic producer + independent reviewer. `AGENTS.md` is the only shared root auto-loaded instruction file.
- **Navigation:** `INDEX.md` then feature `INDEX.md`; `.agents/` provides coordination on demand.
