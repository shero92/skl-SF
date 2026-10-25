# Development roadmap — milestones only

Milestones are not a second task-status board. Active tasks: [TASKS.md](TASKS.md). Graphics queue: [../graphics/QUEUE.md](../graphics/QUEUE.md).

## P0 — Multi-agent coordination
- One root `AGENTS.md` plus on-demand roles/workflows, stable task IDs, generated statuses and per-folder file indexes.
- Every requested graphic represented by one deduplicated request; no coding-agent image generation.
- Review PR checks on index/task/art ledgers.

## P1 — Reference baseline
- Preserve authentic Hero Room source image + hash in repo; link to next immutable map version.
- Obtain honest Godot-vs-reference screenshot comparison before treating a part as approved.

## P2 — Map perspective and compositing
- Fix 3/4 geometry, cliff thickness, stairs and connected walls.
- Verify world Y sorting, mounts, physical pivots and consistent sunlight shadows.

## P3 — Art production (graphics specialist only)
- Commission *missing* high-quality environmental sprite variants, including directional perspectives, from explicit ART requests.
- Artist delivery → independent QA → Godot integration. Never duplicate existing approved parts.

## P4 — Map navigation / release checks
- Complete wall/obstacle collision and provisional walk/fly/swim data.
- Run unit, Godot and artistic reviews before declaring a room approved.

**No gameplay-character/UI development in current scope.**
