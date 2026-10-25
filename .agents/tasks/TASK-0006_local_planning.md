---
id: TASK-0006
status: done
owner: chatgpt
branch: feat/local-goal-planner
agent: codex
touches: tools/local_planner.py,tools/goal_task_factory.py,.agents/planner/
test: python -m unittest discover -s tools/tests -p test_local_planner.py
done_when: Local scheduled planner passes repository checks
started_at: unknown
cost_usd: unknown
depends_on: TASK-0005
issue: none
art_request: none
---
# Replace GitHub planning with local Windows subscription-only analysis

**Goal:** Alternate four bounded read-only planning runs/day on the owner's PC.

## Acceptance
- [x] CLI flags taken from the owner's actual local help output, no API keys.
- [x] Text-only planning context, JSON-schema proposal, deterministic scope checks.
- [x] Git SHA/digest skip, quota cooldown, no repeated CLI retries.
- [x] Four-times-daily configurable Task Scheduler setup and uninstall.
- [x] Planning PR safe-path and CI gate, no cloud AI.
- [x] PR #7 merged with all three CI checks; supervised Windows dry run remains outstanding.

## Evidence / handoff
- Changes: tools/local_planner.py, goal_task_factory.py, setup_local_planner.ps1,
  .agents/planner, agent_workflow.yml, generated indexes.
- Tests: Python unit and CI; actual local Windows OAuth unavailable remotely.
- PR: https://github.com/shero92/skl-SF/pull/7 (merged).
- Next: merge PR then install schedules on logged-in Windows.
