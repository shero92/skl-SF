# Canonical task workflow

**Source of truth for live status:** one `../tasks/TASK-####_*.md` file per task. The auto-generated `../project/TASKS.md` is only a tiny index; Git commits/PRs are the source of truth for what code actually changed. Keep `../project/PLAN.md` as milestones, not a duplicate checklist.

## Long goals and explicit user prompts
- Follow .agents/planner/PROMPT_RULES.md: narrow scope, evidence, exact file and verified line, tests and acceptance criteria.
- A specific user bug/feature becomes a request using goal_task_factory.py request; requests outrank general goals.
- Long goals are recorded in .agents/planner/goals.json with approved steps. Scheduled analysis runs 4/day and proposes task files via PR, not production code.
- Claim a task before starting a new Claude/Codex session. Suggested agent routing is a heuristic, not a measured quality claim.

## Before starting
1. Check `../project/TASKS.md` for an active task, owner, dependency and any related GitHub Issue/PR.
2. Open only that task and the feature-specific files through the root/folder indexes.
3. If a task is already `in_progress` by another agent, do not redo it. Work in a separate Git branch/worktree. Name branch in the task record when claimed.
4. If an art request is required, first search the art queue/catalog, create/reuse one request, and set task `blocked` with that request ID.

## Mandatory Claude/Codex token receipts for task commits
- Start tracking a real `TASK-####` before beginning a fresh session: `py -3 tools/agent_costs.py start TASK-#### --agent claude|codex` (use `python3` on Linux).
- After finishing work and tests, import Codex JSONL usage if using `codex exec --json`, then stage **only intended task code/evidence** with `git add path1 path2`.
- The finishing agent MUST run `py -3 tools/agent_costs.py complete --message "feat: ..." --push`. It snapshots measured tokens/cost, commits receipt + leaderboard along with staged work, includes Task-ID/Agent/Tokens-Input/Tokens-Output/Tokens-Cached-Input/Tokens-Reasoning/Cost-USD/Cost-Receipt trailers and pushes to the task branch. Never push directly to main.
- Missing metrics remain unknown (not $0), and API-equivalent estimates are not subscription bills. Logs and raw transcripts stay local. See `.agents/monitoring/README.md`.

## States and completion
- `todo`: planned; `in_progress`: assigned and editing; `blocked`: waiting on something explicit; `review`: PR submitted; `done`: reviewed/merged and validated; `cancelled`: no longer needed.
- Update task body: actual changed file paths, test commands + outcomes, PR/commit link, reason for blocking, then **one next step**. Do not paste giant logs.
- Set `done` only after reviewed/merged evidence, not merely after writing code.
- Run `python tools/agent_workflow.py --write`; commit generated dashboards and index updates with the task.
- Use GitHub Issues/sub-issues for multi-person planning if useful; record the issue URL/number in the task file. Avoid a second divergent task status in Issues and MD.

## Adding a task
Copy `../templates/TASK.md`, select the next unoccupied `TASK-####` ID, keep frontmatter keys and short acceptance criteria. One task should produce one reviewable PR. Do not create many speculative tasks without an actual plan.
