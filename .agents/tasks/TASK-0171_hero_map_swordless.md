---
id: TASK-0171
status: review
owner: codex
agent: codex
branch: codex/art-0054-hero-map
depends_on: TASK-0168
issue: none
art_request: ART-0054
touches: INDEX.md,game_factory/hero_map_art_index.json,tools/prepare_art0054.py,assets_hd/hero/map_sf_down_idle/v001,game_factory/environment/ART-0054/v001,.agents/graphics/deliveries/ART-0054,.agents/graphics/requests/ART-0054_hero_map_sprite_shining_force_style.md
test: python tools/graphics_validation.py --changed; python tools/run_tests.py --changed
done_when: One independently generated transparent down-idle hero without sword, native frame and measured metadata, genuine Godot review capture, published task branch.
---
# ART-0054 swordless map hero
Owner override 2026-11-13: no sword. One down-idle frame only; preserve existing animation sources. Approval basis: owner_automatic_20261111. Runtime activation of forty missing directional frames is outside this delivery.

## Evidence
- Master 1254x1254, transparent native 96x96, anchor [48,90], one unarmed down-idle frame.
- Custom PNG checks pass. Real Godot SubViewport capture 1536x1024. Generic graphics validator exit 0 (0 registry PNGs selected; source-specific validation is recorded separately).
- Full changed-test suite: 90/90 passed on fd708c5a; existing frame context copied read-only, never staged.
- No rejected attempts; no old character sources or active animation registry replaced.
- Delivery metadata and per-piece index under game_factory/environment/ART-0054/v001; hero map art navigation added to INDEX.md.
- Next: integrate this delivered frame as a reviewed style source; directional walks remain a separate request.

- PR: https://github.com/shero92/skl-SF/pull/193 (base claude/photo-backdrop-test; open, not merged).
- Art commit: bf8b69d3f782922adfccfd84c6d6bc3262d3e5e7. Local editor history excluded after saving all task files; post-isolation editor 4/4 and equipment 2/2 pass.
