import base64
import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import generate_factory_images as gen

KEY = "sk-test-secret-value"


def png_bytes(alpha=True, size=(8, 8), transparent_pixel=True):
    image = Image.new("RGBA" if alpha else "RGB", size, (200, 150, 80, 255) if alpha else (200, 150, 80))
    if alpha and transparent_pixel:
        image.putpixel((0, 0), (0, 0, 0, 0))
    out = io.BytesIO()
    image.save(out, "PNG")
    return out.getvalue()


def sync_response(data):
    return (200, json.dumps({"data": [{"b64_json": base64.b64encode(data).decode()}]}).encode())


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def request(self, method, path, headers=None, json_body=None, fields=None, files=None):
        self.calls.append((method, path, headers, json_body, fields, files))
        return self.responses.pop(0)


class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "ref.png").write_bytes(png_bytes())
        self.item = {"id": "A1", "title": "t", "output": "out/a1.png", "prompt": "draw", "size": "1024x1024",
                     "background": "transparent", "native_size": [64, 128], "references": ["ref.png"],
                     "protected": False}
        self.jobs_path = self.root / "jobs.json"
        self.write_jobs([self.item])
        self.sleeps = []

    def write_jobs(self, items):
        doc = {"schema_version": 1, "provider": "apimaster", "model": "gpt-image-2", "items": items}
        self.jobs_path.write_text(json.dumps(doc), encoding="utf-8")

    def generator(self, responses, **kwargs):
        transport = FakeTransport(responses)
        made = gen.Generator(transport, "gpt-image-2", self.root / "out_root", self.root / "cp.json",
                             sleep=self.sleeps.append, repo_root=self.root, log=lambda *_: None, **kwargs)
        return made, transport

    def test_dry_run_makes_no_call_and_writes_nothing(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = gen.main(["--jobs", str(self.jobs_path), "--all", "--dry-run",
                             "--out-root", str(self.root / "out_root")], env={})
        self.assertEqual(code, 0)
        self.assertFalse((self.root / "out_root").exists())

    def test_missing_key_is_a_config_error(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = gen.main(["--jobs", str(self.jobs_path), "--all"], env={})
        self.assertEqual(code, gen.EXIT_USAGE)

    def test_sync_success_writes_candidate_and_sidecar(self):
        made, transport = self.generator([sync_response(png_bytes())])
        self.assertEqual(made.run([self.item], False, False), 0)
        out = self.root / "out_root/out/a1.png"
        self.assertTrue(out.is_file())
        side = json.loads(out.with_suffix(".json").read_text())
        self.assertFalse(side["visual_approval"])
        self.assertEqual(transport.calls[0][1], "/v1/images/edits")
        self.assertIn("A1-", transport.calls[0][2]["Idempotency-Key"])

    def test_no_references_uses_generations_endpoint(self):
        item = dict(self.item, references=[])
        made, transport = self.generator([sync_response(png_bytes())])
        self.assertEqual(made.run([item], False, False), 0)
        self.assertEqual(transport.calls[0][1], "/v1/images/generations")

    def test_async_polling_success(self):
        task = (200, json.dumps({"task_id": "T9", "status": "pending"}).encode())
        done = (200, json.dumps({"status": "succeeded",
                                 "output": [{"b64_json": base64.b64encode(png_bytes()).decode()}]}).encode())
        made, transport = self.generator([task, task, done])
        self.assertEqual(made.run([self.item], False, False), 0)
        self.assertEqual(transport.calls[1][0], "GET")
        self.assertIn("/v1/tasks/T9?model=gpt-image-2", transport.calls[1][1])
        self.assertEqual(len(self.sleeps), 2)

    def test_402_stops_run_and_saves_checkpoint(self):
        second = dict(self.item, id="A2", output="out/a2.png")
        made, transport = self.generator([(402, b"{}")])
        self.assertEqual(made.run([self.item, second], False, False), gen.EXIT_CREDITS)
        self.assertEqual(len(transport.calls), 1)
        saved = json.loads((self.root / "cp.json").read_text())
        self.assertEqual(saved["items"]["A1"]["status"], "stopped_no_credits")
        self.assertNotIn("A2", saved["items"])

    def test_403_insufficient_quota_is_treated_as_no_credits(self):
        body = b'{"error":{"message":"Insufficient balance","code":"insufficient_user_quota"}}'
        made, transport = self.generator([(403, body)])
        self.assertEqual(made.run([self.item], False, False), gen.EXIT_CREDITS)
        self.assertEqual(len(transport.calls), 1)

    def test_429_is_retried_then_succeeds(self):
        made, transport = self.generator([(429, b"{}"), sync_response(png_bytes())])
        self.assertEqual(made.run([self.item], False, False), 0)
        self.assertEqual(len(transport.calls), 2)
        self.assertEqual(len(self.sleeps), 1)

    def test_resume_skips_done_items(self):
        made, _ = self.generator([sync_response(png_bytes())])
        made.run([self.item], False, False)
        again, transport = self.generator([])
        self.assertEqual(again.run([self.item], True, False), 0)
        self.assertEqual(transport.calls, [])

    def test_protected_item_refused_without_flag(self):
        item = dict(self.item, protected=True)
        made, transport = self.generator([])
        self.assertEqual(made.run([item], False, False), gen.EXIT_FAILED)
        self.assertEqual(transport.calls, [])

    def test_protected_item_allowed_with_flag(self):
        item = dict(self.item, protected=True)
        made, transport = self.generator([sync_response(png_bytes())])
        self.assertEqual(made.run([item], False, True), 0)
        self.assertEqual(len(transport.calls), 1)

    def test_existing_output_is_never_overwritten(self):
        target = self.root / "out_root/out/a1.png"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"keep me")
        made, _ = self.generator([sync_response(png_bytes())])
        made.run([self.item], False, False)
        self.assertEqual(target.read_bytes(), b"keep me")
        self.assertTrue((self.root / "out_root/out/a1_02.png").is_file())

    def test_non_png_and_opaque_png_rejected(self):
        for payload in (b"not a png", png_bytes(alpha=False), png_bytes(transparent_pixel=False)):
            made, _ = self.generator([sync_response(payload)])
            self.assertEqual(made.run([self.item], False, False), gen.EXIT_FAILED)
            self.assertEqual(json.loads((self.root / "cp.json").read_text())["items"]["A1"]["status"], "failed")
            (self.root / "cp.json").unlink()
        self.assertFalse((self.root / "out_root/out/a1.png").exists())

    def test_secret_never_in_checkpoint_or_sidecar(self):
        made, _ = self.generator([sync_response(png_bytes())])
        made.run([self.item], False, False)
        stored = (self.root / "cp.json").read_text() + (self.root / "out_root/out/a1.json").read_text()
        self.assertNotIn(KEY, stored)

    def test_job_file_rejects_bad_paths_and_duplicates(self):
        self.write_jobs([dict(self.item, output="../escape.png")])
        with self.assertRaises(ValueError):
            gen.load_jobs(self.jobs_path)
        self.write_jobs([self.item, self.item])
        with self.assertRaises(ValueError):
            gen.load_jobs(self.jobs_path)

    def test_repository_art_0031_job_is_valid_and_not_protected(self):
        job = Path(__file__).resolve().parents[1] / "factory_image_jobs" / "ART-0031_back_wall_window.json"
        data = gen.load_jobs(job)
        self.assertFalse(any(i.get("protected") for i in data["items"]))


if __name__ == "__main__":
    unittest.main()
