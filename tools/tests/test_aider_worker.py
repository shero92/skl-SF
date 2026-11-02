import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import aider_worker


class AiderWorkerTests(unittest.TestCase):

    def test_only_aider_tasks_are_eligible(self):
        tasks = {
            "TASK-0001": {
                "id": "TASK-0001",
                "agent": "codex",
                "status": "todo",
                "depends_on": "none",
            },
            "TASK-0002": {
                "id": "TASK-0002",
                "agent": "aider",
                "status": "todo",
                "depends_on": "none",
            },
        }
        self.assertFalse(aider_worker.eligible(tasks["TASK-0001"], tasks))
        self.assertTrue(aider_worker.eligible(tasks["TASK-0002"], tasks))

    def test_reject_unauthorized_file_changes(self):
        with self.assertRaises(RuntimeError):
            aider_worker.validate_changed(
                ["tools/unrelated.py"],
                ["tools/aider_worker.py"],
            )

    def test_reject_graphics_changes(self):
        with self.assertRaises(RuntimeError):
            aider_worker.validate_changed(
                ["assets/character.png"],
                ["assets"],
            )

    def test_automation_disabled_by_default(self):
        with patch.object(
            aider_worker,
            "read_json",
            return_value={"aider_execution_enabled": False},
        ):
            with self.assertRaises(RuntimeError):
                aider_worker.run_task({"id": "TASK-0071"})


if __name__ == "__main__":
    unittest.main()
