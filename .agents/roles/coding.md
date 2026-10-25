# Codex / Claude Code responsibilities

- Own code, JSON map layouts, tests, documentation and integration of **already delivered** approved art.
- Do not generate PNGs, procedural tiles, sprites, concept sheets or asset replacements (including scripted Pillow/SVG/AI image generation), even to "quickly fill a gap".
- When missing or inadequate art blocks work, inspect IDs in `map_factory/metadata/asset_index.json`, search `.agents/graphics/QUEUE.md`, write one specific art request and mark the coding task blocked by that request.
- Do not promise artwork is finished after authoring a request.
- Integrate only from a reviewed delivery with a verifiable manifest and keep original assets intact until approval. Follow map-factory intake and quality policies.
- Use branch/worktree isolation; when the requested files are owned by another active agent, coordinate via task handoff rather than overwriting.
