---
id: TASK-0006
status: review
owner: chatgpt
branch: feat/local-goal-planner
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
- [ ] Supervised Windows dry run and first live planning PR verified.

## Evidence / handoff
- Changes: tools/local_planner.py, goal_task_factory.py, setup_local_planner.ps1,
  .agents/planner, agent_workflow.yml, generated indexes.
- Tests: Python unit and CI; actual local Windows OAuth unavailable remotely.
- PR: review required.
- Next: merge PR then install schedules on logged-in Windows.
