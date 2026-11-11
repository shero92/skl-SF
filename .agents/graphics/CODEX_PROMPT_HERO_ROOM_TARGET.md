# Codex prompt — Hero Room target art (2026-11-10)

Paste everything below the line into Codex. It is self-contained; Codex reads the repo files it names.

---

You are Codex, the graphics producer for the SKL-SF Godot project (repo `H:\shining force\skl-SF`, branch from `main`, never push to `main`). Task: produce the independent environment images that are still missing so that the Hero Room matches the owner's target picture.

Read first, in this order, and obey them: `AGENTS.md`, `.agents/workflows/GRAPHICS.md`, `docs/GRAPHICS_PRODUCTION_POLICY.md`, `assets_hd/RULES.md`, `docs/OWNER_ART_APPROVAL_20261109.md`, then **`docs/HERO_ROOM_TARGET_20261110_ASSET_SPEC.md`** (the full plan: reference, rules, gap matrix, batches, per-asset specs, acceptance checklist).

The reference picture is `map_factory/references/hero_room_01_target_20261110.webp` (sha256 `4e55aeaa5a5e500760f48fed75c3ce7f6d56d55c1ca06b8c70839cce517e4323`; same design as `hero_room_01_target_20261103.png`). It is a style and composition reference only: never paste, crop or trace it. Compare with the current render `docs/previews/map_factory_renders/t0128_v0021/hero_room_01_v0021.png`.

Work in batches, one ART request per generation, one subject per PNG:
1. **Batch B1:** ART-0019 study table (four independent views: south, north, east, west), **ART-0039** wooden stool, ART-0011 large potted plant in a blue-white vase, ART-0025 entrance stairs.
2. **Batch B2:** ART-0020 bookshelf with armillary sphere and candles, ART-0008 headboard shelf, ART-0006 sphere-topped stone post, ART-0024 rope posts and rails, ART-0022 oblique compass inlay.
3. **Batch B3:** **ART-0037** seamless sea light-lattice overlay, ART-0023 side banner and lantern views, ART-0005 compass door, **ART-0038** wall run with a window opening.
4. **Batch B4 (optional):** the remaining polish requests listed in the spec.
Where an older request is `blocked_reference`, the committed target above satisfies its reference gate; follow the request text but deliver an independent image, not a stacked composite.

Hard rules: transparent RGBA PNG; no baked shadow, ground, frame, text, watermark or characters; no multi-pose sheet; no flipping or rotating one view to make another; no cropping from a generated sheet; use only the built-in `image_gen` (no Aider, no paid or external image service); never edit or delete anything in `assets/`, `assets_generated/`, `assets_hd/` masters, `map_factory/parts/`, `map_factory/references/` or earlier map versions. Style: warm limestone, cobalt-and-gold cloth, oak wood, green foliage with white flowers, upper-left light, hard pixel clusters with a 1-2 px dark outline at 1x, density like the `assets_hd` masters. Build each master at least 4x its on-canvas size (sizes are in the spec).

For every file: save the master under `assets_hd/<category>/<group>/v001/` (add `.gdignore`), copy it to the exact path in the request under `.agents/graphics/deliveries/ART-####/`, write `manifest.json` (`request_id`, paths, SHA-256, pixel_size, mode, alpha extrema, alpha-128 bounds, origin = bottom centre of visible pixels, prompt text, rejected attempts kept in `rejected/`), render native review images and one real Godot capture under `game_factory/environment/ART-####/v001/`, run `python tools/graphics_validation.py --changed` and `python tools/run_tests.py --changed`, set the request to `delivered` (never `reviewed` or `integrated`; the owner approves, Claude integrates). Use a branch and a PR per batch; stage only your files; do not touch Golden Cyclone files or files another agent has open.

Report per batch in Arabic: what was produced (paths and hashes), what was rejected and why, what you could not do, and the PR link. Do not claim visual approval.
