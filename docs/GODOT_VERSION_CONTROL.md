# Godot 4.4 Git / import hygiene

This project tracks **source files and useful import configuration**, not Godot's disposable caches. Official references:

- https://docs.godotengine.org/en/4.4/tutorials/best_practices/version_control_systems.html
- https://docs.godotengine.org/en/4.4/tutorials/assets_pipeline/import_process.html
- https://docs.godotengine.org/en/4.4/tutorials/best_practices/project_organization.html
- https://docs.godotengine.org/en/4.4/tutorials/assets_pipeline/importing_translations.html

## Track and push (do not blanket-ignore)

- `project.godot`; `*.gd`, `*.tscn`, `*.tres`; authored gameplay source JSON and CSV.
- `*.png` and other **source game art**, including `map_factory/parts/**`.
- Companion `*.png.import` / other `<resource>.import` for **game assets**. The official import guide says these contain meaningful importer options; share across machines. Godot's `.godot/imported/**` cache is different.
- `*.gd.uid` script UIDs for stable references across machine checkouts. Do not mistake these for temporary caches.
- `docs/previews/**/*.png` as reproducible *documentation/QA screenshots* (optional retention based on team needs, but keep reviewed evidence).
- Source art and metadata in `map_factory/references/`, catalogs and immutable map history, when reviewed.

## Ignore / never push

- `.godot/` cache, legacy `.import/` cache, generated `*.translation`, temporary editor/OS files, Python virtual env/cache.
- Unnecessary screenshot-specific `docs/previews/**/*.import`. These are deliberately NOT game assets; `docs/previews/.gdignore` stops their import and hides them from Godot's resource browser. Never put `.gdignore` in a runtime asset folder (such as `map_factory/parts` or `map_factory/metadata`).
- Keep PNG screenshots; do not confuse exclusion of PNG.import metadata with removal of PNG visual evidence.

## Why local project.godot may show modified

`map_factory/metadata/production_queue.csv` is *a production spreadsheet*, not language localization. Godot 4.4 interprets CSV as translation by default and may add entries to `project.godot` or generate `production_queue.*.translation`. Inspect `git diff -- project.godot` before staging. If caused by this CSV, use Godot's Import dock to choose **Skip File (not exported)** / appropriate non-translation import mode, reimport it, and review the generated `production_queue.csv.import` settings for a separate commit. Never ignore every `*.csv.import`; other projects may have real translation settings. A future refactor could move tooling-only CSV outside Godot's resource root, but update dependent scripts first.

## Windows: what to do with the current git status

1. **Do not** run `git add .` indiscriminately. Keep local edits safe and inspect diffs first.
2. `git diff -- project.godot`: if it only contains accidental CSV translation registration, discard *that specific unwanted change* after verifying; preserve any real project settings.
3. `git diff -- docs/previews/map_factory_renders/hero_room_01_v0009.png.import`: screenshot importer churn is no longer tracked by this cleanup.
4. `git add -- map_factory/parts` to stage reviewed first-time `*.png.import` files for real game graphics, then `git diff --cached --stat`. Store GDScript UIDs with their `.gd` files. Do not commit unreviewed unrelated edits.
5. Once the hygiene PR is merged, update local checkout; local modifications to paths removed from Git may need to be stashed first. Verify `git status`.
6. If Windows EOL changes cause false diffs, the repository `.gitattributes` standardizes LF (as Godot recommends). Do not blindly discard changed `project.godot`.

**Only import configuration for screenshots is intentionally removed here,** not importer configuration for production art. A global `*.import` ignore would contradict the official Godot 4 workflow.
