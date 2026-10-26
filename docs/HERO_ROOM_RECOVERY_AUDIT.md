# Hero Room recovery baseline and execution gates

Owner-approved recovery plan, 2026-10-26. Metadata/code audit only; no restricted image inspection or visual approval.

## Verified baseline
- Main includes Hero Room v0011 and Courtyard v0002. Registry validation passed.
- 238 catalog records: 214 environment, 12 characters, 12 UI. All records needs_cleanup; zero ready. Environment paths exist; no duplicate IDs or paths.
- Nine HD assets W021/W022, A017/A018, D019, P023-P026 are registered and placed. Style approval is distinct from production approval.
- Hero Room has 84 placements, 15 mounts, no explicit facing sets, grid placements or motion metadata. Legacy scale-based composition remains.
- Compiled passes: background 5, ground overlays 2, walls 40, decorations 37, shadows 27. Floor cells render separately.
- Only 2 of 38 architecture placements have effective collision enabled. Navigation is provisional.
- 26 placement contracts are provisional; no reviewed measurements exist.
- Source path/hash in the map remain null. Goal reference identity relative to original 1448x1086 upload remains unconfirmed. 1536x1024 is output canvas, not source size.
- ART-0001 through ART-0021 remain blocked_reference. No delivery manifests found. Twenty newer requests name 50 outputs, plus the bed request; these are not produced sprites.
- TASK-0033 merged in PR #31, merge 850fe77cbabc0f88b2a34520a67b6a76a414d020. Full hosted Godot smoke passed before merge. Room motion configuration still remains.
- Optional world_y_sort and static mount resolution exist. Moving-owner lifecycle and assembled occlusion need dedicated tests.
- Shadow helpers store initial owner metadata/position; room construction uses ordinary create_shadow. No runtime follower is established by those helpers.
- goal_qa.py and capture_map_previews.gd are hardcoded to v0010. Current-version capture and intermediate/final gate separation require TASK-0037.
- Catalog pivot edits change regenerated historical graphs: immutable resolved metadata needs TASK-0039 before measurement integration.

## Locked product decisions
- Original 1448x1086 image governs composition; accepted nine HD sprites govern craftsmanship.
- Visible authored views first; no claim of four-way reuse without four independent views.
- Keep the existing Godot 2D rectangular logical grid. Calibrate before proposing projection changes.
- Preserve rejected 22 low-detail drafts as rejected; do not integrate them or replace HD bytes.
- Coding agents receive text measurements and approved manifests, never inspect or synthesize production artwork.

## Seven phases
1. Audit/source identity: TASK-0036 and existing TASK-0001; preserve TASK-0033 merge evidence.
2. Delivery readiness: calibrated reuse and request amendment, proposed TASK-0038.
3. Geometry contracts: measured pivots/interfaces and historical graph protection, proposed TASK-0039.
4. Sorting/mounts/shadows: existing g1-m6-sort-mount, proposed TASK-0040.
5. Approved delivery integration and next immutable room reconstruction, proposed TASK-0041/0042.
6. Environment collision/navigation then owner visual acceptance, proposed TASK-0043/0044.
7. Second-room data-only reuse proof, proposed TASK-0045, after first-room acceptance.

## Production gates and parallel work
TASK-0037 capture tooling can proceed beside source confirmation. Historical metadata safety can proceed beside specialist calibration. Renderer/compiler/catalog/map writers run serially with non-overlapping claims; one active task per agent in isolated image-free worktrees. Specialist art is independent. No policy or execution configuration is changed by this plan.

## Completion
Authenticated source and new immutable map linked; every critical visible component approved or explicitly omitted by owner; measured strict placement; compatible seams and real authored used views; verified mounts/occlusion/shadows/motion; complete environment collision/navigation; Python/registry/Godot checks pass; owner signs the real source-versus-Godot comparison with no unresolved critical defects. First-room acceptance does not complete deferred views or the broader multi-room goal.

## Costs and evidence
Existing Claude API-equivalent receipt estimates: TASK-0008 $0.397005; TASK-0034 $0.319695; TASK-0035 $0.171417. These are not subscription bills. Other costs remain unknown. Use targeted contexts, small batches and actual receipts, never invented budgets.

## Explicit blockers
Owner/specialist must authenticate the source and supply reviewed calibration/delivery records. No production asset is promoted or map rewritten by this audit. New milestones are stored as a draft proposed_revision in goals.json; existing source keys are retained.
