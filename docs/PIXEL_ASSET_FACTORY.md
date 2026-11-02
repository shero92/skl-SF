# Local built-in Pixel Art Asset Factory

This factory uses Codex's `imagegen` skill and the built-in `image_gen` tool only.
There is no external image API client, credential requirement or paid API fallback.
Python prepares jobs, imports tool outputs, validates them, and runs Godot. Python
cannot invoke a conversation-only Codex tool: an active Codex session executes each
prepared request. This is an agent-driven production queue, not an unattended daemon.

## Current plan

`tools/pixel_factory/production_plan.txt` preserves the owner's full 104-item plan.
`plan.json` expands it to 128 independent asset/facing specifications: the four bed
IDs already represent the four bed views; other rotatable furniture receives four
separate requests. Horizontal/vertical bench identities remain separate source IDs.
Non-floor dimensions are inferred and explicitly marked for review. Native sprite
canvas, ground footprint, anchor in pixels from top-left, and layer are independent.
West/east bed footprints are 4x3, south/north 3x4. The grid is always 64x64 pixels.
Layer names map to the supplied production plan, not a replacement for the published
Map Factory catalog schema. No generated candidate is auto-published to that catalog.

The original room is the primary reference. Existing owner-designated approved
G01/G02/G03 files are imported byte-for-byte, hashed and protected. Never regenerate
them to satisfy another placement. Up to one approved same-identity view is attached
for subsequent directional redraws. Every request has one unique prompt and one PNG
result; diagnostic repetition/direction/room sheets are local QA, not generated art.

## Run in the task worktree

Install Pillow if missing. Use `python` here because this host's `py -3` launcher
does not find its installed Python. Initialize Godot imports once:

```powershell
python tools/pixel_asset_factory.py compile
python tools/pixel_asset_factory.py preflight
# Godot must have imported the project before RoomFactory global classes are used.
$env:APPDATA = Join-Path (Get-Location) 'assets_generated/logs/godot_user'
Godot_v4.7.2-stable_win64.exe --headless --path . --editor --quit
python tools/pixel_asset_factory.py prepare G04 --test
```

Codex reads the returned `request.json`, visually inspects its local references,
and invokes `image_gen` once with the saved `arguments`. The tool initially saves
under Codex's generated_images directory; ingestion copies it into this project:

```powershell
python tools/pixel_asset_factory.py ingest <request.json> <saved-output.png> --execution-id <actual-tool-output-id>
```

Record the exact executed prompt in request.json before ingestion if a prompt was
refined. Never claim a synthetic fixture as a real tool execution. The execution ID
is an audit record supplied by the agent, not a cryptographic provider attestation.

The test creates native PNG + same-basename JSON, separate metadata index, raw
source, hashed references, request, repetition previews and actual RoomFactory
assembly/capture. A real rendering window may briefly appear for the capture.
The original and rendered room comparison is stored beside `room.png`. Native 64px
floor placement compensates for the previous texture's dimensions so legacy scales
cannot leave gaps. Published maps and existing scenes remain unchanged.

After the single-asset test passes:

```powershell
python tools/pixel_asset_factory.py next
```

This returns ONE next request. Codex repeats tool invocation then ingestion, serially.
No local script can autonomously launch built-in image generation outside Codex.
If the tool is unavailable or errors, stop or record the failure; do not use an API:

```powershell
python tools/pixel_asset_factory.py fail <request.json> --notes 'Tool unavailable'
```

## Limits, validation and approval

`max_requests` bounds persisted reservations, including failed calls; default 128.
`max_attempts_per_asset` defaults to 3. Each retry is a fresh independent tool call.
Pending requests block duplicate dispatch for the same asset. A filesystem lock
prevents simultaneous state mutations. An abandoned lock requires inspecting the
process before removal. Usage/cost stay unknown unless measured by the host; request
limits are not dollar guarantees. No API keys, billing lookup, or invented prices.

Native dimensions, valid PNG decoding, nonempty alpha, required transparency, naming,
categories, grid and anchors are checked. A required transparent source must already
contain alpha; padding an opaque rectangle cannot count as background removal.
Nearest-neighbor normalization preserves the raw result and records source/native
sizes. It does not prove handcrafted pixel quality. Transparent canvases may receive
padding without stretching/cropping; opaque aspect mismatch fails. Color/alpha
metrics assist review. Labels, single-object semantics, palette, lighting, perspective,
seams, pixel quality and direction consistency require visual review.

Only the owner/reviewer can mark a candidate approved after comparing source and
Godot room. Technical pass leaves `validated_pending_review`. Approval copies the
PNG into `approved/`, records reviewer/notes, and marks it completed. Rejection
quarantines the asset and marks `needs_regeneration`. All attempts are retained:

```powershell
python tools/pixel_asset_factory.py approve G04 --reviewer owner --notes 'Reviewed source versus Godot room'
python tools/pixel_asset_factory.py reject G04 --reviewer owner --notes 'Explain the visual defect'
```

There is deliberately no overwrite-approved switch. Use a new asset ID for a
separately authorized replacement. A changed config/plan invalidates the test gate;
run a fresh test before resuming production. Do not manually reset budget receipts.

## Verification

```powershell
python -m unittest discover -s tools/tests -p test_pixel_asset_factory.py -v
python tools/run_tests.py --changed
```

Offline tests use clearly marked fixture images and mocked Godot; the delivered G04
has a separate actual image_gen execution ID and actual Godot room capture. Library
completion requires all remaining assets to be generated and reviewed; compiling
prompts or passing the single test does not imply the entire library exists.
