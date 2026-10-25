# skl-SF — project navigation (START HERE)

**Do not read the entire repository.** Pick the smallest matching area below, open its `INDEX.md`, then inspect only the listed files/functions. For an exhaustive direct file listing use that directory's generated `FILES.md`. An index is a location hint, not proof of runtime behavior.

| Task request / feature | Go here first | Then inspect |
| --- | --- | --- |
| Map factory design, JSON contracts, layer ordering | [map_factory/INDEX.md](map_factory/INDEX.md) | `map_factory/MAP_FACTORY_RULES.md`, targeted workflow docs |
| Create/clone/patch a room | [map_factory/INDEX.md](map_factory/INDEX.md) | `tools/map_factory_cli.py`, `map_factory/maps/index.json` |
| Hero Room version, placement and fidelity | [map_factory/maps/INDEX.md](map_factory/maps/INDEX.md) | `hero_room_01/latest.json`, `docs/MAP_FACTORY_REFERENCE_DIAGNOSIS.md` |
| Add/find a sprite, PNG or reusable block ID | [map_factory/parts/INDEX.md](map_factory/parts/INDEX.md) | `map_factory/metadata/asset_index.json` (filter by ID) |
| Four-facing objects / perspective variants | [map_factory/INDEX.md](map_factory/INDEX.md) | `FOUR_DIRECTION_BLOCKS.md`, `tools/map_factory_orientation.py` |
| Shadows, sorting, collisions, map rendering | [map_factory/scripts/INDEX.md](map_factory/scripts/INDEX.md) | `room_factory.gd`, `shadow_factory.gd`, layer docs |
| Import reference image / pending job | [map_factory/intake/INDEX.md](map_factory/intake/INDEX.md) | `tools/prepare_map_reference.py`, `tools/process_map_intake.py` |
| Godot-only map preview, camera, runtime | [scenes/INDEX.md](scenes/INDEX.md) | `map_factory_preview.gd`, `map_factory_preview.tscn` |
| Python map tests / tools | [tools/INDEX.md](tools/INDEX.md) | `tools/tests/INDEX.md` |
| Automated GitHub validation | [.github/INDEX.md](.github/INDEX.md) | `.github/workflows/INDEX.md` |
| Art direction, visual QA and historical reviews | [docs/INDEX.md](docs/INDEX.md) | relevant review/quality policy |
| Project constraints / milestones / current progress | [Project files](.agents/project/INDEX.md) | refer only when relevant |

## Shared multi-agent coordination
- [Agent collaboration, task handoffs and graphics queue](.agents/INDEX.md): roles, task records, stage-gated specialist graphics requests and project status.
- [Project roadmap and handoff](.agents/project/INDEX.md): PROJECT, PLAN, STATUS, generated TASKS, CHANGELOG and DECISIONS.
- Root `AGENTS.md` is the **only** agent instruction file at root; the project has no root `CLAUDE.md` for current Claude Code v2.1.277+.

## Major directories
- [.agents/](.agents/INDEX.md): on-demand agent instructions, live task records and specialist graphics.
- [map_factory/](map_factory/INDEX.md): source assets, factory rules, JSON map snapshots and Godot renderers.
- [tools/](tools/INDEX.md): builders, audits and tests.
- [scenes/](scenes/INDEX.md): runtime/preview GDScript.
- [docs/](docs/INDEX.md): art references and QA evidence.
- [.github/](.github/INDEX.md): GitHub Actions.
- [Full root file inventory](FILES.md).

## Search recipe
1. Navigate this table to the relevant folder.
2. Consult that folder's `INDEX.md` for responsibilities, then its `FILES.md` for actual filenames.
3. Search narrowly, e.g. `rg -n "orientation_mode" tools/map_factory_orientation.py map_factory/scripts/`.
4. Read exact code ranges rather than printing all large JSONs, all test files or the whole sprite catalog.
5. Confirm source/version via `map_factory/maps/index.json` and current catalog; only edit the needed files.
