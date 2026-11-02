# Repository consolidation report - 2026-11-02

Scope: audit every local/remote branch, worktree, open PR and uncommitted file of `skl-SF`, preserve all unsaved work, merge validated work into `main`. Nothing was reset, cleaned, force-pushed or deleted. Branches and worktrees were left in place.

## 1. Audit result

| Item | Count / state |
| --- | --- |
| Git worktrees | 25 (main checkout + 24). 9 had uncommitted work. |
| Remote branches fully merged into `main` already | 22 (no action needed) |
| Branches with unmerged commits | 12 (see section 3) |
| Open PRs at start | #59, #63, #64, #65 (draft), #67 |
| Merged before this task | #66 (Aider worker). Not touched again. |
| Dirty main checkout (`feat/hero-room-reference-rebuild`) | 13 modified tracked + ~1,200 untracked files; 407 files existed in no branch |

## 2. Preservation (done first, non-destructive)

Snapshots were committed with a temporary git index, so no working tree, index or branch of another agent was touched; the originals are still in place. Runtime/cache files (`.godot-runtime`, `.venv`, `__pycache__`, `.aider*` chat history, `AGENTS.md.bak-*`) were skipped. A text scan of every snapshot found no API keys or secrets. All branches are pushed to `origin`.

| Preserve branch | Source | Files |
| --- | --- | --- |
| `preserve/main-checkout-wip-20261102` | main checkout (3 commits: policy/docs, Hero Room map work, Codex character/Game Factory WIP) | 844 |
| `preserve/task-0069-asset-factory-wip-20261102` | `.worktrees/TASK-0069-asset-factory` | 654 |
| `preserve/task-0070-game-factory-wip-20261102` | `.worktrees/TASK-0070-game-factory` | 224 |
| `preserve/task-0072-hero-attack-art-wip-20261102` | `.worktrees/TASK-0072-hero-attack-art` | 189 |
| `preserve/task-0074-golden-cyclone-wip-20261102` | `.worktrees/TASK-0074-golden-cyclone` | 48 |
| `preserve/task-0073-hero-attack-runtime-wip-20261102` | `.worktrees/TASK-0073-hero-attack-runtime` | 1 |
| `preserve/work-task-0071-aider-wip-20261102` | `skl-SF-TASK-0071` | 7 |
| `preserve/nifty-hellman-wip-20261102` | `.claude/worktrees/nifty-hellman-cad0fc` | 1 |
| `preserve/current-map-qa-wip-20261102` | `AncientSeal-DevTools/current-map-qa` | 5 |

The local-only branch `claude/nifty-hellman-cad0fc` was also pushed.

## 3. Branch decisions

Merged through `integration/consolidation-20261102` (clean worktree cut from `origin/main` `db2c678`):

1. `task-0061-token-preflight` (PR #63) - scoped Codex file bridge. Clean.
2. `claude/24h-battle-backlog` (PR #67) - TASK-0075..0089 battle backlog and the TASK-0071 follow-up (local config override, delayed trigger). Clean.
3. `task-0068-context-efficiency` (PR #64) - **conflict in `AGENTS.md`**, resolved by content (section 4).
4. `claude/nifty-hellman-cad0fc` - real Godot capture of `hero_room_01` v0011. Clean.
5. `feat/original-room-rebuild` - 128 approved environment PNGs, registry v2, blueprints, reference layout, Godot builder and stage screenshots. Clean.
6. `codex/game-factory` (also `codex/hero-attack-art`, `codex/golden-cyclone`, `codex/aider-hero-attack-runtime` which point at the same commit `936b1ca`, and PR #65 `codex/pixel-asset-factory`) - Game Factory, weaponless Hero, weapon factory, built-in image_gen asset factory. **Conflicts** in 129 `assets_generated` JSON files and `tools/test_map.json` (section 4).

Not merged, kept on their branches (stale Oct-27 candidates, conflicts only in generated monitoring/planner files):
- `feat/hero-room-props` (TASK-0067), `feat/hero-room-tileset` (TASK-0066) - Blender 64px prop/tileset candidates, unapproved art.
- `work/task-0063-00ca7e6f` (PR #59) - Blender side-wall candidate spec.
- `planning/20261027-000002-claude`, `planning/20261027-060002-codex` - read-only planner run logs.
These need an owner decision; they are not lost.

## 4. Conflict resolution (by content, no blind ours/theirs)

- `AGENTS.md`: PR #64 condensed the contract; `main` had gained the owner's 2026-11-02 roles/permissions policy, the graphics policy and the Aider gate. The result keeps the condensed structure, re-inserts the owner policy blocks, and removes the old "Codex must not write code" wording. It is 2,462 characters (limit 3,500 enforced by `test_local_planner`).
- `assets_generated/**/*.json` + `library_manifest.json` (129 files): both sides added the same sidecars. A script confirmed they differ only in `approval_status`/`approval`, so the owner-approved version (all 128 `approved`) was kept. PNG hashes were re-verified against the manifest: 0 mismatches.
- `tools/test_map.json`: both sides' test entries kept.
- The older `AGENTS.md` amendments in the main checkout ("Codex must NOT write code", `openai/gpt-4o`) conflict with the newer owner decision, so they were **kept only on `preserve/main-checkout-wip-20261102`**, not merged.

## 5. Validation

- `python tools/run_tests.py --all`: **34/34 passed** (python + Godot headless: import, map smoke, cardinal blocks, Aider worker). Two failures found after the merge were fixed first: AGENTS.md size limit and LF writers in the new room tools.
- `python tools/run_tests.py --check-index`: OK after `--write-index`.
- Godot render of the rebuilt room in the integration worktree: 0 validation issues, 52/52 free floor cells reachable.
- Aider compatibility: worker, `TASK-0071` and `TASK-0075..0089` present; models `openai/gpt-6.1-sol` / `openai/gpt-6-sol`, base `https://apimaster.ai/v1`; `aider_execution_enabled` and `execution_enabled` still `false`; no paid run was started. The $10 cap lives in the git-ignored local config of the main checkout (tracked `config.json` has `max_spend_usd: null`).

## 6. Still needs review / action

- The main checkout and the Codex worktrees still hold **uncommitted** WIP (character art, Hero Golden Cyclone/Phantom Dash frames, Hero Room v0012). It is preserved on `preserve/*` branches but not merged; merge it when each task is reviewed.
- Character, weapon and Game Factory art merged from `codex/game-factory` is **not visually approved** (`needs_review` stays in force).
- The 5 stale branches above and PR #59 need an owner decision.
- The Windows Scheduled Task is not registered and the Aider worker is not enabled (waiting on a fresh `OPENAI_API_KEY`).
- Old branches were intentionally not deleted.
