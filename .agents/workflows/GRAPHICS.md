# Graphics production workflow â€” local Blender environment blocks

## Owner authorization (2026-10-28)
Codex and Claude Code may both perform assigned environment graphics tasks on the owner's PC. Use local scripted Blender modeling/rendering to produce reusable pixel-art blocks, tiles, furniture, foliage and separate shadows. This is an authorized producer role, not a requirement to wait for an external artist. Character, portrait, UI and gameplay work is excluded.

The authorized workspace and canonical generated asset destination is `H:\shining force\pixel-art`. Use `<TASK-ID>/<ART-ID-or-candidate>/<revision>/` with separate `source/`, `renders/` and `qa/` folders. Save editable `.blend` projects, PNG masters/native sprites, shadows and SHA-256 manifests there. Never overwrite a prior revision or another agent's files.

## Required workflow
1. Claim one TASK and reference its deduplicated ART request. Read only relevant text records/catalog and compare existing IDs before creating replacements. A request is not completed art.
2. Verify the authenticated reference path/hash. Preserve the original and the nine accepted HD assets; do not infer authenticity from dimensions alone.
3. Write/edit reproducible Blender builders/specs, run Blender locally and regenerate outputs. Python may orchestrate builds, process alpha/alignment, calculate hashes and run technical QA. Godot may assemble/capture an unapproved candidate. No AI image service or API key is required; use one only if the owner explicitly asks.
4. Run scripted checks of every output's dimensions, alpha, clipping, palette, footprint, anchors, facing and shadow direction. Render upright facings independently from the Blender model; never mirror/rotate a bitmap to invent a perspective view. Visible required facings come first; defer unused views explicitly.
5. Save `.blend` sources, rendered assets and `manifest.json` in the external workspace. Keep portable script/spec changes under version control. Record tool versions, exact source/spec paths, task/ART, reference hash, output hashes/dimensions/anchors/footprint/facing and actual cost or `unknown`.
6. Existing helpers may require repo-relative `--out` or texture paths. In that case use a new request/candidate staging directory in the repo for that helper, preserve the canonical generated assets in the external workspace, and record both paths/hashes. Do not claim that permissions alone add external-path support to a helper.
7. Build the actual room and produce a genuine Godot comparison sheet. Individual parts are checked by scripted QA; agent image viewing is limited to the assembled comparison. Numerical similarity and technical QA never count as visual approval.
8. Set produced work to `delivered`/`review`, not `ready`/approved. Owner approval of the final assembled-room comparison remains mandatory. Integration uses a reviewed manifest, stable IDs and a new immutable map revision; never write directly over `map_factory/parts` or old maps.

## States and handoff
Requests follow `blocked_reference -> requested -> in_progress -> delivered -> reviewed -> integrated`, or `cancelled` with evidence. Missing reference, measurement, executable or host permission blocks only its affected task. Do not call Blender unsupported solely because the agent is Codex or Claude. Producer, independent review and owner acceptance remain distinct; no self-approval or automatic art merge.

A handoff names the external workspace revision, repo staging path (if any), source/spec commit, manifest and capture paths, observed QA and unresolved defects. A PR containing scripts is not proof that its PNG outputs or full-room capture were produced.

## Permission boundary
Project settings add only the owner-named external workspace. Keep normal sandbox/approval mode, existing hooks, credentials and protected character/UI paths. Do not use `danger-full-access`, skip-permissions switches or unrestricted shell allow rules. A manually launched graphics-capable session can use its scoped tools; a launcher that explicitly removes Bash or hides assets still needs a separate reviewed implementation change. Report that distinction instead of silently changing launcher code in a rules-only task.
