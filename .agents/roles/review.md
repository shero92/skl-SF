# Owner / reviewer

- Check changed files and linked PR/commit, not just agent completion claims.
- For graphics: inspect the final assembled-room comparison sheet and review the scripted QA, manifest hashes, native dimensions, anchors and real independently rendered facings. Individual piece images use scripted QA, not agent visual opening. The owner decides visual acceptance; local Blender production by Codex/Claude and the external pixel-art workspace follow GRAPHICS.md.
- For code: require targeted tests and review scope boundaries; no unverified visual claims.
- Approve art and code separately. Mark art integrated only after registration, Godot validation and human review.
- After merge, record *one* concise entry in `../project/CHANGELOG.md`; keep detailed history in Git.
