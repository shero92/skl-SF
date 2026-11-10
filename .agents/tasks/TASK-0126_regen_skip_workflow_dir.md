---
id: TASK-0126
status: review
owner: claude
agent: claude
priority: high
branch: claude/ci-regen-fix
depends_on: TASK-0125
issue: none
art_request: none
touches: tools/generate_project_indexes.py,tools/tests/test_project_indexes.py
test: python tools/run_tests.py --changed
done_when: The post-merge regeneration job can push because no generated file lives under .github/workflows.
estimate_minutes: 20
---
# Let the regeneration job push (no inventory under .github/workflows)

**Problem (verified in the first run on main after PR #141):** the job regenerated everything and committed, but GitHub rejected the push: "refusing to allow a GitHub App to create or update workflow .github/workflows/FILES.md without workflows permission". The GITHUB_TOKEN can never write under .github/workflows, and the folder inventory generator wrote FILES.md there.

**Fix:** generate_project_indexes.py skips .github/workflows (the folder keeps its hand-written INDEX.md); the old tracked .github/workflows/FILES.md is left in place and ignored (a task branch may not touch generated files and the bot may not delete it; the owner can remove it directly); a test guards it. Alternatives rejected: a personal access token in secrets (extra credential), or excluding the file from the bot commit (main would stay stale).

## Evidence / handoff
- Tests: test_project_indexes.py (8 pass).
- Next: after merge confirm the Regenerate workflow pushes and the three strict checks turn green.
