# Hero Room — Visual Fidelity Standard

This is the reference art direction for the provided 1448×1086 Hero Room screenshot. It is the standard against which candidate replacement sprites should be reviewed, not an automatic approval checklist.

## Original reference appearance

- **Viewpoint:** three-quarter top-down fantasy JRPG, not strict isometric; room geometry follows a rectangular floor grid.
- **Stonework:** detailed sunlit amber/limestone sandstone, visible blocks and soft occlusion, crisp engraved cuts, weathered edges. Use warm highlights over a coherent mid-brown shadow value.
- **Sea and distance:** vivid high-saturation cobalt/cyan ocean with bright foam, receding rocky islands, deep blue distance and luminous sky clouds. Layer as separate moving water, static islands, and distant sky.
- **Greenery:** strongly saturated yet readable green ivy, small white/yellow flowers, orange accent blooms, layered vines attached to architecture. Never bake neighboring objects into vegetation sprite crops.
- **Wood/furniture:** textured brown/gold wood with tightly organized blue/gold cloth, small compass medallion details and readable silhouette in a tiny top-down game.
- **Hero/companions:** the reference hero is much more detailed than the current procedural 72×96-native prototypes: layered auburn hair, gold/cobalt outfit, soft shaded face, cape and sword; the companion has a detailed crystal ridge and expressive face.
- **UI:** nearly black navy with deep sapphire gradient, thin gold border and cutout gold corner ornament. Face portrait uses anime pixel-art with detailed hair/blue eyes.
- **Lighting:** strong warm sun arriving from the upper left, small amber lantern/candle pools, coherent shadows cast to the lower-right. Avoid multiplying baked shadows onto independent alpha shadows.
- **Atlas hygiene:** NO screenshot text, source-sheet captions, gold label bars, neighboring sprite slivers, cut-off outlines, solid box backgrounds behind object sprites, or alpha fringes.

## Approximate palette sampled from the provided screenshot

These are *guideline samples*, not rigid global quantization (which would destroy detail).

| Material | Highlights | Midtones | Shadows |
|---|---|---|---|
| Sunlit limestone | #FCE28E | #F1BA6E, #C8A279 | #89654C |
| Maritime textiles | #0960DF | #1248A5 | #031844 |
| Nautical golden trim | #F4E041 | #E6B11D | #B69C36 |
| Deep dialogue panel | #394668 | #031844 | #040A1D |
| Sky/sea | #90C3F9 | #3A9FFB, #0E6DD2 | #2F67AB |
| Ivy | #9FBA62 | #3C5C1D | #141D09 |

## QA acceptance test for every replacement

1. Compare the sprite at **native on-screen Godot scale**, not an enlarged editor preview.
2. Ensure a consistent overhead perspective, shape, proportions and contact point with the supplied screenshot.
3. Save a true **individual transparent PNG** except opaque full-screen environments.
4. Check no visible labels, neighbor fragments, alpha halos or clipping; verify animation frame alignment.
5. Fit position/anchor/collision/shadow metadata to actual sprite, preserve stable ID and room instances.
6. Keep a visible before/after comparison, and do not replace an image merely because its pixel dimensions are larger.
7. Run the Godot CI smoke test before approving. Only then may an artist or reviewer set status to ready.

## Current state

The automated cleanup pass removed unrelated cutout scraps from 23 PNGs, but **all 218 sprites still need artistic review**. The first-pass procedural hero, fairy and sea assets will require high-fidelity replacement artwork to fully match the reference.

Related: [art cleanup findings](ART_QUALITY_REVIEW.md), [visual preview gallery](ASSET_GALLERY.md) and [asset index](../map_factory/metadata/asset_index.json).

## GOAL-0001 art intake triage (2026-10-26, not visual approval)

