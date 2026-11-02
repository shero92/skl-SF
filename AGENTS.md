# Shared coding-agent contract

Applies to Codex, Claude Code and coding agents. Read this contract, then consult only the assigned task and relevant supporting instructions.

## سياسة الرسوم الدائمة — قرار المالك 2026-11-01

قبل أي عمل رسومي اقرأ [السياسة الموحدة](docs/GRAPHICS_PRODUCTION_POLICY.md). كل إطار أو عنصر قابل لإعادة الاستخدام يولد مستقلاً في ملفه؛ يمنع توليد عدة وضعيات في صورة واقتطاعها كأصول إنتاجية. Sprite Sheets مخرجات تجميع من الملفات الفردية فقط. تحفظ المصادر عالية الجودة والأصول المعتمدة وتراجع النسخ الجديدة قبل التفعيل. هذه السياسة تعلو على أي نص قديم متعارض.

## Agent roles and permissions (owner decision 2026-11-02; supersedes the 2026-10-31 amendment and the old "Codex must not code" rules)

Any agent may do any task the owner explicitly assigns to it; the model's identity alone is never a reason to refuse an owner-assigned task.
- **Codex Pro:** code, tests, scripts and automation configuration, plus graphics, plans, reports and task records.
- **Aider CLI:** coding tasks whose canonical `TASK-####` record says `agent: aider`, run unattended by `tools/aider_worker.py` (see `docs/AIDER_AUTOMATION.md`). Models: main `openai/gpt-6.1-sol`, weak `openai/gpt-6-sol`, API base `https://apimaster.ai/v1`. Aider must not generate images or touch approved image assets.
- **Claude Code:** tasks explicitly assigned to it (`agent: claude`) or requested by the owner in chat. Complex code is not escalated to Claude automatically.
- **Provenance:** record the real execution tool and underlying model (`Agent: aider` + model, `Agent: claude`, `Agent: codex`); never attribute one implementer's work to another.
- **Secrets:** API keys are read at run time from the owner's environment/secure store. Never copy them into the repo, task files, prompts, command lines or logs.
- **Unchanged protections:** Git/worktree isolation (branch per task, no push to main, no force push), preserve uncommitted owner changes, protected character/UI assets, approved art and map history.
- **Gates:** unattended Aider execution and the Windows Scheduled Task stay OFF in `.agents/planner/config.json` until activated by `tools/setup_aider_worker.ps1` after an API-key check. Owner approved a $10 spend cap for a 24-hour Aider plan on 2026-11-02 (`max_spend_usd`, enforced by the worker). Automatic merging stays OFF; the worker never merges.

## Scope and truth
- Work on environment art and Map Factory only. Characters, NPCs, gameplay, portraits, dialogue and UI are protected unless the owner explicitly approves a separate scope.
- Follow `INDEX.md` to locate files; read only relevant files and ranges. Do not bulk-read inventories.
- Git commits/PRs prove code changes; task records track status; catalog IDs prove registered assets. Never claim unreviewed art is approved.

## Tasks, branches and evidence
- Follow `.agents/workflows/TASKS.md`. Check task ownership/dependencies, claim one task, and use an isolated branch/worktree. Do not overlap active touches.
- Start and complete task receipts with `tools/agent_costs.py`; stage only task files and push task branches, never `main`. Missing usage/cost stays `unknown`. See `.agents/monitoring/README.md`.
- Before commits run `py -3 tools/run_tests.py --changed`; report actual checks, results, commit/PR and one next action. Preserve local user changes.
- Direct merges to `main` follow owner ADR-006 only after a verified, supervised end-to-end test (the Aider worker never merges). Infrastructure and planning changes use PRs. Do not set tasks `done` before reviewed/merged evidence. Generated indexes and dashboards are updated on `main` only.

## Graphics and map safety
- Owner authorizes assigned Codex/Claude Code environment-art production using local Blender (other assigned agents may take the producer role). Canonical workspace: `H:\shining force\pixel-art`; follow `.agents/workflows/GRAPHICS.md` for sources, outputs, manifests and review. Preserve published art and accepted HD assets W021/W022, A017/A018, D019, P023-P026. Owner visual approval remains required for the assembled room.
- Never alter character/UI art or use paid image services. Do not disable sandboxing or expand permissions.
- Preserve map history: patch the latest revision; never rewrite historical snapshots. Follow `map_factory/MAP_FACTORY_RULES.md` for map work. Preview scene: `scenes/map_factory_preview.tscn`.

## Tools and planning
- Use existing RTK hooks for useful human-readable shell output. Use `rtk bypass` when exact output is required, especially JSON/JSONL, manifests and machine-parsed `git --porcelain`; keep full failure logs locally.
- Keep the existing Godot MCP; use it only when the task needs Godot editor/runtime functions. Do not add duplicate MCP servers or change global tool settings for routine work.
- Follow `.agents/planner/PROMPT_RULES.md` and `tools/goal_task_factory.py` for planning. Approved goal steps and user requests remain distinct; do not invent evidence or approve a goal from tests alone.
- Read `.agents/roles/`, `.agents/graphics/` and other supporting docs only when the task needs them.
