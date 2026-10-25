---
id: TASK-0004
status: done
owner: coding-agent
branch: feat/daily-goal-task-factory
depends_on: TASK-0003
issue: none
art_request: none
---
# Add four-times-daily goal planning and prompt standards

**Goal:** Create grounded tasks from approved long-goal steps and exact manual requests.

## Acceptance
- [x] Long goal schema and prompt-writing rules.
- [x] Manual requests, priority, routing, deduplication, low token budgets.
- [x] Four-times-daily GitHub Actions proposal PR and index regeneration.
- [x] Verified completed-goal notification via assigned GitHub Issue.
- [x] PR #5 merged and CI passed; 4x cloud planning now superseded by local-only design.

## Evidence / handoff
- Changed files: tools/goal_task_factory.py, .agents/planner, workflow, tests and indexes.
- Tests: unit test and GitHub CI.
- PR: https://github.com/shero92/skl-SF/pull/5 (merged).
- Next: implement verified local planning to replace the disabled cloud schedule.
