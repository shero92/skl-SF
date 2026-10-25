# skl-SF — shared coding-agent contract

**Applies to Codex, Claude Code and all coding agents.** These are the only auto-loaded project instructions; open supporting files on demand.

1. **Scope:** environment / Map Factory only. Do NOT alter characters, NPC/player gameplay, portraits, dialogue or UI without a separate explicit new scope approval.
2. **Locate first:** `INDEX.md` → relevant folder `INDEX.md` → exact file/range. Read `.agents/INDEX.md` only when coordinating work or delegating graphics; never bulk-read all inventories.
3. **Track tasks:** follow `.agents/workflows/TASKS.md`. Check `.agents/project/TASKS.md` for current ownership/status before editing; claim one task and branch/worktree, avoid parallel edits to the same file. Update the task's own status and evidence, then regenerate dashboards.
4. **Graphics boundary (hard rule):** Codex/Claude Code MUST NOT generate, redraw, repaint, upscale, synthesize or replace production graphics or art with scripts, image tools or AI. Instead check the asset catalog and `.agents/graphics/QUEUE.md` for duplicates, then create a full art request using `.agents/workflows/GRAPHICS.md`. A graphics specialist creates the art. Coding agents may validate and integrate approved delivered files only.
5. **Truth:** Git commits and PRs prove changes, task files track progress, existing art IDs/catalog prove registered sprites. Do not claim a requested image or unapproved sprite is finished.
6. **Map safety:** follow `map_factory/MAP_FACTORY_RULES.md` for map tasks; load `MAP_FACTORY_WORKFLOW.md`, `LAYER_SCHEMA.md`, `FOUR_DIRECTION_BLOCKS.md`, or art rules only when relevant. Preserve map revisions; patch latest, never historical JSON snapshots. Godot preview is `scenes/map_factory_preview.tscn`.
7. **Completion:** run applicable tests, report actual commands/results, changed paths, PR/commit, blockers and one next task. Never claim visual approval without a genuine source-versus-Godot comparison and reviewer.
8. **Index maintenance:** when files change, run `python tools/generate_project_indexes.py --write` and `python tools/agent_workflow.py --write`; validate both with `--check`. Work on branches and use PR review, not direct main pushes.

Details only when needed: `.agents/roles/`, `.agents/workflows/`, `.agents/project/`, `.agents/graphics/`. Keep context concise.
