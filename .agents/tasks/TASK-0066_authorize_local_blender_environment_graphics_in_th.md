---
id: TASK-0066
status: review
owner: codex
branch: codex/graphics-rules-external-workspace
agent: codex
touches: AGENTS.md,CLAUDE.md,.agents/workflows/GRAPHICS.md,.agents/roles/graphics.md,.agents/roles/coding.md,.agents/workflows/HANDOFF.md,tools/blender/README.md,.agents/planner/goals.json,.claude/settings.json,.codex/config.toml,.agents/roles/review.md
test: py -3 tools/run_tests.py --changed
done_when: Consistent owner-authorized environment graphics rules and scoped workspace permissions; protected character/UI scope and human approval retained; no renderer/runner logic or image changes.
started_at: 2026-10-28T00:21:36.691283+01:00
cost_usd: unknown
depends_on: none
issue: none
art_request: none
---
# Authorize local Blender environment graphics in the external pixel-art workspace

**Source:** request:REQ-beabc1b08754
**Created:** 2026-10-28
**Goal:** manual request
**Type:** architecture
**Priority:** critical
**Suggested agent:** codex (routing heuristic, not a performance claim)
**File:** AGENTS.md
**Line:** unspecified
**Problem:** Owner explicitly requests rules and permissions only: Codex and Claude may build pixel-art environment blocks with local Blender and save assets under H:/shining force/pixel-art; conflicting instructions and blanket image denies currently block assigned graphics work.

## Acceptance
- [ ] Consistent owner-authorized environment graphics rules and scoped workspace permissions; protected character/UI scope and human approval retained; no renderer/runner logic or image changes.
- [ ] Test: py -3 tools/run_tests.py --changed
- [ ] PR and observed test evidence.

## Agent prompt
Outcome: Consistent owner-authorized environment graphics rules and scoped workspace permissions; protected character/UI scope and human approval retained; no renderer/runner logic or image changes.. Evidence: Owner explicitly requests rules and permissions only: Codex and Claude may build pixel-art environment blocks with local Blender and save assets under H:/shining force/pixel-art; conflicting instructions and blanket image denies currently block assigned graphics work.. Target: AGENTS.md (line unspecified). Verify with: py -3 tools/run_tests.py --changed. Read AGENTS.md and this task, then only the target file. Verify the issue and location before changing code. Work only within Map Factory. Never generate artwork. Stop when evidence is missing. Commit the task, token receipt and summary on a PR branch, never main.

## Budget
- Aim below 12000 tokens; context estimate, not enforced cap.
- Read only targeted files, then expand if necessary.

## Evidence / handoff
- Changed files: none.
- Tests: not run.
- PR: none.
- Next: claim task after checking blockers.

## Owner-supervised rules-only scope
- Explicit owner request 2026-10-28 authorizes these scoped project permission changes. No runner/renderer/Python implementation changes, no art produced, and no external folder contents changed.
- Existing helper external-path limitations and launcher tool exclusions are documented, not silently bypassed.

## Verification and handoff
- py -3 tools/run_tests.py --changed: 30/30 groups passed, including Python, Blender tooling and Godot.
- py -3 tools/agent_workflow.py --sources-only: passed. JSON/TOML parse and exact external-root assertions passed; hooks/statusLine preserved; no blanket Bash or sandbox bypass setting added.
- Rules/config only: no .py/.ps1/.gd implementation changed and no assets or external folder contents edited. Original dirty primary checkout and TASK-0061 implementation worktree preserved.
- Current helper relative-path requirements and explicit launcher tool restrictions remain documented limitations; this PR does not claim runtime support was implemented.
- Next: review/merge this owner-authorized project policy PR, trust/restart agent sessions to load settings; graphics producers follow the scoped workspace rules.
