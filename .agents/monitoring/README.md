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

The versioned hook configurations use sh tools/agent_costs_hook.sh to try the Windows py launcher, then python3 and python (minimum Python 3.10). Git Bash is expected on Windows. If py -3 --version fails, install Python 3.x first and relaunch the terminal. Claude hook edits may need approval under /hooks after pulling new settings. Codex project hooks require workspace trust.

## How to use

Start from the repository root in a dedicated branch/worktree, BEFORE opening a new agent session.

Claude example:
    python3 tools/agent_costs.py start TASK-0003 --agent claude
    claude
    python3 tools/agent_costs.py finish
    python3 tools/agent_costs.py report
    git add .agents/monitoring/receipts .agents/monitoring/summary.json .agents/monitoring/summary.md
    git commit -m "feat: describe task" -m "Task-ID: TASK-0003" -m "Agent: claude"
    git push origin YOUR_BRANCH

Codex: start with --agent codex, then launch codex in a FRESH session, and finish/commit the same way with Agent: codex.

For joint tasks each agent uses its own worktree and writes a separate receipt. Both receipts share the same Task-ID. Never run two agents from the same worktree: the ignored local active-task file is worktree-scoped.

## Data collection

- Claude Code project statusLine supplies total session estimated cost in USD. Stop and SessionEnd hooks collect transcript token usage when available.
- Codex project hooks read local JSONL token counts at Stop/SessionEnd. The price is estimated only for a model explicitly listed in pricing.json, using standard API-equivalent rates.
- For unsupported clients, cloud sessions or unavailable data, finish still creates a receipt but stores null for unknown cost or tokens. Manual estimation is possible using: python3 tools/agent_costs.py finish --manual-cost-usd 0.42 (labeled manual).
- Fresh sessions are required for task attribution. Existing sessions that demonstrably began before tracking are excluded instead of charging earlier tasks to the current one.
- A session cost can contain subagent usage if the provider includes it. Subscription charges, third-party tool charges and unobserved subagent costs are NOT independently measured.
- No hooks automatically push commits. The finishing agent must include the receipt and summary in the same commit as the code. The SHA can then be resolved using: git log -1 --format=%H -- path/to/receipt.json. Including the SHA inside that same receipt would be circular.

## Read or validate

    python3 tools/agent_costs.py report
    python3 tools/agent_costs.py report --check

summary.md ranks tasks by known USD; summary.json powers dashboards. If unknown_costs is not zero, that task's known USD is a lower bound and should not be used as a complete comparison.

Keep local session files and provider credentials private. Inspect project hooks before trusting the repository.
