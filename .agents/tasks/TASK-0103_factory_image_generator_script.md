---
id: TASK-0103
status: todo
owner: aider
agent: aider
priority: normal
branch: aider/task-0103
depends_on: none
issue: none
art_request: none
touches: tools/generate_factory_images.py,tools/tests/test_generate_factory_images.py,tools/test_map.json
test: python -m unittest discover -s tools/tests -p test_generate_factory_images.py
done_when: tools/generate_factory_images.py is a working, tested command line image generator with dry-run, resume, retry, checkpoint and insufficient-credit handling that makes no network call in tests and never approves art automatically.
estimate_minutes: 120
---
# Implement the factory image generator script

The file currently only prints that its implementation is missing. Replace it with a real implementation. Job files already exist in the repository folder `tools/factory_image_jobs/` (read them at runtime by building the path from parts; do not list them in any file you edit).

## Command line
- `python tools/generate_factory_images.py --jobs <job json> [--all | --id <item id>] [--dry-run] [--out-root <dir>] [--resume] [--max-retries N] [--checkpoint <json>]`
- Default out root is a directory given on the command line; do not hard-code a user path.
- `--dry-run`: load and validate jobs, print each request (model, size, prompt length, reference files, output path) and exit 0 without any network call and without writing images.

## Job file contract
- JSON object with `schema_version` 1, `provider` apimaster, `model`, and `items`: each item has `id`, `title`, `output` (relative path), `prompt`, `references` (list of relative paths), `size`, `background`, `native_size` [w, h], `protected` (bool).
- Reject items marked `protected` true unless `--allow-protected` is passed. Never overwrite an existing output file; write a new numbered candidate name instead.

## API behaviour (APIMaster images)
- Base URL from environment variable APIMASTER_BASE_URL, key from APIMASTER_API_KEY. Never print, log, store or write the key anywhere. Fail with a clear message if either is missing and not in dry-run.
- With references use a multipart POST to `/v1/images/edits`; without references use `/v1/images/generations`. Send an `Idempotency-Key` header derived from item id and a run id.
- Support both synchronous results (base64 or url) and asynchronous results: if a task id is returned, poll `/v1/tasks/{id}` with a delay and an overall timeout, then fetch the image.
- HTTP 402 or an insufficient credits message: stop the whole run immediately, save the checkpoint, print a short explanation, exit with a distinct non-zero code. Do not retry it. Treat HTTP 429 and 5xx as retryable with backoff up to `--max-retries`.

## Checkpoint and resume
- Write a checkpoint JSON after every item (status pending, done, failed, stopped_no_credits; output path; attempts; error text without secrets). `--resume` skips items already done.

## Validation of every downloaded image
- Must be a PNG. When background is transparent it must have an alpha channel with some fully transparent pixels. Record pixel size; do not resize or modify the file. Add a sidecar JSON next to the output with item id, model, prompt sha256, reference sha256 values, output sha256 and `visual_approval: false`. Never mark anything approved.

## Tests (no network)
- Use a fake transport object injected into the generator. Cover: dry-run writes nothing, missing key error, sync success, async polling success, 402 stops and saves checkpoint, 429 retried then succeeds, resume skips done items, protected item refused, existing output not overwritten, non-PNG rejected, key never appears in checkpoint or sidecar. Register a `tools/test_map.json` entry for the test.

## Acceptance
- `python tools/run_tests.py --changed` passes. No image files are created or changed by Aider. No paid call is made.

## Reply rules
Do not write the path or file name of any file that is not in `touches` anywhere in your reply or in the files you edit (not in prose, not in the `paths` list of the tools/test_map.json entry, not in comments): Aider treats such a mention as a request to add the file, discards your edits and asks again. In the test_map.json entry list in `paths` only files from `touches`; read other data files at runtime inside the test by constructing the path from parts. Use plain ASCII characters only in every reply, comment, string and file you write.
