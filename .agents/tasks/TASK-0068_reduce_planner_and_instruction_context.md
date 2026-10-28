---
id: TASK-0068
status: review
owner: codex
branch: task-0068-context-efficiency
issue: none
art_request: none
agent: codex
touches: AGENTS.md,CLAUDE.md,tools/local_planner.py,tools/tests/test_local_planner.py,tools/run_tests.py,tools/tests/test_run_tests.py,.agents/skills/goal-task-factory/SKILL.md,.claude/skills/goal-task-factory/SKILL.md,.github/workflows/agent_workflow.yml
test: py -3 tools/run_tests.py --changed
done_when: Reduce always-loaded instructions to at most 3500 characters while preserving scope, safety, graphics, task, test, cost and approval rules; make CLAUDE.md a concise entrypoint; keep one canonical goal-task-factory skill body and make Claude's project skill a short pointer; build deterministic planner context from open requests and approved actionable goal/task records with relevant blockers and evidence, cap it at 12000 characters by dropping whole lowest-priority sections and never truncating a record; preserve existing RTK/Godot MCP settings and document only safe RTK bypass/use guidance in project instructions; add tests for selection, priority, complete-record trimming and limits. Run the same local context-size and output-size scenarios before and after; report character/byte proxies only, never claim model token savings.
depends_on: none
---
# Reduce always-loaded and planner context safely

**Goal:** Lower repeat context overhead for Codex and Claude without removing owner controls or changing global tool settings.

## Acceptance
- [x] The task-specific contract remains complete, with `AGENTS.md` <= 3500 characters and concise `CLAUDE.md`.
- [x] Planner context contains only open requests, approved active goal steps with unresolved task dependencies/blockers/evidence, and recent relevant commits; selection is deterministic and <= 12000 characters without partial records.
- [x] Claude skill is a short discovery wrapper to the canonical `.agents/skills/goal-task-factory/SKILL.md`; both retain valid frontmatter and clear invocation guidance.
- [x] RTK guidance avoids JSON/JSONL and machine-parsed Git output; no global settings, MCP servers, hooks, or installed tools are changed.
- [x] Unit and test-router checks pass; failed test output retains concise diagnostics and a complete local raw log; local before/after measurements record sizes, read counts and median elapsed time from three runs where measurable.

## Evidence / handoff
- Changed files: `AGENTS.md`, `CLAUDE.md`, planner context builder/tests, test failure diagnostics/logging and regression tests, Claude skill discovery wrapper, and this task record.
- Tests: `tools/run_tests.py --only test_router` passed; `tools/run_tests.py --changed` passed 30/30; `tools/run_tests.py --all` passed 30/30; `tools/agent_workflow.py --sources-only` passed. `agent_workflow.py --check` reports stale main-generated `.agents/project/ACTIVE.md` and `TASKS.md`, intentionally not regenerated in this worktree. Initial PR CI exposed an equality check that contradicted the concise Claude-wrapper requirement; updated it to assert a short wrapper references the canonical skill.
- Measurements: context 28,000→11,771 characters; planner file reads 87→53 per run; median local time 42.67→63.49 ms. Instructions 7,356→2,737 characters; Claude entry 749→330 characters. Character/byte measurements are proxies, not model-token savings.
- PR: https://github.com/shero92/skl-SF/pull/64 (CI follow-up pushed after initial run).
- Next: review and merge through the repository workflow.
