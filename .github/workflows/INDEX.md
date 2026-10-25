# GitHub Actions workflows — targeted navigation

| Work type | Main workflow(s) |
| --- | --- |
| Project parser / headless Godot | `godot_validate.yml` |
| Map version registry and unit tests | `validate_map_factory.yml` |
| Every-map Godot smoke/facing checks | `map_factory_godot_smoke.yml` |
| AI map manifests to versioned maps (writes back to repo) | `process_map_intake.yml` |
| Initial version bootstrap/backfill (may write) | `map_factory_bootstrap.yml`, `backfill_map_blocks.yml` |
| Actual Godot screenshot capture (writes images) | `capture_map_previews.yml` |
| Image presence / regressions | `audit_assets.yml`, `audit_room_assets.yml`, `quality_guard.yml` |
| Repainting, curated art, core/character generation | remaining workflows; **outside the active map-only scope where they edit characters/UI** |

Browse [all workflow filenames](FILES.md). Prefer PR-triggered read-only validation; don't trigger publishing/repainting automatically as a side effect of routine agent edits.
