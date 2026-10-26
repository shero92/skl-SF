# Graphics production workflow — reviewed, AI-assisted environment art

## Separation of responsibility
**Producers (owner decision 2026-10-26):** Codex, Claude Code or an external graphics specialist create original **environment** art for one assigned ART request with authorized image tools (e.g. Codex `image_generation`). Never characters, UI or gameplay art; never a procedural or low-detail stand-in. **Reviewer:** approves visual quality and must not be the producing session; **owner:** final approval; **coder:** imports only reviewed deliveries and tests Godot.

## Before drafting an ART request (mandatory duplicate check)
1. Check latest `map_factory/metadata/asset_index.json` for identical ID/name, native size, source, status, art variants.
2. Check the current map placement and actual existing PNG. Don't assume `needs_cleanup` means missing.
3. Check `../graphics/QUEUE.md` plus all active request deliverable paths. Reuse/update an existing request rather than creating duplicates.
4. If the genuine reference image is not committed, create a `blocked_reference` specification; do not generate art from a guess. If it is committed but its SHA-256/dimensions are not yet confirmed, production may start, but the delivery cannot be reviewed or approved until the owner confirms the source.

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
- The producer stages PNGs under `../graphics/deliveries/<ART-ID>/` and writes a JSON `manifest.json` with output paths and actual SHA-256 values.
- Once output exists, `python tools/agent_workflow.py --check` checks filenames/manifest/hashes for statuses `delivered`, `reviewed` and `integrated`.
- Reviewer compares new images with **genuine** source at game scale, marks `reviewed` only after approval and records evidence.
- Coding agent imports approved art with stable ID/provenance/anchors/collision/shadows, updates map revision, runs Godot preview, then marks `integrated`.
- Completed requests are never regenerated: check request status, actual files and catalog before any new graphics task.

## Producing with image tools (Codex / Claude Code)
1. Claim the ART request's TASK in its own branch/worktree (`art/<ART-ID>`); never touch another agent's files.
2. Read the ART request, the goal reference and the accepted HD style references (W021, W022, A017, A018, D019, P023-P026); record the reference SHA-256 you actually measured.
3. Check reuse first (catalog IDs named in the request); cancel or narrow covered outputs instead of duplicating them.
4. Generate each asset and facing as a separate original image. Upright 3/4 objects need four distinct drawn views; never rotate or mirror a bitmap to invent a facing.
5. Use Python only for alpha cleanup, cropping, alignment and technical QA, never to paint content.
6. Write `manifest.json`: request_id, each path, measured SHA-256, pixel_size, origin/anchor, facing or frame order, footprint/mount/shadow notes, tool and model, prompt summary, producing agent, reference SHA-256, real cost or `unknown`.
7. Set the request to `delivered` only; keep the TASK `review`. Never write `map_factory/parts/`, never mark `reviewed`/`ready` yourself, never overwrite existing files.
