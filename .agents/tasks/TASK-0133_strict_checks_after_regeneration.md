---
id: TASK-0133
status: review
owner: claude
agent: claude
priority: medium
branch: claude/strict-after-regen
depends_on: TASK-0126
issue: none
art_request: none
touches: .github/workflows/agent_workflow.yml,.github/workflows/project_indexes.yml,.github/workflows/agent_costs.yml,tools/tests/test_regenerate_main_outputs.py
test: python tools/run_tests.py --changed
done_when: The three strict generated-file checks run on main after the regeneration job instead of on the stale merge commit, still strict, and still run if regeneration fails.
estimate_minutes: 20
---
# Strict checks after regeneration (no more transient red on every merge)

**Problem (verified):** the bot's regeneration commit does not trigger workflows (GITHUB_TOKEN), so the three strict checks ran only on the merge commit, before regeneration, and showed red on every merge even though main was refreshed seconds later.

**Fix:** on main the checks are triggered by `workflow_run` of "Regenerate main-only outputs" (any conclusion) and check out `main`, so they see the regenerated state; pull-request behaviour (read-only sources checks) is unchanged and nothing is disabled. If regeneration fails or the generated files are still stale, the strict check still fails visibly.

## Limits
workflow_run workflows only start once the workflow files are on the default branch, so the first run happens after this merge.

## Evidence / handoff
- Tests: test_regenerate_main_outputs.py (new case), test_project_indexes.py (existing strict/PR-read-only case).
- Next: confirm the three checks are green on the first main run after merge.
