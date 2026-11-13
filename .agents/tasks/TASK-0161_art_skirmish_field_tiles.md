---
id: TASK-0161
status: review
owner: codex
agent: codex
priority: low
branch: codex/art-0041-skirmish-tiles
depends_on: TASK-0147
issue: none
art_request: ART-0041
touches: .agents/tasks/TASK-0161_art_skirmish_field_tiles.md,.agents/graphics/deliveries/ART-0041,.agents/graphics/requests/ART-0041_skirmish_field_tiles.md,assets_hd/floor/skirmish_field/v001,assets_hd/props/skirmish_rock/v001,assets_hd/decor/skirmish_markers/v001,game_factory/environment/ART-0041/v001,docs/SOURCE_ART_CATALOG.md,map_factory/metadata/source_art_index.json
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0041 (skirmish field tiles and cell markers) is delivered with a valid delivery manifest in a PR whose checks pass.
---
# Codex art: skirmish field tiles and cell markers

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Request: .agents/graphics/requests/ART-0041_skirmish_field_tiles.md.

## Production claim — 2026-11-11
Agent codex; branch codex/art-0041-skirmish-tiles. Six independent image_gen outputs:2checker-compatible grass tiles,1limestone rock,3translucent markers. Masters assets_hd/floor/skirmish_field/v001, assets_hd/props/skirmish_rock/v001 and assets_hd/decor/skirmish_markers/v001; provenance/QA game_factory/environment/ART-0041/v001. Native64x64 floor/markers and64x96rock; minima512square /512x768rock. Work remains isolated per TASK-0162. No character or gameplay rules modified. Seam/alpha/border readability must be checked at native scale; missing properties stay honest.

## Delivery evidence
Six selected independent sources,7image_gen calls,1retained earlier gold ring. Exact delivery PNGs/manifest.files present. RGB floor originals preserved and pixel-equal RGBA exports proven; source minima and >=4x native density pass. Whole-canvas64x64 exports for floor/markers, one-cell rock64x96 with bottom alignment. Native ring sampling phase2sourcepx clips only verified alpha0 margins and yields2px cardinal core strokes. Actual Godot checker/asset board plus original tactical_battle.tscn instance with in-memory rendering-only QA override; frozen Session and existing shape actors, red target demo not gameplay range logic. Sources/QA/provenance game_factory/environment/ART-0041/v001. No production scene/character/UI history/map/runtime edits or owner-main checkout writes. Next: integrate delivered native textures into the production renderer without changing Session rules.

Validation: python -u tools/run_tests.py --changed --timeout120 passed90/90groups, exit0. Dedicated prepare/verify audits checked6distinct RGBA masters/deliveries/native PNGs,2preserved RGB generation originals with exact RGB-byte equality, all size minima and>=4x density, one archived initial ring, and2actual Godot viewport captures. Markers have2px cardinal alpha128 core strokes; gold uses measured2sourcepx empty-margin export phase, no master repaint. All4AA/AB/BA/BB seam metrics below interior local differences; actual native checker/source scene images inspected without hard seam lines. Existing tactical_battle.tscn instantiated with rendering-only QA subclass, frozenSession, original circle actors; no gameplay/range/damage integration claimed. Source catalog143records/31HDgroups/zero unindexed PNGs and linked paths verified in assembled local context; prior PR179/182/185 snapshots not staged. Receipt45files verified. graphics_validation.py --changed exit0,0errors/warnings,0production PNGs covered for these masters; dedicated source audit provides verification. Test-index and whitespace checks passed. Godot4.7.2/ANGLE capture exit0; sandbox user:// log/shader-cache warnings nonfatal. No original battle scripts, maps, character/UI history, Golden Cyclone, generated main-only indexes or owner-main checkout files modified. Agent codex; built-in image_gen7calls; model/cost unknown.
