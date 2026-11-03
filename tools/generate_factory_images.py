"""Factory image generator (APIMaster images API).

Generates CANDIDATE art only. Nothing is ever approved here: every sidecar records
visual_approval false and the owner must review the picture.

    python tools/generate_factory_images.py --jobs <job json> --all --dry-run
    python tools/generate_factory_images.py --jobs <job json> --id ART-0031 --out-root <dir> --resume

Environment: APIMASTER_BASE_URL, APIMASTER_API_KEY (never printed, logged or stored).
Exit codes: 0 ok, 1 some item failed, 2 usage/config error, 3 insufficient credits (run stopped).
"""
import argparse
import base64
import hashlib
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXIT_OK, EXIT_FAILED, EXIT_USAGE, EXIT_CREDITS = 0, 1, 2, 3
DONE_WORDS = {"succeeded", "success", "completed", "complete", "done"}
FAIL_WORDS = {"failed", "error", "cancelled", "canceled"}


class CreditsExhausted(Exception):
    pass


class ApiError(Exception):
    def __init__(self, message, retryable=False):
        super().__init__(message)
        self.retryable = retryable


class UrllibTransport:
    """Real HTTP transport. request() returns (status, body_bytes)."""

    def __init__(self, base_url, api_key, timeout=120):
        self.base_url, self.api_key, self.timeout = base_url.rstrip("/"), api_key, timeout

    def request(self, method, path, headers=None, json_body=None, fields=None, files=None):
        headers = dict(headers or {})
        headers["Authorization"] = "Bearer " + self.api_key
        body = None
        if files is not None or fields is not None:
            boundary = uuid.uuid4().hex
            headers["Content-Type"] = "multipart/form-data; boundary=" + boundary
            parts = []
            for key, value in (fields or {}).items():
                parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"\r\n\r\n%s\r\n"
                              % (boundary, key, value)).encode())
            for key, name, data in (files or []):
                parts.append(("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\n"
                              "Content-Type: image/png\r\n\r\n" % (boundary, key, name)).encode() + data + b"\r\n")
            parts.append(("--%s--\r\n" % boundary).encode())
            body = b"".join(parts)
        elif json_body is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(json_body).encode()
        url = path if path.startswith("http") else self.base_url + path
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as err:
            return err.code, err.read()
        except (urllib.error.URLError, TimeoutError) as err:
            raise ApiError("network error: %s" % type(err).__name__, retryable=True)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def load_jobs(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("items"), list):
        raise ValueError("job file needs schema_version 1 and an items list")
    if data.get("provider") != "apimaster":
        raise ValueError("job file provider must be apimaster")
    if not data.get("model"):
        raise ValueError("job file needs a model")
    seen = set()
    for item in data["items"]:
        for key in ("id", "title", "output", "prompt", "size", "native_size"):
            if key not in item:
                raise ValueError("item missing %s" % key)
        if item["id"] in seen:
            raise ValueError("duplicate item id " + item["id"])
        seen.add(item["id"])
        out = Path(item["output"])
        if out.is_absolute() or ".." in out.parts:
            raise ValueError("output must be a relative path without '..': " + item["output"])
    return data


def pick_items(data, ids, all_items):
    if all_items:
        return list(data["items"])
    chosen = [i for i in data["items"] if i["id"] in set(ids or [])]
    missing = set(ids or []) - {i["id"] for i in chosen}
    if missing or not chosen:
        raise ValueError("unknown or no item selected: %s" % sorted(missing or ids or []))
    return chosen


def validate_png(data, transparent):
    """Return (width, height) or raise ValueError. The file is never modified."""
    if not data.startswith(PNG_MAGIC):
        raise ValueError("not a PNG")
    from PIL import Image
    image = Image.open(io.BytesIO(data))
    image.load()
    if transparent:
        rgba = image.convert("RGBA")
        if "A" not in image.getbands() and "transparency" not in image.info:
            raise ValueError("expected transparency but the PNG has no alpha channel")
        if rgba.getchannel("A").getextrema()[0] != 0:
            raise ValueError("expected transparent pixels but none are fully transparent")
    return image.size


