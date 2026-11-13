# Story workflow

The story lives in `docs/story/`. Read [docs/story/INDEX.md](../../docs/story/INDEX.md) first, then only the file for the scene you are building ([docs/story/README.md](../../docs/story/README.md) is the status table and the list of open decisions). Never read all chapters.

## When it applies

Any task that touches story events, dialogue, characters, creatures, boss or battle design, locations, cutscenes or a map that is meant to be a story place. Pure tooling and Map Factory work does not need it.

## Rules

1. **Only approved text is fact.** Build what is marked **[معتمد]** or what the owner says in chat. **[مقترح]**, **[تطويري]** and **[مفتوح]** text is a draft: you may use it as a placeholder if the task says so, never as final content, and never present it as approved.
2. **Do not decide open questions.** Silent Gate Forest timing, the end of chapter 1, final names and looks (for example the team dragon), and everything in `chapter_02/` are the owner's. Ask once, briefly, or leave the item out and say so.
3. **Do not reveal secrets early** (the list is in `docs/story/shared/visions_creatures_and_secrets.md`). Dialogue and art must not show them either.
4. **Maps and map art follow the story file too, through a map brief** ([docs/MAP_GRAPHICS_RULES.md](../../docs/MAP_GRAPHICS_RULES.md)).
   **Art follows the story file too.** A graphics request for a character, creature or place quotes the story file it comes from and keeps to the camera rule in [GRAPHICS.md](GRAPHICS.md). Story text never replaces a visual reference the owner supplied.
5. **Changing the story is the owner's call.** When the owner approves a change, update the affected chapter file and `docs/story/INDEX.md` (new row for a new file, `chapter_NN/NN_short_slug.md`), keep the marker on every changed line, and list the changed files in the task report. Do not copy chapter text into `AGENTS.md`, README files or task records; link to it.
6. **Story files prove nothing about the game.** Say "written in `docs/story/`" until a task, a test and a real Godot run show it implemented.
7. Language: story text is Arabic with English proper names; keep names exactly as written (`Bone-Tide Shore`, `Temple of the First Seal`, `Neru`, `Reef Friend`, and so on).

## Task record

A story-driven task names the story file in its `touches` or body. Tests are the normal ones for the code or data it changes (`python tools/run_tests.py --changed`).
