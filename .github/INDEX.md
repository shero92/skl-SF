# GitHub automation index

- [workflows/INDEX.md](workflows/INDEX.md): purpose and risk level of GitHub Actions workflows.
- [copilot-instructions.md](copilot-instructions.md): GitHub Copilot-specific instruction file; keep consistent with root `AGENTS.md`.
- **Current risk:** some workflows commit generated map data or screenshot outputs back to `main` on push. Agents should work on isolated branches and submit PRs; do not assume workflows are read-only.
- Distinguish metadata-valid/tests-pass from source-versus-render visual approval.

[All directory entries](FILES.md).
