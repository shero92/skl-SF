# Archived GitHub Actions — disabled intentionally

These original workflow YAML files were **moved out of `.github/workflows/`**, which disables all their triggers. No scripts, art assets, gameplay or history were deleted.

## Reason for disabling

- `art_quality_cleanup.yml` — Edits original sprite crops and commits PNGs.
- `audit_assets.yml` — Changes and commits asset audit metadata.
- `audit_room_assets.yml` — Writes/commits room QA metadata.
- `backfill_map_blocks.yml` — Regenerates map metadata and writes automatically.
- `build_asset_previews.yml` — Generates QA gallery files and commits them automatically.
- `capture_map_previews.yml` — Generates Godot screenshots and writes directly to main.
- `check_floor_emblem.yml` — Generates/commits floor QA image.
- `complete_remaining_art.yml` — Synthesizes missing production sprites.
- `create_missing_hero_art.yml` — Generates Hero Room environment/shadow PNGs and pushes to main.
- `curate_high_detail_sprites.yml` — Rewrites prop sprite cutouts.
- `curate_wall_lanterns.yml` — Rewrites lantern sprite transparency.
- `generate_character_art.yml` — Generates character animation and portraits (out of scope).
- `generate_core_assets.yml` — Synthesizes core production PNG parts.
- `generate_missing_details.yml` — Synthesizes environment detail sprites.
- `import_asset_pack.yml` — Imports/commits production PNG assets from ZIP automatically.
- `map_factory_bootstrap.yml` — Bootstraps and writes map snapshot data automatically.
- `process_map_intake.yml` — Writes AI-supplied maps/metadata to main automatically.
- `repaint_dialogue_ui.yml` — Repaints game UI art (out of scope).
- `repaint_ocean.yml` — Repaints ocean production textures.
- `repaint_sandstone_floor.yml` — Repaints production floors.
- `restore_high_detail_floors.yml` — Replaces/restores production floor PNGs.

Keep historical definitions for review; do not move back into `.github/workflows/` without explicit user approval and an isolated review PR.
All GitHub Actions that remain active must be read-only validation or guarded goal-completion notification.
