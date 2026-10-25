# Prompt construction rules — Claude Code and Codex

Treat each TASK-#### record as the task-specific prompt, not repeated giant chat instructions.
Adopt goal/context/constraints/done-when and GitLab-style workplan dependencies.

1. State an observable outcome, not "make it better".
2. Ground in evidence: exact error text, failing test or verified code. Never invent line numbers.
3. Locate using INDEX.md. Aim for 1-3 relevant source files only.
4. Reference AGENTS.md for stable policy; do not paste it into every prompt.
5. List non-goals, acceptance checks and the test command. Separate code from art requests.
6. For an ambiguous report create an investigation task first, not an invented fix.
7. Break an approved long goal into 1-3 bounded tasks/day, with dependencies.
8. Suggest Codex for bounded code/tests; Claude for architecture/investigation. This is a
   routing heuristic, not a claim of superiority. Improve it using measured receipts and rework.
9. User manual requests outrank ordinary goal milestones, without losing original intent.
10. Claim a task and worktree before new agent session. Track tokens; stage only task files.
11. Require real tests, task evidence, cost receipt, PR. Never push to main automatically.
12. Keep budget hints as guidance, not as guarantees; stop rather than consume unlimited context.

Minimal prompt components: Goal | observed evidence | exact path/verified line | non-goals |
test command | done-when | token budget.

To submit a manual bug/feature request, use the request command documented in README.md.
To define a long goal, edit goals.json and have a human or planner agent review the
milestone steps ONCE. Each step requires stable key, title, problem, file, done_when,
test, kind, priority, with optional depends_on, agent and line. Then set status=active.
Natural language by itself cannot be deterministically decomposed into grounded code tasks.

A goal-completion notification requires all named task_ids DONE with PR links and
final_verified=true, set only after checking actual end-to-end acceptance evidence.
