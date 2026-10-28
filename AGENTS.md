# Shared coding-agent contract

Applies to Codex, Claude Code and coding agents. Read this contract, then consult only the assigned task and relevant supporting instructions.

## Scope and truth
- Work on environment art and Map Factory only. Characters, NPCs, gameplay, portraits, dialogue and UI are protected unless the owner explicitly approves a separate scope.
- Follow `INDEX.md` to locate files; read only relevant files and ranges. Do not bulk-read inventories.
- Git commits/PRs prove code changes; task records track status; catalog IDs prove registered assets. Never claim unreviewed art is approved.

## Tasks, branches and evidence
- Follow `.agents/workflows/TASKS.md`. Check task ownership/dependencies, claim one task, and use an isolated branch/worktree. Do not overlap active touches.
- Start and complete task receipts with `tools/agent_costs.py`; stage only task files and push task branches, never `main`. Missing usage/cost stays `unknown`. See `.agents/monitoring/README.md`.
- Before commits run `py -3 tools/run_tests.py --changed`; report actual checks, results, commit/PR and one next action. Preserve local user changes.
- Infrastructure and planning changes use PRs. Do not set tasks `done` before reviewed/merged evidence. Generated indexes and dashboards are updated on `main` only.

## Graphics and map safety
- Owner authorizes assigned Codex/Claude environment-art production using local Blender. Canonical workspace: `H:\shining force\pixel-art`; follow `.agents/workflows/GRAPHICS.md` for sources, outputs, manifests and review. Preserve published art and accepted HD assets W021/W022, A017/A018, D019, P023-P026. Owner visual approval remains required for the assembled room.
- Never alter character/UI art or use paid image services. Do not disable sandboxing or expand permissions.
- Preserve map history: patch the latest revision; never rewrite historical snapshots. Follow `map_factory/MAP_FACTORY_RULES.md` for map work. Preview scene: `scenes/map_factory_preview.tscn`.

## Tools and planning
- Use existing RTK hooks for useful human-readable shell output. Use `rtk bypass` when exact output is required, especially JSON/JSONL, manifests and machine-parsed `git --porcelain`; keep full failure logs locally.
- Keep the existing Godot MCP; use it only when the task needs Godot editor/runtime functions. Do not add duplicate MCP servers or change global tool settings for routine work.
- Follow `.agents/planner/PROMPT_RULES.md` and `tools/goal_task_factory.py` for planning. Approved goal steps and user requests remain distinct; do not invent evidence or approve a goal from tests alone.
- Read `.agents/roles/`, `.agents/graphics/` and other supporting docs only when the task needs them.
