# Generated versus planned art

The pipeline uses two routes:
1. **High-detail reference art** from AI concept sheets, extracted and artist-reviewed individually.
2. **Procedural base textures** via \`tools/generate_core_assets.py\` for floor drafts, reusable alpha shadows and dialogue UI frames.

Running \`python tools/generate_core_assets.py\` creates **48 independent RGBA PNGs** (22 floor variants, 16 shadows, 10 UI icons/frames). It never overwrites existing PNGs. The workflow on GitHub generates these once and commits them. It does NOT generate the other 170 custom illustrations.

The full catalog still contains 218 named slots. A \`planned\` status means PNG is missing. \`needs_cleanup\` is an imported/generator draft not approved for final production. \`ready\` is suitable for first-pass functional use. Character animation, ocean and architecture sprites must be painted and QA checked.

Never call procedural drafts high-quality completed hero-room sprites; replace them with individually authored texture files while preserving stable IDs.
