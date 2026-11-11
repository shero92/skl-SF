---
id: TASK-0162
status: todo
owner: codex
agent: codex
priority: high
branch: codex/own-worktree-rule
depends_on: none
issue: none
art_request: none
touches: .agents/tasks/TASK-0162_codex_own_worktree.md,docs/CODEX_WORKTREE.md
test: python tools/agent_workflow.py --sources-only --base origin/main
done_when: Codex produces and stages art in its own git worktree under .worktrees/, never in the owner's main checkout H:/shining force/skl-SF, so the owner's F5 always runs the latest main; the rule is written down and the main checkout has no uncommitted Codex files.
---
# Codex works in its own worktree, not the main checkout

Planned 2026-11-11 after hero_room_01 v0026 (owner asked for the next tasks for Claude and for Codex).

- On 2026-11-11 uncommitted Codex files in the main checkout blocked two updates to origin/main; they were saved to backup/local-changes-20261111 and backup/local-changes-20261111b.
- Delivery manifests must carry request_id and a files list (path and sha256) matching the request output_paths; three PRs failed the check for this on 2026-11-11.
