import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "agent_costs.py"

class CostTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)
        self.root = Path(self.d.name)
        self.env = {**os.environ, "SKL_COST_ROOT": str(self.root)}

    def invoke(self, *args, event=None):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args],
                              env=self.env, input=json.dumps(event) if event is not None else None,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return proc.stdout

    def receipts(self):
        return list((self.root / ".agents/monitoring/receipts").glob("TASK-*.json"))

    def test_codex_rate_and_transcript(self):
        self.invoke("start", "TASK-0099", "--agent", "codex")
        log = self.root / "codex.jsonl"
        entries = [
            {"timestamp": "2099-01-01T00:00:00Z", "type": "session_meta", "payload": {}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {
                "total_token_usage": {"input_tokens": 1000, "cached_input_tokens": 500, "output_tokens": 100}}}}
        ]
        log.write_text("\n".join(json.dumps(x) for x in entries) + "\n")
        prices = self.root / ".agents/monitoring/pricing.json"
        prices.parent.mkdir(parents=True, exist_ok=True)
        prices.write_text(json.dumps({"models": {"test": {
            "input_per_million": 2, "cached_input_per_million": 1, "output_per_million": 10}}}))
        self.invoke("hook", "--agent", "codex", event={"session_id": "sample", "model": "test",
                                                        "transcript_path": str(log)})
        self.invoke("finish")
        receipt = json.loads(self.receipts()[0].read_text())
        self.assertEqual(receipt["cost_usd"], 0.0025)
        self.assertEqual(receipt["tokens"]["input_tokens"], 1000)
        self.assertNotIn("transcript_path", self.receipts()[0].read_text())
        self.invoke("report", "--check")

    def test_claude_statusline_no_fabricated_tokens(self):
        self.invoke("start", "TASK-0098", "--agent", "claude")
        self.invoke("hook", "--agent", "claude", "--statusline",
                    event={"session_id": "example", "model": {"id": "claude-test"},
                           "cost": {"total_cost_usd": 0.42}})
        self.invoke("finish")
        receipt = json.loads(self.receipts()[0].read_text())
        self.assertEqual(receipt["cost_usd"], 0.42)
        self.assertIsNone(receipt["tokens"])
        self.assertEqual(receipt["coverage"], "partial")

    def test_no_id_creates_local_test_receipt(self):
        response = self.invoke("start", "--agent", "claude")
        self.assertIn("TEST-", response)
        self.invoke("hook", "--agent", "claude", event={
            "session_id": "test-only", "cost": {"total_cost_usd": 0.10}})
        self.invoke("finish")
        local_receipts = list((self.root / ".agents/monitoring/.local/test_receipts").glob("TEST-*.json"))
        self.assertEqual(len(local_receipts), 1)
        self.assertEqual(json.loads(local_receipts[0].read_text())["cost_usd"], 0.10)
        self.assertFalse(self.receipts())
        summary = json.loads((self.root / ".agents/monitoring/summary.json").read_text())
        self.assertEqual(summary["tasks"], [])
        self.invoke("report", "--check")

    def test_claude_transcript_fallback_with_cache_prices(self):
        self.invoke("start", "TASK-0096", "--agent", "claude")
        log = self.root / "claude.jsonl"
        log.write_text(json.dumps({
            "timestamp": "2099-01-01T00:00:00Z",
            "type": "assistant",
            "message": {"id": "msg-1", "model": "claude-opus-5-5",
                        "usage": {"input_tokens": 1000, "cache_read_input_tokens": 500,
                                  "cache_creation_input_tokens": 300,
                                  "cache_creation": {"ephemeral_1h_input_tokens": 100},
                                  "output_tokens": 100}}
        }) + "\n")
        pricing = self.root / ".agents/monitoring/pricing.json"
        pricing.parent.mkdir(parents=True, exist_ok=True)
        pricing.write_text(json.dumps({"models": {"claude-opus-5-5": {
            "input_per_million": 4, "cached_input_per_million": 0.2,
            "output_per_million": 20, "cache_creation_5m_per_million": 5,
            "cache_creation_1h_per_million": 8}}}))
        self.invoke("hook", "--agent", "claude",
                    event={"session_id": "test", "transcript_path": str(log)})
        diagnostic = json.loads(self.invoke("diagnose"))
        self.assertTrue(diagnostic["sessions"][0]["tokens_found"])
        self.assertFalse(diagnostic["sessions"][0]["statusline_cost_found"])
        self.invoke("finish")
        receipt = json.loads(self.receipts()[0].read_text())
        self.assertEqual(receipt["tokens"]["input_tokens"], 1800)
        self.assertEqual(receipt["cost_usd"], 0.0079)
        self.assertEqual(receipt["coverage"], "complete")
        self.assertIn("claude_api_equivalent_estimate", receipt["source"])

    def test_import_codex_exec_json_and_deduplicate_session(self):
        self.invoke("start", "--agent", "codex")
        path = self.root / "codex-exec.jsonl"
        path.write_text("\n".join(json.dumps(event) for event in [
            {"type": "thread.started", "thread_id": "abc123"},
            {"type": "turn.started"},
            {"type": "turn.completed", "usage": {
                "input_tokens": 1200, "cached_input_tokens": 100,
                "output_tokens": 250}},
            {"type": "turn.completed", "usage": {
                "input_tokens": 700, "cached_input_tokens": 200,
                "output_tokens": 100}}
        ]) + "\n")
        pricing = self.root / ".agents/monitoring/pricing.json"
        pricing.parent.mkdir(parents=True, exist_ok=True)
        pricing.write_text(json.dumps({"models": {"test-model": {
            "input_per_million": 2, "cached_input_per_million": 1,
            "output_per_million": 10}}}))
        self.invoke("import-codex", str(path), "--model", "test-model")
        self.invoke("import-codex", str(path), "--model", "test-model")
        self.invoke("finish")
        receipt = json.loads(list((self.root / ".agents/monitoring/.local/test_receipts").glob("TEST-*.json"))[0].read_text())
        self.assertEqual(receipt["session_count"], 1)
        self.assertEqual(receipt["tokens"]["input_tokens"], 1900)
        self.assertEqual(receipt["tokens"]["output_tokens"], 350)
        self.assertEqual(receipt["cost_usd"], 0.007)
        self.assertEqual(receipt["coverage"], "complete")
        self.assertNotIn("abc123", json.dumps(receipt))

    def test_unknown_is_not_zero(self):
        self.invoke("start", "TASK-0097", "--agent", "codex")
        self.invoke("finish")
        doc = json.loads((self.root / ".agents/monitoring/summary.json").read_text())
        self.assertEqual(doc["missing_cost_receipts"], 1)
        self.assertEqual(doc["tasks"][0]["known_usd"], 0)

if __name__ == "__main__":
    unittest.main()
