---
id: TASK-0010
status: review
owner: codex
branch: fix/planner-milestone-pulse
agent: codex
touches: tools/runner_safety.py,tools/goal_task_factory.py,tools/local_planner.py,tools/tests/test_goal_task_factory.py,tools/tests/test_local_planner.py,tools/tests/test_parallel_safety.py
test: py -3 tools/run_tests.py --all
done_when: Request records pass guarded validation and approved goal steps create tasks before AI, including skip runs.
started_at: 2026-10-26T12:05:32.387574+01:00
depends_on: none
issue: none
art_request: none
---
# Fix planner request records and deterministic milestone pulse

**Source:** request:REQ-a9695420d495

## Evidence / handoff
- Requested fix: planner run 20261026-120001-claude rejected request records; local planner never invokes pulse.
- Tests: py -3 tools/run_tests.py --changed passed 5/5 suites; full suite required on main after merge.
- Changed paths: tools/goal_task_factory.py, tools/local_planner.py, tools/runner_safety.py and their three unit-test files.
- Execution agent: codex; metrics remain unknown unless captured.
- Next: validate full suite on main and run the requested Claude planner once.
