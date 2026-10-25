# Claude Code + Codex: cost per committed task

Every coding task gets a JSON cost receipt inside .agents/monitoring/receipts, committed WITH its code changes. The task ID is the common key for both agents. Logs and transcripts stay local and ignored by Git.

## Quick local smoke test, no task ID needed

On Windows **exit Claude/Codex before starting** and use a normal PowerShell terminal:

    py -3 --version
    py -3 tools/agent_costs.py start --agent claude
    claude
    # ask a short read-only question, then /exit
    py -3 tools/agent_costs.py finish

Use --agent codex and launch codex for the other client. A no-ID run receives a unique TEST-* ID and creates a **local-only** receipt under .agents/monitoring/.local/test_receipts/. Test receipts never appear in the committed leaderboard. This cannot retroactively measure a session that was started before tracking.

To run the portable hook command manually in Git Bash:

    sh tools/agent_costs_hook.sh --help

On this Windows project, Claude and Codex hooks invoke `py -3` directly; no Git Bash is required. On macOS/Linux, replace the hook command with `python3 tools/agent_costs.py hook ...` or use `sh tools/agent_costs_hook.sh`. A task transcript is never committed. Use `py -3 tools/agent_costs.py diagnose` to check whether hooks captured a transcript, tokens, and status-line cost without revealing personal paths. If py -3 --version fails, install Python 3.x first and relaunch the terminal. Claude hook edits may need approval under /hooks after pulling new settings. Codex project hooks require workspace trust.

## How to use

Start from the repository root in a dedicated branch/worktree, BEFORE opening a new agent session.

Claude example:
    py -3 tools/agent_costs.py start TASK-0003 --agent claude
    claude
    # After tests, agent stages only intended task files:
    git add path/to/changed/code path/to/task/evidence
    py -3 tools/agent_costs.py complete --message "feat: implement TASK-0003" --push

Codex: start with `--agent codex`, then launch Codex in a fresh session. If using `codex exec --json`, import the JSONL usage after the run. Once task code/evidence is staged, invoke the same `complete --message ... --push` command. Hooks gather usage but **do not perform git actions on their own**.

For joint tasks each agent uses its own worktree and writes a separate receipt. Both receipts share the same Task-ID. Never run two agents from the same worktree: the ignored local active-task file is worktree-scoped.

## Data collection

- Claude Code project statusLine supplies total session estimated cost in USD. Stop and SessionEnd hooks collect transcript token usage when available.
- Codex project hooks read local JSONL token counts at Stop/SessionEnd. The price is estimated only for a model explicitly listed in pricing.json, using standard API-equivalent rates.
- For unsupported clients, cloud sessions or unavailable data, finish still creates a receipt but stores null for unknown cost or tokens. Manual estimation is possible using: python3 tools/agent_costs.py finish --manual-cost-usd 0.42 (labeled manual).
- Fresh sessions are required for task attribution. Existing sessions that demonstrably began before tracking are excluded instead of charging earlier tasks to the current one.
- A session cost can contain subagent usage if the provider includes it. Subscription charges, third-party tool charges and unobserved subagent costs are NOT independently measured.
- The agent's `complete --message "..." --push` command commits and pushes only its task branch, never `main`. It will refuse to run without a tracked TASK ID and already staged task files. If push fails, the commit remains local and the agent must report that failure. The SHA is resolved from git history after committing; it cannot be embedded into the commit it names.

## Read or validate

    python3 tools/agent_costs.py report
    python3 tools/agent_costs.py report --check

summary.md ranks tasks by known USD; summary.json powers dashboards. If unknown_costs is not zero, that task's known USD is a lower bound and should not be used as a complete comparison.

Keep local session files and provider credentials private. Inspect project hooks before trusting the repository.

## Print mode and cost estimation

`claude -p` might not invoke a UI status line. For such sessions the tool now estimates Opus 5.5 API-equivalent USD from Claude JSONL assistant usage, including 5-minute and 1-hour cache creation when the transcript distinguishes them, and cache reads. This is an estimate, NOT what a Claude Pro subscription charged. If the model or transcript cannot be determined, cost remains null. Codex pricing still requires a matching model key. The `diagnose` command reports local hook coverage without exposing transcripts.

## Codex CLI without TUI: reliable JSON usage import (Windows)

If `codex resume` fails or the terminal immediately disconnects, use the officially supported `codex exec --json` mode. Use a fresh task (`start --agent codex`) in PowerShell, then:

    codex exec --json --sandbox read-only "Review map_factory/FOUR_DIRECTION_BLOCKS.md. Explain directions briefly. Do not change files." 2> $null | Tee-Object -FilePath ".agents/monitoring/.local/codex-exec.jsonl"
    py -3 tools/agent_costs.py import-codex ".agents/monitoring/.local/codex-exec.jsonl"
    py -3 tools/agent_costs.py diagnose
    py -3 tools/agent_costs.py finish

PowerShell 5.1 may write Tee-Object JSONL with UTF-16LE BOM. `import-codex` handles UTF-8, UTF-8 BOM and UTF-16 BOM. The JSONL contains tool output, prompts and model responses: treat it as **private** and never commit it. The importer extracts **only** `turn.completed.usage` into a hashed local snapshot, with thread IDs not committed. If the stream lacks a model identifier, add `--model ACTUAL_MODEL_SLUG` to `import-codex` after confirming the model used. The pricing table contains only verified/existing slugs; unknown rates produce null cost. Never invent a model or a price.

When the same thread's Codex hooks have run, the imported thread ID replaces its session usage to avoid double-counting. This importer can be reused for real tasks as well as smoke tests.

## Required committed token receipt and Git trailers

For every **real TASK-####**, Claude or Codex should stage only intended code/evidence, then finish with `py -3 tools/agent_costs.py complete --message "feat: ..." --push`. This does NOT automatically stage all modifications, avoiding accidental unrelated changes. The resulting commit includes:

    Task-ID: TASK-0012
    Agent: codex
    Tokens-Input: 57167
    Tokens-Output: 199
    Tokens-Cached-Input: 49920
    Tokens-Reasoning: 0
    Cost-USD: unknown
    Cost-Receipt: .agents/monitoring/receipts/TASK-0012_codex_xxxxx.json

Each receipt also records models, agent, measured tokens, estimated cost (nullable), and completion timestamp. The per-task leaderboard combines Claude and Codex receipts under the same TASK ID. `Tokens-Input` already includes cached tokens; `Tokens-Output` includes reasoning tokens, so never sum them twice. Capture is a snapshot **as of the completion command** and cannot include later agent output or changes made after push. This is a price-comparison estimate, not an actual subscription bill. Unknown costs are clearly marked; never invent rates or metrics.
