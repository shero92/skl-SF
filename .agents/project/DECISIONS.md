# Material architectural decisions

- **ADR-001 — Single instruction entry:** root `AGENTS.md` is the common project contract. More detailed role/workflow guides live under `.agents/`; no duplicate root `CLAUDE.md` on Claude Code v2.1.277+. Older Claude installations need update or a small optional compatibility bridge.
- **ADR-002 — Task identity:** stable `TASK-####` Markdown record owns status, owner and evidence. The generated task board is a read-only projection; commits/PRs prove actual code changes.
- **ADR-003 — Graphics ownership:** production art belongs to a separate graphics specialist; coding agents only write ART specifications and integrate reviewed outputs.
- **ADR-004 — Art deduplication:** one `ART-####` request per distinct asset need, planned outputs recorded up front; delivered PNGs with hash manifests, quality signoff and map metadata before integration.
- **ADR-005 — Visual QA:** CI can verify files and metadata, not artistic parity. Preserve a real source image and actual Godot render for human comparison.
