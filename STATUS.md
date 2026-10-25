# skl-SF — current state (verified from main, 2026-10-25)

> Update this file only after checking current GitHub or local project state. This is a snapshot, not a live CI signal.

- **Branch inspected:** `main` at `be9ec8413af1cee7eb78f65038252722bc4d9560`.
- **Engine:** Godot 4; `project.godot` uses `scenes/main.tscn`.
- **Current scope:** map factory / rooms / environment only; do not edit characters, UI or NPC gameplay.
- **Map registry:** `hero_room_01` v0010; `courtyard_demo_01` v0002.
- **Assets:** 229 records / 229 PNGs in catalog (all marked `needs_cleanup`; zero artist-approved).
- **Hero Room:** 78 positioned environment blocks; no `facing` values or 4-view groups in v0010.
- **Reference:** original scene not committed; current Hero Room source_image.path and sha256 are null, visual_qa is `needs_review`.
- **Navigation:** provisional; full physics and gameplay abilities are not implemented by the map factory.
- **CI:** validation workflows exist; latest observed map-factory validation on main passed, but visual parity is not machine-proven.
- **Documentation debt:** some historical docs/README figures cite 218 assets or old room versions; use registry/catalog as live source.
- **Immediate next development task:** merge this navigation/index setup, then import exact reference image and verify actual Godot before-after captures.
- **Known risk:** automation scripts currently push compiled assets/map versions directly to main; use separate agent branches and review before integration.

## Handoff after a task
Write at most: **What changed | Files | Tests actually run/results | Blockers | Next one task**. Do not paste full logs or repeat files already linked.
