# Tools — narrow code search map

| Task | Script(s) |
| --- | --- |
| Create, clone, patch, validate maps | `map_factory_cli.py` |
| Build five passes and derived layers | `map_factory_layers.py` |
| Resolve 4 directions, pivots and mounted offsets | `map_factory_orientation.py` |
| Ingest source image and prepare draft | `prepare_map_reference.py` |
| Validate and process pending map edits | `process_map_intake.py`, `import_map_assets.py` |
| Verify image presence and map quality | `verify_map_assets.py`, `audit_room_assets.py`, `quality_guard.py` |
| Render real Godot preview | `capture_map_previews.gd`, `map_factory_godot_smoke.gd` |
| Test map behaviors | [tests/INDEX.md](tests/INDEX.md), `test_cardinal_map_blocks.gd` |
| Generate agent task/art queues and verify delivery hashes | `agent_workflow.py` |
| Grounded daily goal/task proposals and agent claims | `goal_task_factory.py` |
| Capture agent usage and produce per-task cost leaderboard | `agent_costs.py` |
| Generate directory inventories | `generate_project_indexes.py` |
| Curate/import historical asset sheets | other `generate_*`, `repaint_*`, `curate_*` scripts; not part of map-only task by default |

**Commands:** `python tools/map_factory_cli.py validate` and `python -m unittest discover -s tools/tests -p 'test_map*.py' -v`. For Godot screenshot checks read factory deployment docs. [All tool files](FILES.md).
