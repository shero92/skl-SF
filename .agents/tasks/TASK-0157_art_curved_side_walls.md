---
id: TASK-0157
status: blocked
owner: codex
agent: codex
priority: high
branch: codex/art-0044-0045-side-walls
depends_on: TASK-0148
issue: none
art_request: ART-0044
touches: .agents/tasks/TASK-0157_art_curved_side_walls.md,.agents/graphics/deliveries/ART-0044,.agents/graphics/deliveries/ART-0045
test: py -3 -m unittest discover -s tools/tests -p test_art_delivery.py
done_when: ART-0044 and ART-0045 are delivered as independent curved wall PNGs that match their reference crops (the east wall is its own drawing, not a mirror), each with a valid delivery manifest, in a PR whose checks pass.
---
# Codex art: west and east curved side walls

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- Requests: .agents/graphics/requests/ART-0044_hero_room_west_curved_side_wall.md and .agents/graphics/requests/ART-0045_hero_room_east_curved_side_wall.md.

## Production claim — 2026-11-11
Agent codex, branch codex/art-0044-0045-side-walls. Independent curved west/east sources and per-asset metadata/Godot reviews; no mirrored view or old-map edits. Sources under assets_hd/architecture/curved_west_side_wall/v001 and curved_east_side_wall/v001; metadata game_factory/environment/ART-0044/v001 and ART-0045/v001. Native proposals230x470 and236x540; requested4x source density will be measured, never fabricated/upscaled. Work remains in isolated worktree per TASK-0162.

## Verified technical blocker
West outputs877x1794 and878x1792 vs required920x1880; east829x1898 vs944x2160. Larger-native-resolution request/retry did not meet dimensions. Three candidate images, zero qualified production sources. No upscale, mirror or native-contract reduction. All candidates retained with metadata and real Godot evidence; draft PR will preserve work without claiming completion. Owner automatic visual approval recorded, but production_active=false and both requests remain requested / needs_regeneration. Next: obtain genuinely higher-resolution independently drawn sources that meet the existing4x native contract.

Evidence validation: python -u tools/run_tests.py --changed --timeout120 passed90/90groups, exit0. This validates project/evidence integrity only, NOT the failed4x art gate. Dedicated verify_candidates.py confirmed all source/candidate-copy/native/reference/capture hashes and asserted0qualified outputs, requested statuses, no production PNGs and no activation. Godot4.7.2/ANGLE actual candidate captures exited0. Source catalog136records /28HDgroups /zero unindexed source PNGs /all linked paths present, using local read-only PR179/182 context (not staged). Receipt34task files verified; test-index/whitespace checks passed. graphics_validation.py --changed exited0,0errors/warnings,0production PNGs covered because these are archived candidates. Observed dimensions877x1794,878x1792,829x1898 remain below required920x1880,920x1880,944x2160; all3failed measured4xqualification. No upscaling or hidden native-contract relaxation. No source/code from earlier tasks, runtime/map/character/UI/Golden Cyclone edits or owner-main writes. Godot user:// log/shader-cache warnings did not prevent capture. Task remains blocked; requests remain requested, production_active=false. Tool built-in image_gen,3calls, model/cost unknown.
