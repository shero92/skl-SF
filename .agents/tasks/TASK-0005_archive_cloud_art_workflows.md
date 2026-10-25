---
id: TASK-0005
status: review
owner: chatgpt
branch: chore/disable-cloud-art-generation
depends_on: TASK-0004
issue: none
art_request: none
---
# Archive cloud art generators and remove unsafe write-back workflows

**Goal:** preserve definitions but stop GitHub Actions modifying production art
or project snapshots. Active cloud workflows are read-only tests plus verified
GitHub Issue notification; no cloud AI execution or generation.

## Acceptance
- [x] Archive all 12 game-art generation, repaint, curate and restore workflows.
- [x] Archive nine additional workflows that write map data or QA image files.
- [x] Disable cloud 4x task-writing schedule; retain verified-goal Issue notification.
- [x] Byte-identical Claude/Codex goal-task-factory skill CI guard.
- [x] Ignore .claude/settings.local.json.
- [x] Mark old merged tasks done, require real Agent git trailer.
- [ ] Review and merge PR; verify CI.

## Evidence / handoff
- Changed files: .github/workflows-disabled/, .github/workflows/,
  .gitignore, AGENTS.md, task records and generated FILES/TASKS indexes.
- Tests: GitHub Actions task/index/receipt validations; no art tasks executed.
- PR: review required.
- Next: confirm actual local Windows CLI help outputs, then implement Part 2.
