# Local subscription planner (Part 2)

One owner-goal folder per GOAL-#### with goal.md (owner's original text),
state.json (draft/active, milestone approval) and optional references/.
Reference images are NEVER fed to scheduled jobs; agents must not open project
graphics. One-time goal planning and final verification are separate reviewed
steps. The existing goals.json is a compatibility index until goal migration
is completed; never silently mark the first goal active.

## Schedule
Windows Task Scheduler, using the signed-in user's existing Claude Pro and
ChatGPT plan CLI login. Four times daily in Europe/Berlin local time:
08:13 Claude, 12:13 Codex, 16:13 Claude, 20:13 Codex.
Times, auto_activate (false), timeout and flags live in config.json.
The PC must be on AND the user session signed in; never put tokens or API
keys in Task Scheduler, GitHub Actions or the repository.

Windows (run from repo root in PowerShell after merging Part 2):
  py -3 tools/local_planner.py --agent claude --dry-run
  powershell -NoProfile -File tools/setup_local_planner.ps1

Remove schedules safely:
  powershell -NoProfile -File tools/setup_local_planner.ps1 -Uninstall

Pause everything: set planning_enabled=false and execution_enabled=false in
config.json, then run -Uninstall. Existing code and tasks remain intact.

## Read-only guarantees and expenses
Agents run LOCAL on subscriptions, no paid API keys or cloud AI calls:
- Claude: claude -p --permission-mode plan --tools "" --effort low
          --output-format json --json-schema ...
- Codex: codex exec --sandbox read-only --skip-git-repo-check
         --output-schema ... --output-last-message ... -
Both analyze a temporary TEXT-ONLY folder containing bounded inputs.
The host collects limited data from goals, task files, index and git log.
No model may inspect art or map images in routine analysis.
Model output is a JSON proposal: at most four tasks, with paths checked
against real existing non-image source files. Only the deterministic
goal_task_factory.py apply-proposal command edits task files.
An input SHA and fingerprint are tracked in checkpoint.json. If unchanged,
the model is not called at all. Rate-limits create cooldowns.json with a
6-hour cooldown; the other agent may be used once, never retry in a loop.
Runs produce sanitized JSON metadata in runs/. Raw prompts, model responses,
auth data or transcripts are never committed. Token/cost values may be unknown;
equivalent API cost is not an actual subscription charge.

Every planner branch is planning/YYYYMMDD-HHMMSS-agent, with a PR.
Automatic merge is allowed only if every CI check is successful and all paths
are restricted to .agents/tasks/, .agents/planner/ and generated FILES.md /
task dashboards. If CI fails or cannot be verified, PR stays open.
Code-task execution is *not* enabled here.

## Safe parallel code execution (Part 3 — OFF until owner-supervised E2E)
- Local script: `py -3 tools/agent_runner.py --preflight`. This checks configuration but cannot run code.
- `execution_enabled=false`, `supervised_e2e_passed=false` by default. **Do not toggle these before the first observed real task completes with tests, merge and post-merge verification.**
- After owner approval on Windows: `py -3 tools/agent_runner.py --run TASK-####` on a clean main branch. The runner creates an ephemeral worktree, hides image files during the AI stage, records task token receipts without writing indexes there, runs trusted unittest/Godot checks and serializes direct main merges. After a regression it reverts the merge commit and blocks the task.
- Two agents may run distinct nonoverlapping tasks, but merge to main is guarded by one lock. No auto-start Schedule for execution is installed while disabled.
- Art delivery: `py -3 tools/art_delivery.py --check` verifies PNG headers, alpha-capable channels, dimensions and SHA/metadata without rendering. `--integrate` remains disabled until metadata workflow supervision; it never paints images.
- Final goal visual approval belongs to owner. Rendering/comparing goal references is a separately supervised phase, not part of regular planning or coding.
- Risks: Claude and Codex file tool settings do not imply perfect OS-level denial of image reads; Codex can potentially read git objects. The sparse worktree reduces exposure but needs explicit real-world validation. Godot may require a renderable desktop environment for screenshots; headless dummy rendering cannot certify artwork.

## Owner art handoffs and final goal QA (supervised)
1. New art need: on clean main run tools/art_requests.py request with all required native dimensions, reference path, palette, 4 filenames, shadows, layers and quality criteria; commit ART record and blocked_on_art task before notifying.
2. Issue notice: set graphics_issue_enabled=true **only after checking gh auth**, then a local scheduled pulse calls art_requests.py notify; creates art-needed GitHub Issue assigned to shero92, one per request.
3. Owner delivers PNGs + complete native asset metadata and SHA hashes in .agents/graphics/deliveries/ART-####/; no coder opens these PNGs. tools/art_delivery.py --check validates headers, RGBA-capable channels, dimensions, hashes and catalog fields without visual interpretation. Once art_integration_enabled=true following supervised dry run, local planner integrates valid artifacts, closes Issue and unblocks ART-only blockers when dependencies are done. It cannot certify artistic quality.
4. Final goal preview: py -3 tools/goal_qa.py render GOAL-0001. Godot capture runs in temporary separate worktree using **actual factory script** tools/capture_map_previews.gd, copies real hero_room_final.png to .agents/qa/renders/GOAL-0001/. The renderer needs working OpenGL/video; if Windows --headless dummy cannot produce frames, switch config godot_qa_headless=false for owner desktop.
5. Compare once: py -3 tools/goal_qa.py compare GOAL-0001. ONLY this explicitly requested final verification permits Codex to see the original goal reference and final Godot render as image attachments. A one-attempt guard prevents unnoticed repeat viewing. Differences are written to .agents/qa/results/ for your review, not misattributed to fictional code lines.
6. After committing the QA paths and results, py -3 tools/goal_qa.py notify GOAL-0001 opens an owner-assigned GitHub Issue. Owner decides whether to approve or create new narrow investigation tasks. The script NEVER sets final_verified=true.
