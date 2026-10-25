# Goal-driven daily task factory

The repository already uses AGENTS.md, TASK-####, agent_workflow.py and agent_costs.py.
This is a small orchestration layer on top of those canonical artifacts.

The GitHub Actions workflow daily_goal_task_factory.yml runs four times daily:
01:17, 07:17, 13:17 and 19:17 Europe/Berlin. It can also be started manually.
It inspects explicitly defined goal milestones, manual requests, and task states,
creates at most three new tasks/day, and regenerates indexes. No paid AI call
occurs during the pulse. Suggestions use auditable heuristics; no model performance
claims are made.

Source files:
- goals.json: your persistent goals, verification and approved milestone steps.
- PROMPT_RULES.md: how to turn a goal or instruction into a narrow task prompt.
- requests/REQ-*.json: exact user-requested bug/feature tasks and locations.
- ../tasks/TASK-####_*.md: each task is canonical for status and owner.
- daily/YYYY-MM-DD.md: current daily pulse and blockers.

The schedule writes to branch automation/daily-queue and opens a reviewable PR.
It does not automatically write to main, run Claude/Codex, or generate artwork.
Running the agents unattended needs configured runner, provider credentials,
permissions and explicit expense limits. Do not put subscription credentials
into a GitHub repository.

Completion: all linked tasks must be done with PR evidence AND final_verified=true
after a human actually checks the outcome. GitHub Actions then opens a single issue
assigned to shero92. Mobile/email notification depends on GitHub notification preferences.
GitHub may delay schedule runs; workflow_dispatch provides manual fallback.
GitHub Actions must be allowed to create PRs in repo Actions settings.

Windows PowerShell examples (run from repository root):

    py -3 tools/goal_task_factory.py pulse
    py -3 tools/goal_task_factory.py request --title "Fix wall turn" --problem "Observed misalignment" --file map_factory/scripts/room_factory.gd --done-when "Turn confirmed in Godot preview" --test "python -m unittest discover -s tools/tests -p test_map*.py"
    py -3 tools/goal_task_factory.py claim TASK-0004 --agent codex --branch feat/task-0004
    py -3 tools/goal_task_factory.py prompt TASK-0004
    py -3 tools/goal_task_factory.py completed

Run agent task tracking BEFORE a new session, and finish via agent_costs.py complete
on the task branch after tests. For goals with broad text only, first review
and fill the milestone steps once; never invent an implementation file/line.
