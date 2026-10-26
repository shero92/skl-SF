---
id: TASK-0012
status: review
owner: codex
branch: fix/planner-generated-checks
agent: codex
touches: tools/runner_safety.py,tools/agent_runner.py,tools/agent_workflow.py,tools/generate_project_indexes.py,tools/agent_costs.py,tools/local_planner.py,tools/tests/test_local_planner.py,tools/tests/test_agent_workflow.py,tools/tests/test_project_indexes.py,tools/tests/test_agent_costs.py,tools/tests/test_parallel_safety.py,tools/tests/test_runner_main_clean.py,.github/workflows/agent_workflow.yml,.github/workflows/project_indexes.yml,.github/workflows/agent_costs.yml
test: py -3 -m unittest discover -s tools/tests -p test_local_planner.py
done_when: PR source-only validation is read-only, rejects generated edits and invalid records; strict main checks stay enabled; local planner refreshes main-only outputs after successful merge.
started_at: 2026-10-26T12:25:45.831047+01:00
depends_on: TASK-0010
issue: none
art_request: none
---
# Reconcile planning PR checks with main-only generated outputs

**Source:** request:REQ-7175675bbea0

## Evidence / handoff
- PR 17 fails agent_workflow --check and generate_project_indexes --check on intentionally stale generated outputs.
- Scope: planning and validation infrastructure only. No production images opened or changed.
- Tests: py -3 tools/run_tests.py --changed --kind python: 21/21 passed in the image-free task worktree.
- Regression evidence: PR checks accept stale inherited dashboards without writes, reject generated output edits (unstaged/staged/committed/renamed/untracked), reject invalid source records and missing base refs; planner refresh runs only after allowed successful merges and takes the main-merge lock.
- Godot tests: not rerun for this infrastructure-only change; automatic approval review rejected restoring production art into the coding worktree.
- Changed paths: tools/runner_safety.py, tools/agent_runner.py, tools/local_planner.py, tools/agent_workflow.py, tools/generate_project_indexes.py, tools/agent_costs.py; three GitHub validation workflows and three regression-test files.
- Generated dashboards/indexes: unchanged in this task worktree.
- Next: review and merge this infrastructure PR, refresh planning PR 17, then claim TASK-0011 for ART request records.
