# Shared coding-agent contract

Applies to Codex, Claude Code, Aider and all coding agents. Read this, then only the assigned task and relevant docs.

## Owner policy (2026-11-02; supersedes older "Codex must not code" rules)
- Any agent may do a task the owner explicitly assigns; model identity alone never blocks it.
- Codex Pro: code, tests, scripts, automation config, graphics, plans, reports, task records. Aider CLI: tasks with `agent: aider`, run by `tools/aider_worker.py` (`docs/AIDER_AUTOMATION.md`), models `openai/gpt-6.1-sol` / `openai/gpt-6-sol` at `https://apimaster.ai/v1`, never images. Claude Code: tasks marked `agent: claude` or requested by the owner.
- Record the real tool and model (`Agent: aider|claude|codex`). API keys come from the owner's environment, never repo, prompts or logs.
- Aider stays OFF until `tools/setup_aider_worker.ps1` activates it (owner cap $10 per 24 h, `max_spend_usd`); the worker never merges.
- Protections: branch and worktree per task, no push to `main`, no force push, keep uncommitted owner changes, protected character/UI art, approved art and map history.

## Graphics
- Read `docs/GRAPHICS_PRODUCTION_POLICY.md` first: each reusable frame/item is its own file, no multi-pose crops, sprite sheets are assembled outputs only, keep sources, review new art before activation, unapproved art is never production.
- Assigned agents may use local Blender in `H:\shining force\pixel-art` (`.agents/workflows/GRAPHICS.md`). No paid image services.

## Scope and truth
- Story/world grounding: start at `docs/story/INDEX.md` and `docs/design/STORY_CANON_AR.md` before changing a location or character role. Owner clarification2026-11-13: Hidden Island is wild; the hero is the only known human at the opening, with nonhuman family/friends. Do not infer human settlements or maintained palaces from art-style references. Local2026-10-16 Reef Friend correction takes precedence over older Cely-as-waiting-friend text. Story documents do not prove runtime implementation.
- Environment/Map Factory by default; characters, gameplay, portraits, dialogue and UI only when the owner assigns them.
- Locate files via `INDEX.md`; read only needed ranges. Commits/PRs and catalog IDs prove work; never call unreviewed art approved.

## Tasks and evidence
- Follow `.agents/workflows/TASKS.md`: claim one task, isolated branch/worktree, no overlapping touches. Receipts via `tools/agent_costs.py` (missing usage stays `unknown`); stage only task files; push task branches.
- Run `py -3 tools/run_tests.py --changed` before commits and report real results. Direct merges to `main` follow owner ADR-006; generated indexes update on `main` only.

## Map safety and tools
- Patch the latest map revision, never rewrite history. See `map_factory/MAP_FACTORY_RULES.md`; preview `scenes/map_factory_preview.tscn`.
- Use RTK (`rtk bypass` for exact output) and the existing Godot MCP; plan per `.agents/planner/PROMPT_RULES.md`.
