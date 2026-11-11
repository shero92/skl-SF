---
id: TASK-0156
status: review
owner: codex
agent: codex
priority: high
branch: codex/art-0042-0043-rear-walls
depends_on: TASK-0148
issue: none
art_request: ART-0042
touches: .agents/tasks/TASK-0156_art_rear_walls.md,.agents/graphics/deliveries/ART-0042,.agents/graphics/deliveries/ART-0043
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0042 and ART-0043 are delivered as independent PNGs that match their reference crops, each with a delivery manifest listing request_id and files (path and sha256), in a PR whose checks pass.
---
# Codex art: rear-left wall with window and rear-right wall with arched door niche

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0042_hero_room_rear_left_ruined_wall_window.md and .agents/graphics/requests/ART-0043_hero_room_rear_right_wall_arched_door_niche.md.
- Draw from the reference crop named in each request; one piece per file; no lanterns, plants or banners baked in.

## Production claim — 2026-11-11
Agent: codex. Branch codex/art-0042-0043-rear-walls. Two independent clean wall pieces, no pasted decorations. Masters assets_hd/architecture/rear_left_window_wall/v001 and rear_right_door_niche/v001; per-request provenance/QA under game_factory/environment/ART-0042/v001 and ART-0043/v001. Master canvas minimum1880x800 and1240x1000 respectively. Work stays in this isolated worktree under H:/shining force/skl-SF/.worktrees; no uncommitted art copied into the owner main checkout (TASK-0162). Owner automatic visual approval applies, technical calibration remains separate.

## Delivered source evidence
Two selected RGBA masters, five independent image_gen calls, three retained nonselected attempts. ART0042 master1921x819 / native470x200, enclosed transparent square aperture about43.3x44native maximum low-alpha bounds. ART0043 master1397x1126 / native310x250; approximately8courses, door-frame manual bounds about74x105native. Both master minima and4x density passed; sources never upscaled or cropped from a sheet. Requests delivered only; owner automatic visual approval recorded, collision/sockets/room placement remain uncalibrated. Actual Godot1x/2x source/reference comparison captures and verified source/native/delivery/reference/attempt hashes. Full provenance, reusable QA scripts, and delivery receipt under game_factory/environment/rear_walls_20261111. No root main copy or runtime/map edits. Catalog133records includes local pending ART0040 metadata snapshot from PR179 (not re-staged); merge PR179 before combined checkout catalog audit. Next: integrate wall endpoints/collisions and capture a new immutable room revision.

Validation: python -u tools/run_tests.py --changed --timeout 120 passed89/89groups, exit0. Godot4.7.2/ANGLE actual source/reference captures exited0 for bothARTs; verify_delivery.py confirmed source/delivery/native/reference/attempt and viewport hashes. Source-art catalog check passed133records /26HDgroups /zero unindexed source PNGs /all linked item paths present, with pending ART0040 audit context from PR179. Delivery receipt44files verified; master minima and >=4x source density passed. graphics_validation.py --changed exited0, zero errors/warnings but covers0production PNGs because masters lie outside its production scope; dedicated source checks cover all five generated source PNGs. Test-index and whitespace checks passed. Local Godot log/shader-cache and QA raw-image export warnings did not prevent capture; review script is a local source inspector, not export runtime code. No image, metadata or code from ART0040 staged. No owner-main checkout writes, old map/runtime/character/UI/Golden Cyclone edits or generated main-only indexes. Agent codex; tool built-in image_gen; model/cost unknown.
