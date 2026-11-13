# Map brief — copy to `docs/maps/briefs/<map_id>.md`

Rules: [docs/MAP_GRAPHICS_RULES.md](../../docs/MAP_GRAPHICS_RULES.md). Fill every line. An empty line, or a line you had to invent, stops stage 2; ask the owner.

- **Map id / name:**
- **Story source:** file and scene id (for example `docs/story/chapter_01/01_home_and_storm.md` SC01) — marker: approved / proposed / open
- **Story phase:** (what has and has not happened yet; early maps never show later events)
- **Purpose:** walk / battle / both — and what the player does here
- **Size:** squares (64 px), screens (1536x1024 each)
- **Exits:** neighbour map id, edge or square, return square in this map, return square in the neighbour (both must be walkable and on a step square)
- **Mood, time, weather, light:** (light from the upper left, shadows to the lower right unless the owner says otherwise)
- **Place and surfaces:** ground types, vertical masses (cliff, wall, ruin), water, vegetation, props — each as a short list of separate pieces
- **Story allows:**
- **Story forbids on this map:** (for example human settlement, guards, markets, maintained gardens, baked characters; secrets from `shared/visions_creatures_and_secrets.md`)
- **Separate from the environment:** NPCs, creatures, the hero, the companion (never baked into pictures)
- **Moving touches:** sea, foam, lanterns, fog, petals, clouds, birds (each needs its own animation pieces)
- **Shared kit reused:** asset ids already in `map_factory/metadata/asset_index.json`
- **Open questions for the owner:**
- **Board:** `map_factory/references/<map_id>_target_<yyyymmdd>.png` — SHA-256 — owner approved: no / yes (date)
