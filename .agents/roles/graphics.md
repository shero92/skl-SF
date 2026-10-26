# Graphics specialist — separate production role

The graphics producer role may be filled by Codex, Claude Code (owner decision 2026-10-26, environment art only) or an external specialist. It does not own gameplay/map logic, and the producing session never reviews its own work.

1. Read the **single assigned** `.agents/graphics/requests/ART-*.md` file, the referenced source image, and the relevant art-direction policy. Do not preload all assets.
2. Before rendering, check `map_factory/metadata/asset_index.json`, the existing target PNG and `.agents/graphics/QUEUE.md` to avoid duplicates and regressions.
3. Refuse to invent unavailable reference details: a `blocked_reference` request must wait for the authentic source asset to be committed; with an unconfirmed SHA-256 the delivery stays unapproved.
4. Produce independently editable high-quality RGBA PNGs in the request-specific delivery folder; no baked-in adjacent props, labels, cropping artifacts or fake upscales. Respect dimensions/facing/anchors.
5. Create a delivery `manifest.json` listing each expected output and its SHA-256. Update the art request checklist/status to delivered; never overwrite `map_factory/parts` directly.
6. A separate reviewer validates screenshot-scale quality, all directions and metadata. Only coding/integration work may import approved art, preserving stable asset IDs and map version history.
