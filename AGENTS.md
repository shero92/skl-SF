# skl-SF â€” shared coding-agent contract

**Applies to Codex, Claude Code and all coding agents.** These are the only auto-loaded project instructions; open supporting files on demand.

## سياسة الرسوم الدائمة — قرار المالك 2026-11-01

قبل أي عمل رسومي اقرأ [السياسة الموحدة](docs/GRAPHICS_PRODUCTION_POLICY.md). كل إطار أو عنصر قابل لإعادة الاستخدام يولد مستقلاً في ملفه؛ يمنع توليد عدة وضعيات في صورة واقتطاعها كأصول إنتاجية. Sprite Sheets مخرجات تجميع من الملفات الفردية فقط. تحفظ المصادر عالية الجودة والأصول المعتمدة وتراجع النسخ الجديدة قبل التفعيل. هذه السياسة تعلو على أي نص قديم متعارض، ولا تجيز كتابة الكود لـCodex أو تغيير نطاق العمل دون طلب المالك.

طلب المالك الحالي يجيز إنتاج رسوم Hero Golden Cyclone ومراجعة أسلوب الهجوم. Codex للرسوم والتحليل والتقارير فقط، دون كود أو اختبارات أو إعدادات أتمتة؛ لا تشغيل Aider أو Claude أو خدمات صور خارجية في هذه المهمة.

## Owner responsibility amendment — 2026-10-31

This amendment supersedes older producer/coding permissions wherever they conflict.
- Codex must NOT write or modify code, scripts, tests, or automation configuration. Its role is analysis, reports, task records, image/asset generation and visual review. Creating task/report documents does not authorize implementing their code.
- Ordinary coding tasks belong to Aider. Only ready tasks explicitly assigned to Aider may be picked up automatically, after dependency checks.
- Claude Code handles complex coding only after the owner explicitly asks Codex to create a Claude Code task. Codex may recommend Claude with a reason, but must not create, dispatch or escalate a task to Claude implicitly.
- Aider must not generate images or modify approved image assets. Different implementers' changes must not be attributed to Codex.
- The requested Aider watcher is NOT implemented or enabled by this amendment. Existing disabled automation stays disabled until the responsible coding agent implements and verifies the integration with a supervised end-to-end test.
- Keep the existing Aider model selection (`openai/gpt-4o`, weak model `gpt-4o-mini`). The owner wants continuous processing of eligible tasks, not automatic provider/model changes. Never copy credentials into task files or reports.
- See `docs/PROJECT_STATUS_2026-10-31_AND_AIDER_PLAN.md` for the dated evidence and pending implementation. No Claude task is authorized merely by this reference.

1. **Scope:** environment / Map Factory only. Do NOT alter characters, NPC/player gameplay, portraits, dialogue or UI without a separate explicit new scope approval.
2. **Locate first:** `INDEX.md` â†’ relevant folder `INDEX.md` â†’ exact file/range. Read `.agents/INDEX.md` only when coordinating work or delegating graphics; never bulk-read all inventories.
3. **Track tasks:** follow `.agents/workflows/TASKS.md`. Check `.agents/project/TASKS.md` for current ownership/status before editing; claim one task and branch/worktree, avoid parallel edits to the same file. Update the task's own status and evidence, then regenerate dashboards.
4. **Graphics production (owner decision 2026-10-28):** Codex and Claude Code may both take the environment graphics producer role for an assigned TASK + existing/new deduplicated ART request. They may write and run local Blender scripts to model, render and regenerate reusable pixel-art environment blocks. The authorized external graphics workspace and asset destination is `H:\shining force\pixel-art`; use task/request-specific versioned subfolders for `.blend` sources, render PNGs, shadows, masters and manifests. Builders/specs remain reproducible source in `tools/blender/` and `tools/blender/specs/`; independent workspace files may also be saved with their task provenance. Repository deliveries/candidate renders remain valid staging locations when a helper requires repository-relative paths; retain the canonical asset copy in the external workspace and link its exact path/hash in the handoff. This authorization covers Blender, Python orchestration/QA and Godot room captures; no external image-generation service is required. Do not downgrade or overwrite the nine accepted HD sprites W021/W022/A017/A018/D019/P023-P026, published assets or map history. Outputs remain unapproved until owner room comparison approval; unattended workers never auto-merge art. No character/UI/gameplay art or new paid services.
5. **Truth:** Git commits and PRs prove changes, task files track progress, existing art IDs/catalog prove registered sprites. Do not claim a requested image or unapproved sprite is finished.
6. **Map safety:** follow `map_factory/MAP_FACTORY_RULES.md` for map tasks; load `MAP_FACTORY_WORKFLOW.md`, `LAYER_SCHEMA.md`, `FOUR_DIRECTION_BLOCKS.md`, or art rules only when relevant. Preserve map revisions; patch latest, never historical JSON snapshots. Godot preview is `scenes/map_factory_preview.tscn`.
7. **Completion:** run applicable tests, report actual commands/results, changed paths, PR/commit, blockers and one next task. Never claim visual approval without a genuine source-versus-Godot comparison and reviewer.
8. **Mandatory task token receipts and push:** Every Claude Code/Codex coding task must begin tracking with `py -3 tools/agent_costs.py start TASK-#### --agent claude|codex` (use `python3` on Linux), before a fresh agent session. As the finishing agent: complete changes and tests, stage **only intended task files** with `git add <paths>`, and run `py -3 tools/agent_costs.py complete --message "feat: task description" --push`. This creates the token/cost JSON receipt, commits it and the leaderboard **with task code**, adds measured Token/Cost trailers, and pushes the **task branch**. Never push to main. Codex `exec --json` sessions should import usage with `import-codex` first. If collection fails, record unknown instead of inventing tokens/cost. The final response must link the actual pushed commit/PR. See `.agents/monitoring/README.md`. Separate worktrees for simultaneous agents. Under local runner automation use `complete --message ... --no-summary` (no push) so the runner serially merges the receipt/code into main and then regenerates summaries on main.
9. **Main-only generated indexes and direct merge (owner ADR-006):** Each coding task uses an isolated branch + worktree. Claimed paths must not overlap; agents test/rebase before sequential main merges and run verification on main afterward, reverting and blocking on failures. Do not generate INDEX.md/FILES.md/TASKS.md/ACTIVE.md in task worktrees; regenerate only on main after merge. Automated direct code merges require a reviewed, successful supervised end-to-end runner test before execution is enabled. Agent plans may auto-merge only with successful CI and a strict path allowlist. GitHub Actions do not run AI or mutate game assets.

