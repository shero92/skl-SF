# Graphics production workflow — coding agents must NOT create art

## Separation of responsibility
**Codex / Claude Code:** inspect existing art → specify exact requirement → create/track ART request → integrate *reviewed, delivered* PNG + metadata. Never generate new sprites, procedural pictures, textures, room composites or AI art as a workaround.
**Graphics specialist only:** create high-quality graphics as requested. **Reviewer:** approves visual quality; **coder:** imports safely and tests Godot.

## Before drafting an ART request (mandatory duplicate check)
1. Check latest `map_factory/metadata/asset_index.json` for identical ID/name, native size, source, status, art variants.
2. Check the current map placement and actual existing PNG. Don't assume `needs_cleanup` means missing.
3. Check `../graphics/QUEUE.md` plus all active request deliverable paths. Reuse/update an existing request rather than creating duplicates.
4. If the genuine reference image is not committed, create a `blocked_reference` specification; do not generate art from a guess.

## Art request contract
Copy `../templates/ART_REQUEST.md` to `../graphics/requests/ART-####_short_name.md`. Include a unique stable `dedupe_key` describing the art need (used by CI to prevent duplicate requests), plus:
- Purpose/location/layer and *why existing registered parts cannot be reused*.
- Current reference file and hash or explicit missing reference, screenshot comparison, relevant existing asset IDs.
- Exact independent output paths, desired facing(s), visual scale/dimensions or measurable criteria, RGBA/seams, anchors, shadow/light, collision context and no duplicate/repaint rule.
- Acceptance checklist split into request, specialist delivery, reviewer QA and final integration.
- Related TASK ID, owner, state and evidence links.

## State machine
`blocked_reference` → `requested` → `in_progress` → `delivered` → `reviewed` → `integrated`; `cancelled` if unnecessary. No jumping to integrated. The art request is authoritative; `QUEUE.md` is generated from it.

## Deliver / integrate
- Graphics specialist stages PNGs under `../graphics/deliveries/<ART-ID>/` and writes a JSON `manifest.json` with output paths and actual SHA-256 values.
- Once output exists, `python tools/agent_workflow.py --check` checks filenames/manifest/hashes for statuses `delivered`, `reviewed` and `integrated`.
- Reviewer compares new images with **genuine** source at game scale, marks `reviewed` only after approval and records evidence.
- Coding agent imports approved art with stable ID/provenance/anchors/collision/shadows, updates map revision, runs Godot preview, then marks `integrated`.
- Completed requests are never regenerated: check request status, actual files and catalog before any new graphics task.
