# Handoff in five short fields

Before switching agents/sessions, change the task source file only if meaningful state changed, regenerate dashboards, and leave:

1. **Task:** ID, state, owner and branch/PR.
2. **Changed:** exact files or commit/PR URL, not repeated code.
3. **Verified:** commands/tests actually run and pass/fail evidence.
4. **Blocked:** explicit blockers, related ART requests/owner, missing reference if any.
5. **Next:** one actionable next step.

Do not copy whole conversation transcripts or duplicate background in every task. New agents read `../project/TASKS.md` → selected task file → feature index. If art is blocked, read `../graphics/QUEUE.md` → selected ART request, never produce the PNG yourself.