9a. **Index maintenance:** coding agents NEVER modify generated dashboards or indexes in task worktrees. The local runner regenerates them exclusively on main after each claim/merge and validates output. Infrastructure changes use a PR; code tasks may merge directly only after full tests and the owner-approved supervised launch.

10. **Agent provenance:** Commit trailers must state the actual execution agent as `Agent: claude`, `Agent: codex`, or `Agent: chatgpt`. Never use `Agent: assistant`. Never invent cost or usage: store unknown when measurement is unavailable.

11. **Graphics access and tool availability (owner decision 2026-10-28):** Assigned Codex/Claude graphics sessions may read/write environment build sources and outputs in `H:\shining force\pixel-art` and use the required local Blender/Python/Godot commands. Do not treat a graphics producer as an image-free coding-only session or block it merely because art is needed. Scripted QA checks individual pieces, headers, alpha, manifests, anchors and reference hashes; agent visual review remains limited to the final assembled-room comparison sheet. Characters, portraits and UI stay closed. Ordinary code-only sessions retain image-free isolation. The owner explicitly authorizes this scoped repository permission update; it does not authorize agents to disable sandboxing, expand unrelated paths, or change permissions again without owner direction. Legacy task boilerplate such as "never generate artwork" applies to ordinary code-only work, not to explicitly assigned Blender graphics production authorized by this rule. File settings cannot override tool exclusions imposed by an existing launcher or managed host; if that boundary blocks production, record the exact blocker and do not claim the task ran.

12. **Goal/task automation:** User-specified tasks enter as .agents/planner/requests/REQ-*.json via tools/goal_task_factory.py request. Long goals and accepted step specifications belong in .agents/planner/goals.json; follow PROMPT_RULES.md. Four LOCAL Windows scans propose tasks on review PRs, refresh indexes, and suggest agents; the deterministic milestone pulse creates every ready step (owner decision 2026-10-26: `max_new_tasks_per_day: null` in .agents/planner/config.json) and runners keep working until no task is eligible or the agent's usage limit is reached; cloud GitHub Actions must not run planning or AI. Claim tasks before coding. The scanner never generates production art or directly pushes to main. Verified goal completion produces a GitHub Issue notification.

Before any commit/merge run: py -3 tools/run_tests.py --changed

Details only when needed: `.agents/roles/`, `.agents/workflows/`, `.agents/project/`, `.agents/graphics/`. Keep context concise.

## Aider execution authorization — 2026-11-02

Owner authorization:
- Codex Pro may continue producing approved graphics, plans,
  reports, and task definitions.
- Codex CLI remains restricted from general coding tasks.
- Coding tasks explicitly assigned to Aider may be implemented
  through Aider CLI using openai/gpt-6-sol.
- This authorization applies to TASK-0071.
- The execution tool must be recorded truthfully as Aider CLI;
  the underlying model must also be recorded truthfully.
- Preserve existing uncommitted changes and approved artwork.
- Use isolated Git worktrees for coding tasks.
- Keep unattended execution, startup registration and automatic
  merging disabled until supervised testing succeeds.
