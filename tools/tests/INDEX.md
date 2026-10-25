# Map-factory Python tests

- `test_parallel_safety.py`: task touch isolation, anti-art boundaries, no-code-run default, rollback guard, goal costs.
- `test_goal_task_factory.py`: evidence, deduplication, manual requests, agent routing, claim safeguards.
- `test_map_factory.py`: baseline versioning/factory operations.
- `test_map_cardinal.py`: four directions, sprite selection and mounted offsets.
- `test_map_layers.py`: five-layer composition and block mount rules.
- `test_map_intake.py`, `test_map_reference.py`: intake, source images and version checks.
- `test_map_navigation.py`: traversal metadata validation.
- `test_map_floor_geometry.py`, `test_map_floor_style.py`: floor geometry and tiling.
- `test_map_templates.py`: map templates and presets.

Run: `python -m unittest discover -s tools/tests -p 'test_map*.py' -v`. Do not assume this certifies artistic similarity. [Full file listing](FILES.md).