def candidate_path(out_root, relative):
    target = Path(out_root) / relative
    if not target.exists():
        return target
    n = 2
    while True:
        alt = target.with_name("%s_%02d%s" % (target.stem, n, target.suffix))
        if not alt.exists():
            return alt
        n += 1


class Generator:
    def __init__(self, transport, model, out_root, checkpoint, sleep=time.sleep, clock=time.monotonic,
                 max_retries=3, timeout=300, poll_interval=3, run_id=None, repo_root=None, log=print):
        self.t, self.model, self.out_root = transport, model, Path(out_root)
        self.checkpoint_path, self.sleep, self.clock = Path(checkpoint), sleep, clock
        self.max_retries, self.timeout, self.poll_interval = max_retries, timeout, poll_interval
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.repo_root = Path(repo_root or Path(__file__).resolve().parents[1])
        self.log = log
        self.state = {"run_id": self.run_id, "items": {}}
        if self.checkpoint_path.exists():
            self.state = json.loads(self.checkpoint_path.read_text(encoding="utf-8"))

    def save(self):
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(json.dumps(self.state, indent=1), encoding="utf-8", newline=chr(10))

    def mark(self, item_id, **fields):
        entry = self.state["items"].setdefault(item_id, {"status": "pending", "attempts": 0})
        entry.update(fields)
        self.save()

    def call(self, method, path, **kwargs):
        status, body = self.t.request(method, path, **kwargs)
        if status == 402 or b"insufficient" in body.lower()[:400] and b"credit" in body.lower()[:400]:
            raise CreditsExhausted("insufficient credits")
        if status == 429 or status >= 500:
            raise ApiError("HTTP %d" % status, retryable=True)
        if status >= 400:
            raise ApiError("HTTP %d" % status)
        return body

    def request_image(self, item):
        refs = []
        for ref in item.get("references", []):
            ref_path = self.repo_root / ref
            if not ref_path.is_file():
                raise ApiError("missing reference file: " + ref)
            refs.append(ref_path)
        key = {"Idempotency-Key": "%s-%s" % (item["id"], self.run_id)}
        fields = {"model": self.model, "prompt": item["prompt"], "size": item["size"], "n": "1"}
        if item.get("background") == "transparent":
            fields["background"] = "transparent"
            fields["output_format"] = "png"
        if refs:
            files = [("image[]", p.name, p.read_bytes()) for p in refs]
            body = self.call("POST", "/v1/images/edits", headers=key, fields=fields, files=files)
        else:
            payload = dict(fields, n=1)
            body = self.call("POST", "/v1/images/generations", headers=key, json_body=payload)
        return self.resolve(body)

    def resolve(self, body):
        """Turn a response into PNG bytes; handles sync data and async task ids."""
        start = self.clock()
        while True:
            doc = json.loads(body.decode("utf-8", "replace"))
            data = doc.get("data")
            if isinstance(data, list) and data:
                return self.extract(data[0])
            status = str(doc.get("status", "")).lower()
            task_id = doc.get("task_id") or doc.get("id")
            if status in FAIL_WORDS:
                raise ApiError("generation failed: " + str(doc.get("error", status))[:200])
            if status in DONE_WORDS and doc.get("output"):
                out = doc["output"]
                return self.extract(out[0] if isinstance(out, list) else out)
            if not task_id:
                raise ApiError("unrecognised response shape")
            if self.clock() - start > self.timeout:
                raise ApiError("timed out waiting for task", retryable=True)
            self.sleep(self.poll_interval)
            body = self.call("GET", "/v1/tasks/%s?model=%s" % (task_id, self.model))

    def extract(self, entry):
        if isinstance(entry, dict) and entry.get("b64_json"):
            return base64.b64decode(entry["b64_json"])
        url = entry.get("url") if isinstance(entry, dict) else entry
        if not url:
            raise ApiError("response has no image")
        return self.call("GET", url)

    def run_item(self, item, protected_ok):
        iid = item["id"]
        if item.get("protected") and not protected_ok:
            self.mark(iid, status="failed", error="protected item refused (use --allow-protected)")
            return False
        attempts = self.state["items"].get(iid, {}).get("attempts", 0)
        last = ""
        while attempts < self.max_retries:
            attempts += 1
            self.mark(iid, status="pending", attempts=attempts)
            try:
                data = self.request_image(item)
                size = validate_png(data, item.get("background") == "transparent")
            except CreditsExhausted:
                self.mark(iid, status="stopped_no_credits")
                raise
            except ApiError as err:
                last = str(err)
                if not err.retryable:
                    break
                self.sleep(min(2 ** attempts, 30))
                continue
            except Exception as err:  # invalid PNG, bad JSON, missing PIL
                last = "%s: %s" % (type(err).__name__, str(err)[:160])
                break
            return self.store(item, data, size, attempts)
        self.mark(iid, status="failed", error=last or "failed")
        return False

    def store(self, item, data, size, attempts):
        target = candidate_path(self.out_root, item["output"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        refs = {}
        for ref in item.get("references", []):
            refs[ref] = sha256_bytes((self.repo_root / ref).read_bytes())
        sidecar = {"item_id": item["id"], "model": self.model, "run_id": self.run_id,
                   "prompt_sha256": sha256_bytes(item["prompt"].encode("utf-8")),
                   "reference_sha256": refs, "output_sha256": sha256_bytes(data),
                   "pixel_size": list(size), "native_size": item["native_size"],
                   "visual_approval": False}
        target.with_suffix(".json").write_text(json.dumps(sidecar, indent=1), encoding="utf-8", newline=chr(10))
        self.mark(item["id"], status="done", output=str(target), attempts=attempts, error=None)
        self.log("done %s -> %s (%dx%d, not approved)" % (item["id"], target, size[0], size[1]))
        return True

    def run(self, items, resume, protected_ok):
        failed = False
        for item in items:
            if resume and self.state["items"].get(item["id"], {}).get("status") == "done":
                self.log("skip %s (done)" % item["id"])
                continue
            if item["id"] in self.state["items"]:
                self.state["items"][item["id"]]["attempts"] = 0
            try:
                failed = (not self.run_item(item, protected_ok)) or failed
            except CreditsExhausted:
                self.log("Insufficient credits: run stopped. Checkpoint saved; add credits and use --resume.")
                return EXIT_CREDITS
        return EXIT_FAILED if failed else EXIT_OK


def dry_run(data, items, out_root, log=print):
    for item in items:
        log("%s model=%s size=%s prompt_chars=%d refs=%s output=%s%s" % (
            item["id"], data["model"], item["size"], len(item["prompt"]),
            ",".join(item.get("references", [])) or "none", Path(out_root) / item["output"],
            " PROTECTED" if item.get("protected") else ""))
    log("dry-run: %d item(s), no network call, nothing written" % len(items))


def main(argv=None, transport=None, env=None, sleep=time.sleep):
    env = os.environ if env is None else env
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--id", action="append")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out-root", default="generated_candidates")
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--poll-interval", type=float, default=3)
    parser.add_argument("--allow-protected", action="store_true")
    args = parser.parse_args(argv)
    try:
        data = load_jobs(args.jobs)
        if not args.all and not args.id:
            raise ValueError("choose --all or --id <item id>")
        items = pick_items(data, args.id, args.all)
    except (ValueError, OSError, json.JSONDecodeError) as err:
        print("error: %s" % err, file=sys.stderr)
        return EXIT_USAGE
    if args.dry_run:
        dry_run(data, items, args.out_root)
        return EXIT_OK
    if transport is None:
        base, key = env.get("APIMASTER_BASE_URL"), env.get("APIMASTER_API_KEY")
        if not base or not key:
            print("error: set APIMASTER_BASE_URL and APIMASTER_API_KEY (values are never printed)", file=sys.stderr)
            return EXIT_USAGE
        transport = UrllibTransport(base, key)
    checkpoint = args.checkpoint or str(Path(args.out_root) / "checkpoint.json")
    gen = Generator(transport, data["model"], args.out_root, checkpoint, sleep=sleep,
                    max_retries=args.max_retries, timeout=args.timeout, poll_interval=args.poll_interval)
    return gen.run(items, args.resume, args.allow_protected)


if __name__ == "__main__":
    sys.exit(main())
