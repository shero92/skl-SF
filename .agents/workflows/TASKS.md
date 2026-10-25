# Canonical task workflow

**Source of truth for live status:** one `../tasks/TASK-####_*.md` file per task. The auto-generated `../project/TASKS.md` is only a tiny index; Git commits/PRs are the source of truth for what code actually changed. Keep `../project/PLAN.md` as milestones, not a duplicate checklist.

## Before starting
1. Check `../project/TASKS.md` for an active task, owner, dependency and any related GitHub Issue/PR.
2. Open only that task and the feature-specific files through the root/folder indexes.
3. If a task is already `in_progress` by another agent, do not redo it. Work in a separate Git branch/worktree. Name branch in the task record when claimed.
4. If an art request is required, first search the art queue/catalog, create/reuse one request, and set task `blocked` with that request ID.

## Cost receipts for Claude Code and Codex
- Start the TASK-#### tracker BEFORE a fresh agent session: `python3 tools/agent_costs.py start TASK-#### --agent claude|codex`.
- Before committing task code run `python3 tools/agent_costs.py finish`. Include the receipt and generated summaries in the same commit, with Task-ID and Agent commit trailers.
- Missing or unavailable cost remains unknown (null), not $0. Never commit local transcripts. Read `.agents/monitoring/README.md` for detailed procedure.

## States and completion
- `todo`: planned; `in_progress`: assigned and editing; `blocked`: waiting on something explicit; `review`: PR submitted; `done`: reviewed/merged and validated; `cancelled`: no longer needed.
- Update task body: actual changed file paths, test commands + outcomes, PR/commit link, reason for blocking, then **one next step**. Do not paste giant logs.
- Set `done` only after reviewed/merged evidence, not merely after writing code.
- Run `python tools/agent_workflow.py --write`; commit generated dashboards and index updates with the task.
- Use GitHub Issues/sub-issues for multi-person planning if useful; record the issue URL/number in the task file. Avoid a second divergent task status in Issues and MD.

## Adding a task
Copy `../templates/TASK.md`, select the next unoccupied `TASK-####` ID, keep frontmatter keys and short acceptance criteria. One task should produce one reviewable PR. Do not create many speculative tasks without an actual plan.
