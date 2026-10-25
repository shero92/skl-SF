---
id: TASK-0004
status: review
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
- [ ] CI and manual workflow run verified; PR reviewed and merged.

## Evidence / handoff
- Changed files: tools/goal_task_factory.py, .agents/planner, workflow, tests and indexes.
- Tests: unit test and GitHub CI.
- PR: pending review.
- Next: review and merge after checks; configure your first explicit long-term goal.
