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
            {"timestamp": "2099-01-01T00:00:00Z", "type": "turn_context", "payload": {"model": "test"}},
            {"type": "event_msg", "payload": {"type": "token_count", "info": {
                "total_token_usage": {"input_tokens": 1000, "cached_input_tokens": 500, "output_tokens": 100}}}}
        ]
        log.write_text("\n".join(json.dumps(x) for x in entries) + "\n")
        prices = self.root / ".agents/monitoring/pricing.json"
        prices.parent.mkdir(parents=True, exist_ok=True)
        prices.write_text(json.dumps({"models": {"test": {
            "input_per_million": 2, "cached_input_per_million": 1, "output_per_million": 10}}}))
        self.invoke("hook", "--agent", "codex", event={"session_id": "sample",
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

    def test_unknown_is_not_zero(self):
        self.invoke("start", "TASK-0097", "--agent", "codex")
        self.invoke("finish")
        doc = json.loads((self.root / ".agents/monitoring/summary.json").read_text())
        self.assertEqual(doc["missing_cost_receipts"], 1)
        self.assertEqual(doc["tasks"][0]["known_usd"], 0)

if __name__ == "__main__":
    unittest.main()
