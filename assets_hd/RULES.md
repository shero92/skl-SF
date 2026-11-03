# HD masters (assets_hd) - rules

Owner-supplied high-quality art (~1254 px canvases). These are the quality target for all new and regenerated art.

## Layout
`assets_hd/<category>/<name>_NN.png` + `manifest.json` (source file, sha256, size). Categories: hero, weapons, floor, decor, furniture, lighting, plants, props, architecture, background, concept.
Names are descriptive only. Mapping to catalog ids (G01, F01, W01, ...) is a separate step recorded in the manifest.

## Rules
1. Never overwrite, resize in place or delete a master. Derive runtime sprites into `assets_generated/` from them.
2. New art (any agent) must match these: same pixel density, palette, outline, warm upper-left light, transparent background, one subject per file, no baked shadow.
3. Runtime scale = native footprint size / master size. Keep `native_width/native_height` in metadata; record the master path and sha256 per asset. Downscale with nearest-neighbour or a pixel-art-aware method, never bilinear blur.
4. Hero and weapon masters are protected: add new poses, never edit existing ones; direction and pose must be named before use.
5. `concept/` is reference only, never placed in a map.
6. Requests to Codex must cite a master as the style reference. `visual_approval` stays false until the owner reviews.

## Runtime (implemented)
`assets_hd/hd_map.json` maps every assets_generated PNG to its master. `tools/build_hd_runtime_textures.py --masters <dir>` writes aligned 2x textures to `assets_hd/runtime/` (same file names). `HdAssets.resolve()` makes AssetFactory and the floor painter use them automatically; masters themselves stay local (not in git, 230 MB).
