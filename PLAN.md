# skl-SF — ordered roadmap

This is a proposed execution order, not a claim tasks are complete. One independently reviewable PR per bounded unit of work.

## P0 — Agent collaboration and navigation
- [x] Define shared instruction entry points and locate current project state.
- [ ] Merge indexed navigation and automated inventory validation.
- [ ] Adopt isolated branches/worktrees per agent, PR checks and owner review.
**Done when:** a new agent can find a target file using two index hops, and regenerated inventories pass validation.

## P1 — Reference fidelity baseline (MAP ONLY)
- [ ] Commit the original user-supplied image in `map_factory/references/` (not a recreation).
- [ ] Attach real source path/SHA-256 to a **new** Hero Room version from latest; preserve immutable v0010.
- [ ] Capture Godot preview and produce at-scale source-versus-render comparison.
**Done when:** source/reference and screenshot are reproducible.

## P2 — Fix room geometry and depth
- [ ] Implement coherent 3/4 walls, stepped/cliff depths and transition placement.
- [ ] Verify pivots, occlusion/world-y-sort, mounts and independent shadow layers.
- [ ] Iterate on largest visual deviations using actual Godot renders.
**Done when:** visual reviewer signs off on layout and perspective improvements.

## P3 — Art directions and reusable assets
- [ ] Clean priority environment sprites, tile seams, clipping and alpha halos.
- [ ] Create true cardinal art variants for perspective props as needed (not rotated single views).
- [ ] Approve individual assets only after native-size visual QA.
**Done when:** requested facing variants exist and consistently render in Godot.

## P4 — Environment navigation & release gates
- [ ] Audit collisions and navigation clearance per environmental object and region.
- [ ] Strengthen PR test triggers and visual comparison reports.
- [ ] Only then move to new room archetypes; gameplay remains out of scope.
**Done when:** tests pass and environment metadata is reviewed; do not assert gameplay movement works.

## Working agreement
- Take one small task from a phase; record the observed result, command and remaining blockers in `STATUS.md` when it materially changes.
- Do not rewrite historical map snapshots or mark visual QA approved without a reviewer and verified reference.
