# Autonomous 24-hour plan - Dynamic Battle Animation System

Written by Claude Code on 2026-11-02 from the repository state on branch `task-0071-claude-aider-worker` (PR #66).
Status of execution: **queue prepared, automation NOT started** (see Prerequisites).

## Audit (what was actually found)
- PR #66 (Aider worker): two CI failures were real and are fixed on the branch: `lf_writers` (writes without `newline="\n"`) and the task validator rejecting `agent: aider`. Unit tests: 21 worker tests plus `tools/run_tests.py --all` 31/31 passed locally (incl. Godot). The PR is still **unmerged** and unreviewed.
- TASK-0072/0073/0074 exist only inside Codex worktrees (`codex/hero-attack-art`, `codex/aider-hero-attack-runtime`, `codex/golden-cyclone`) and are unmerged; so are TASK-0070 Game Factory and `docs/HERO_ATTACK_STYLE.md`. TASK-0073 (Aider, blocked) already owns the preview scene, `tools/hero_attack_assets.py` (sheet inspect/extract) and GIF assembly: this plan does **not** duplicate those.
- TASK-0073 recorded a real Aider attempt that failed with `OPENAI_API_KEY: Not set`. TASK-0072 art is `needs_review`; TASK-0074 frames 001-013 are candidates.
- Map Factory: TASK-0062 (depends TASK-0059) and TASK-0064 (depends TASK-0062, TASK-0063) are `blocked`; TASK-0059 `blocked` (depends TASK-0037, TASK-0061), TASK-0061 `blocked`. They stay out of the Aider queue; their blocking art/dependency chain was not resolved here.

## Backlog created (TASK-0075 .. TASK-0089, 15 tasks, about 17 h estimated)
| Task | Agent | Status | Depends | Est. min | What |
|---|---|---|---|---|---|
|  | aider | done | none | 60 | Timeline core + headless Godot harness |
|  | aider | done | 0075 | 90 | BattleAnimationController |
|  | aider | done | 0075 | 45 | Perspective resolver (hero rear 3/4, front, monster rear) |
|  | aider | done | 0075 | 90 | Dynamic Camera2D (zoom, shake, hitstop focus, restore) |
|  | aider | done | none | 60 | Weapon socket schema + validator |
|  | aider | done | 0075,0076 | 45 | Hit timing -> damage-event bridge |
|  | aider | done | 0076,0077 | 60 | Combo sequence + recovery |
|  | aider | done | 0076,0077 | 60 | Monster/hero reactions |
|  | aider | done | 0075,0079 | 75 | Separate VFX layer / sword trail |
|  | claude | done | 0076,0077,0078,0080 | 120 | Preview scene with selectors (stub actors) |
| 0085 | aider | **blocked** | 0084 | 60 | Adapter to ModularBattleCharacter (needs TASK-0070 merged) |
| 0086 | aider | **blocked** | 0085 | 90 | Phantom Dash controller (needs approved rear art, TASK-0072) |
| 0087 | aider | **blocked** | 0085 | 90 | Golden Cyclone controller (needs approved TASK-0074 frames) |
| 0088 | claude | done | 0071,0075-0078,0080 | 45 | Register battle tests in `tools/test_map.json` |
| 0089 | claude | done | 0076 | 45 | Claude review of Aider commits + art-gap report |

First runnable tasks: **0075, 0079** (no dependencies, no shared files). The run window is wall-clock based: time spent in Windows Sleep or shutdown still counts, and actual runtime is not guaranteed.
Scope note: `tools/runner_safety.py` now also allows `scenes/battle/` and `game_factory/battle/` (battle-only new files). Characters, UI, portraits and gameplay folders stay forbidden, and so do images/art.

## Art still missing (owned by Codex / graphics pipeline, not Aider)
- Hero rear 3/4 attack frames (ART-0028, TASK-0072) - needs_review.
- Golden Cyclone body frames 014-022 and separate effects (ART-0029, TASK-0074); weapon anchors and final GIF unconfirmed.
- Hero front-view hit/block frames and monster rear/attack frames: no request found; open one before TASK-0082 can show final visuals (it only reports MISSING_*_ART until then).

## Prerequisites before unattended execution (checked 2026-11-02)
| Item | State |
|---|---|
| PR #66 reviewed and merged (worker + `aider` agent validation on main) | not done |
| `aider` executable found (PATH or `aider.executable` in config) | **not on PATH** |
| API key present in the worker's environment (`OPENAI_API_KEY`, value never read) | **not set** (process or user scope) |
| Explicit spend limit (`aider.max_spend_usd` or `max_aider_runs`) | **not set** (null => worker refuses paid runs) |
| Run window (`run_window_hours: 24`, wall-clock, resumes after restart, `new-window` to renew) | implemented + tested |
| Scheduled Task `SklSfAiderWorker` | not registered (SyncAISkills untouched, Ready) |
| `aider_execution_enabled` | false |
| Model/endpoint availability (`openai/gpt-6.1-sol`, `https://apimaster.ai/v1`) | unverified (no API call made) |

To start after the owner approves: set the key yourself in your terminal (never in the repo), set a spend limit, then
`powershell.exe -NoProfile -File tools\setup_aider_worker.ps1 -Install` and set `aider_execution_enabled: true`.

## Status log
Updated by TASK-0089 (Claude Code, Sonnet 5.5, 2026-11-09) from git history; `.agents/monitoring/.local/aider/` has no `costs.jsonl`/`execution.log` for these tasks, so costs are unknown (not zero).
- 0075-0079, 0083: Aider commits merged to main earlier (PR #70, #73); battle suites pass.
- 0080-0082: Aider commits on `aider/task-0080..0082`, integrated and verified by Claude in PR #105 (only conflict: `tools/test_map.json`, resolved by keeping all entries).
- 0084: implemented by Claude (Aider paused, API balance exhausted on 2026-11-09), PR #106 stacked on #105.
- 0085-0087: still blocked on art/adapter prerequisites. 0088: todo (see its own task). Real defects found in reviewed Aider commits: none beyond the test_map merge conflicts.
- Aider is paused by the owner for about one week; the prerequisites table above is historical (2026-11-02).