Issue [#20](https://github.com/shero92/skl-SF/issues/20) describes ART-0002..ART-0021 (20 requests, 50 named PNG deliverables); [#14](https://github.com/shero92/skl-SF/issues/14) tracks four-view bed ART-0001. All 21 are **blocked_reference**, NOT delivered. Do not create dummy placeholder PNGs, reinterpret existing sprites as approved, or mark art `requested` merely to unblock a coder.

**Reference integrity measured from actual files uploaded in the owner's chat:**
- Full 3/4 seaside Hero Room source: 1448×1086, SHA-256 `42511e4e05176d9057775fa05562ca5b91675d32ba70ae9b8ba1012b41df25a7`, file size 3,350,789 bytes, Git blob SHA-1 of these exact bytes `e359b0783b4e818533eef163643fe93bf840552a`.
- Separate transparent four-object style reference: 1312×1199, SHA-256 `9e8201055c26ac468d3bfd4052dc664925dd3bf5b25a9741f6f786fc79734763`. This style sheet is not the level layout.
- **Committed goal reference is not byte-identical:** `.agents/planner/goals/GOAL-0001/references/hero_room_reference.png` has Git blob SHA-1 `8d9a4c951b169458ceb85f9ad61107b99d59a909` and size 4,028,643 bytes. This does NOT establish a visual difference; recompression can change bytes. The committed source SHA-256/native dimensions and visual equivalence remain unverified. Do not copy the chat-source SHA-256 onto the committed file.

On the owner's local clone, an **authorized owner/reviewer** should run this non-destructive command and compare the result:
```bash
python -c "from pathlib import Path; import hashlib,struct; p=Path('.agents/planner/goals/GOAL-0001/references/hero_room_reference.png'); b=p.read_bytes(); assert b[:8]==bytes.fromhex('89504e470d0a1a0a'); print('committed_sha256',hashlib.sha256(b).hexdigest()); print('native_dimensions',struct.unpack('>II',b[16:24]))"
```
Resolve which version is canonical, confirm perspective/native scale and amend the exact request records before moving them to `requested`. Record dimensions per delivered file in its manifest, not the estimated canvas alone. The room's **1536×1024 output canvas** is distinct from the observed source-image pixel size.

### Disposition and duplicates: reviewed against catalog metadata only

- **Likely new art/specialist scope:** ART-0002 (clouds), 0003 (cliff foam), 0004 (four-view side walls), 0005 (four-view door), 0006 (sphere finial), 0007 (compass blanket), 0008 (headboard shelf), 0009 (wall shelf), 0010 (brass globe), 0011 (blue/white planter), 0012 (palms), 0013 (light shafts).
- **Reuse/compose/scale review FIRST:** ART-0014 (F007/F012/F013), ART-0015 (P005/P006 238×304 rug), ART-0016 (S017 320×158 directional shadow), ART-0017 (S013/S016), ART-0018 (S015 240×128), ART-0019 (P009 393×275), ART-0020 (P014 296×269), ART-0021 (P017 191×157). These are not cancelled automatically: metadata does not prove the registered art fits the required silhouette or angle. Narrow/cancel only *individual confirmed covered outputs* after actual specialist review.
- **Existing tracked bed request:** ART-0001 uses P001 as a reference, not a new P001 replacement; coordinate ART-0007 with it to avoid generating a second whole bed.
- ART-0008 and ART-0009 share the concept of shelves but have different mount interfaces (headboard versus wall); do not dedupe without checking mounting and proportions. ART-0010 O019 is an astrolabe, **not** an automatically approved brass globe.

### Codex / Claude Code handoff

Coding agents may check **metadata, hashes, JSON, task-state consistency**, implement animation/Y-sort/directional-view integration and validate *only externally delivered, reviewer-approved* sprites. In parallel worktrees, never both edit the same Map Factory files. Do **not** use source-art reading or automated art-generation tools in agent sessions. Start from `AGENTS.md` and `.agents/workflows/GRAPHICS.md`. Good first coding task is blocked `TASK-0033` (living background) when Codex availability returns; verify `TASK-0034` and `TASK-0035` remain passing rather than redoing them.

After a graphics specialist supplies real RGBA deliverables, use:
```bash
python tools/agent_workflow.py --check
python tools/art_delivery.py --check
python tools/map_factory_cli.py validate
python tools/run_tests.py --changed
```
Then integrate reviewed artwork with new versioned map data, capture a **real Godot image** and request owner visual approval. Preserve the five render levels; do not change characters/UI/gameplay for this goal.
