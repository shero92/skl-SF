---
name: goal-task-factory
description: Turn a user's long-term Map Factory objective or precise bug report into a small, grounded, cost-aware goal/task plan. Use when asked to plan roadmap tasks, optimize agent prompts, or enter explicit user instructions into the daily task queue. Do not use for generating production art or for silently implementing code.
---

1. Read root AGENTS.md and .agents/planner/PROMPT_RULES.md.
2. For long goals, read only .agents/project/PLAN.md and necessary INDEX.md entries.
   Check actual code/test evidence before claiming a file path or exact line.
3. Draft an outcome, measurable verification, constraints and ordered small
   steps in .agents/planner/goals.json. Each step needs stable key, title, problem,
   file, done_when, test, kind, priority. Use depends_on only when grounded.
4. For explicit user bug/fix requests, use tools/goal_task_factory.py request;
   preserve the exact request and avoid making up evidence or code locations.
5. Leave a new long goal in status=draft for user review. Never set
   final_verified=true without actual reviewer-confirmed end-to-end evidence.
6. The user or approved task activates the goal with status=active. Later
   scheduled pulses create up to 3 tasks/day from the reviewed step plan.
7. Propose Codex for targeted code/tests, Claude for ambiguous investigation,
   and an art specialist for requested production sprites. Rules are heuristics,
   not assertions of quality. Use actual per-task receipts to improve routing.
8. Do not execute coding tasks, push to main, expose secrets or create
   fictional screenshots. After changing planning sources, regenerate indexes
   and canonical task boards, run validations, and open a reviewable PR.
9. Keep the final response short: goal, why, steps, blockers, proposed cost
   guardrails, and where to approve it.
