# Active GitHub Actions — validation and notification only

| Purpose | Workflow |
| --- | --- |
| Verified long-goal GitHub Issue notification | `daily_goal_task_factory.yml` (no planner/AI runs) |
| Godot parser and import verification | `godot_validate.yml` |
| Map version checks and tests | `validate_map_factory.yml` |
| Godot map smoke checks | `map_factory_godot_smoke.yml` |
| Task/art schema and byte-identical planning skills | `agent_workflow.yml` |
| Agent token receipt checks | `agent_costs.yml` |
| Project index verification | `project_indexes.yml` |
| PNG quality regression guard | `quality_guard.yml` |

All 21 cloud write-back / production art workflows have been archived in [workflows-disabled/](../workflows-disabled/README.md). No active Action commits or generates art, maps, task files or screenshots.
