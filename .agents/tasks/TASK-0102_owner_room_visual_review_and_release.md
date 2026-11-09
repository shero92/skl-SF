---
id: TASK-0102
status: review
owner: claude
agent: claude
priority: high
branch: claude/task-hygiene
depends_on: TASK-0101
issue: none
art_request: none
touches: map_factory/maps/hero_room_01/latest.json,map_factory/maps/hero_room_01/versions/v0014.json,map_factory/maps/hero_room_01/patches/v0014.json,map_factory/maps/index.json,docs/previews/map_factory_renders/hero_room_01_v0014.png,docs/previews/map_factory_renders/hero_room_01_v0014.json,docs/HERO_ROOM_20261103_VISUAL_TARGET.md
test: python tools/run_tests.py --all
done_when: Claude merges tested Aider results, publishes a new immutable version after v0013, performs a real Godot capture and side-by-side reference review, reports exact remaining visual gaps, and only marks the room visually approved with explicit owner approval.
estimate_minutes: 120
---
# Integrate and review the Hero Room against the new owner's photo

Reference: `docs/HERO_ROOM_20261103_VISUAL_TARGET.md`. Do not overwrite existing v0012/v0013 or cached render paths. The listed v0014 destinations are **expected if v0013 is latest**; inspect current version at execution time, and use the next free version if newer work exists. Update this task's `touches` if paths change before execution.

## Work
1. Review and merge the output PRs from TASK-0090–0101, including runner-dependent tasks in order. Verify each reported `done` commit landed on main; local Aider done alone is insufficient.
2. From a clean `main` checkout, apply versioned map patch from the tested blueprint generator and verify no preexisting revisions were overwritten.
3. Run Godot import and `python tools/run_tests.py --all`. Capture a real 1536×1024 room screenshot using TASK-0101 path; do not generate an imagined scene.
4. Compare target image to rendered room, side by side: ocean, central arch, connected three-sided ruins, bed/rug, study table/rug, compass, walls, stair descent, flowers/vines, lantern light, sea/cliff edges and contact shadows. Record each zone as matched/partial/missing and give actionable next steps.
5. Do **not** insert characters in Map Factory. Optionally create a second gameplay-only screenshot using existing approved Hero/Neru assets and mark as separate composition; no generated characters.
6. If the approved assets cannot reproduce a target feature, create *specific* ART requests for Codex image_gen and mark the feature blocked; do not substitute unrelated sprites.
7. Keep `visual_approval: false` until explicit owner inspection. Final report includes screenshots, number of PNG paths used, placements, PR/commit links, missing art and test results.
8. Keep Aider Worker, worktrees and the $10 cap undisturbed. Do not automatically update its runner during a live task.

## Acceptance
- User can clone `main` and reproduce the room in Godot with all registered assets present.
- Target composition is reviewed visually; passing test hashes or automatic checks is not called visual approval.

## Closure (Claude, 2026-11-09)
Real Godot captures exist for v0014 to v0017 with passing evidence gates (docs/previews/map_factory_renders/t0104_v0014, t0114_v0015, t0115_v0016, t0116_v0017, t0117_v0017). The gap table in docs/HERO_ROOM_20261103_VISUAL_TARGET.md was written for v0014; v0017 improves the walls, shadows and light but the connected walls, terrace edge, sea stacks and planters still need ART-0032..0035. visual_approval stays false until the owner reviews a render. Not marked done: only the owner can approve.
