# skl-SF — project charter

- **Engine:** Godot 4, coastal fantasy RPG, high-detail pixel art.
- **Current workstream:** environment maps/rooms only. No actors, gameplay AI, dialogue or UI.
- **Factory:** versioned room JSON + registry + reusable PNG blocks remain available. The owner's2026-11-13 exterior uses complete high-detail square-ground paintings with separate authored navigation and actors; see `map_factory/painted_worlds/INDEX.md` and `docs/OWNER_PHOTO_WORLD_20261113.md`.
- **Art direction:** `docs/REFERENCE_ART_DIRECTION.md`; genuine user source references must be present in `map_factory/references/` before visual fidelity can be verified.
- **Quality policy:** existing parts are not production-approved solely because PNG files exist; avoid duplicate generation, keep stable IDs and per-revision provenance.
- **Development model:** independent coding agents on separate branches + a separate specialist graphic producer + independent reviewer. `AGENTS.md` is the only shared root auto-loaded instruction file.
- **Navigation:** `INDEX.md` then feature `INDEX.md`; `.agents/` provides coordination on demand.
- **Story:** `docs/story/INDEX.md` → `docs/design/STORY_CANON_AR.md` → relevant chapter. Hidden Island is a wild hidden island with no other known human residents at the opening; nonhuman allies and abandoned overgrown ruins remain part of the setting. Owner2026-11-13 requests painted high-detail exterior scenes, not tile assembly.
