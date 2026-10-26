# ChatGPT Hero Room sprite pack — 2026-10-26

**Status: DRAFTS ONLY, not production artwork.**

The user-authorized ChatGPT graphics conversation created a download named
`hero_room_art_pack_chatgpt_drafts_2026-10-26.zip`, containing 22 draft RGBA PNGs
and four original, unmodified image crops from the owner's style reference.
The 22 draft filenames correspond to requests ART-0002, ART-0003, ART-0006,
ART-0007, ART-0010, ART-0011, ART-0012, ART-0013, ART-0014,\nART-0015, ART-0016, ART-0017, and ART-0018 (some have multiple frames).
The ZIP also includes a full manifest with original file SHA-256 checksums,
pixel sizes, reviews and a contact sheet.

This repository deliberately stores NO binaries in this folder until their
actual bytes have been transferred from the ChatGPT chat. A GitHub text-only
connector can push these instructions but CANNOT access the locally generated
binary ZIP; a link in the chat is not a public GitHub-hosted asset.

## Exact upload (owner's machine or Work desktop with repository checkout)

1. Download `hero_room_art_pack_chatgpt_drafts_2026-10-26.zip` from the
   ChatGPT message. Do not substitute GitHub screenshots or synthesized PNGs.
2. In a local clone of `shero92/skl-SF`, run:

```bash
git switch main
git pull --ff-only
git switch -c art/chatgpt-hero-room-drafts-20261026
python tools/import_chatgpt_art_pack.py /path/to/hero_room_art_pack_chatgpt_drafts_2026-10-26.zip --dry-run
python tools/import_chatgpt_art_pack.py /path/to/hero_room_art_pack_chatgpt_drafts_2026-10-26.zip
python .agents/graphics/chatgpt_drafts/2026-10-26/verify_art_pack.py
python tools/run_tests.py --changed
git add .agents/graphics/chatgpt_drafts/2026-10-26
git commit -m "art: stage ChatGPT Hero Room drafts for review"
git push --set-upstream origin art/chatgpt-hero-room-drafts-20261026
```

Open a pull request from the pushed branch and review it. Keep all ART
requests at `blocked_reference` pending source provenance, owner scale and
independent visual QA. Do **not** copy draft files into `map_factory/parts/`,
edit the production catalog or rebuild maps automatically.

Codex and Claude Code can verify hashes, copy *unchanged* approved art and run
Godot tests; they must NEVER draw, repaint or generate new sprite graphics.
Artwork production is permitted only in the owner's authorized ChatGPT graphics
conversations or by a graphics specialist.
