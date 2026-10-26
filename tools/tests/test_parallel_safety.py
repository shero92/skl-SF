import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(TOOLS))
import runner_safety as rs
import agent_workflow as aw

class ParallelSafety(unittest.TestCase):
    def test_same_or_ancestor_touches_conflict(self):
        self.assertTrue(rs.overlaps("map_factory/scripts","map_factory/scripts/room_factory.gd"))
        self.assertFalse(rs.overlaps("map_factory/scripts/a.gd","map_factory/scripts/a.gd.bak"))
    def test_changes_cannot_touch_art_or_generated(self):
        for bad in ("map_factory/parts/walls/W001.png","tools/INDEX.md",
                    ".agents/project/ACTIVE.md","map_factory/scripts/../characters/a.gd",
                    "scenes/ui.gd"):
            with self.assertRaises(ValueError):
                rs.allowed_changed([bad],["map_factory/","tools/","scenes/"])
        self.assertTrue(rs.allowed_changed(["tools/example.py"],["tools/example.py"]))
        with self.assertRaises(ValueError):
            rs.allowed_changed(["tools/other.py"],["tools/example.py"])
    def test_strict_touches_and_one_active_task_per_agent(self):
        other={"id":"TASK-1233","status":"in_progress","agent":"codex",
               "touches":"map_factory/scripts"}
        current={"id":"TASK-1234","status":"todo","agent":"claude",
                 "depends_on":"none","touches":"map_factory/scripts/room_factory.gd"}
        with self.assertRaisesRegex(ValueError,"Touch conflict"):
            rs.verify_claim(current,{"TASK-1233":other})
        current["touches"]="tools/tests/test_map_factory.py"
        self.assertEqual(rs.verify_claim(current,{"TASK-1233":other}),["tools/tests/test_map_factory.py"])
        current["agent"]="codex"
        with self.assertRaisesRegex(ValueError,"one active"):
            rs.verify_claim(current,{"TASK-1233":other})
    def test_execution_only_with_supervised_evidence(self):
        # Invariant, not a default: a real supervised run may enable execution.
        cfg=json.loads((TOOLS.parent/".agents/planner/config.json").read_text())
        self.assertEqual(rs.supervised_problems(cfg,TOOLS.parent),[])
    def evidence_root(self,status):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        (root/".agents/tasks").mkdir(parents=True)
        (root/".agents/tasks/TASK-0009_x.md").write_text("---\nid: TASK-0009\nstatus: "+status+"\n---\n")
        return root
    def test_supervised_invariant_rejects_hand_set_flags(self):
        root=self.evidence_root("done")
        good={"task":"TASK-0009","agent":"codex","merge_sha":"a"*40,"verified_at":"2026-10-26T00:00:00+00:00"}
        self.assertEqual(rs.supervised_problems({"execution_enabled":False,"supervised_e2e_passed":False},root),[])
        self.assertEqual(rs.supervised_problems({"execution_enabled":True,"supervised_e2e_passed":True,
                                                 "supervised_e2e":good},root),[])
        bad=[({"execution_enabled":True,"supervised_e2e_passed":False},"requires supervised_e2e_passed"),
             ({"supervised_e2e_passed":True},"runner evidence"),
             ({"supervised_e2e_passed":True,"supervised_e2e":{**good,"merge_sha":"92b89a6"}},"full commit SHA"),
             ({"supervised_e2e_passed":True,"supervised_e2e":{**good,"task":"TASK-9"}},"TASK-####"),
             ({"supervised_e2e_passed":True,"supervised_e2e":{**good,"agent":"owner"}},"claude or codex"),
             ({"supervised_e2e_passed":True,"supervised_e2e":{**good,"task":"TASK-0010"}},"not done")]
        for cfg,message in bad:
            with self.subTest(message=message):
                self.assertTrue(any(message in p for p in rs.supervised_problems(cfg,root)),cfg)
        blocked=self.evidence_root("blocked")
        self.assertIn("supervised_e2e.task TASK-0009 is not done",
                      rs.supervised_problems({"supervised_e2e_passed":True,"supervised_e2e":good},blocked))
    def test_supervised_success_writes_evidence(self):
        import agent_runner
        root=self.evidence_root("done")
        path=root/"config.json"
        path.write_text(json.dumps({"execution_enabled":False,"supervised_e2e_passed":False,"graphics_issue_enabled":True}))
        cfg=agent_runner.record_supervised(path,"TASK-0009","codex","b"*40)
        self.assertEqual(json.loads(path.read_text()),cfg)
        self.assertFalse(cfg["execution_enabled"],"enabling execution stays an owner decision")
        self.assertTrue(cfg["graphics_issue_enabled"])
        self.assertEqual(rs.supervised_problems(cfg,root),[])
        self.assertEqual(rs.supervised_problems({**cfg,"execution_enabled":True},root),[])
        with self.assertRaisesRegex(RuntimeError,"Execution disabled"):
            agent_runner.execution_gate(cfg)
        with self.assertRaisesRegex(RuntimeError,"evidence invalid"):
            agent_runner.execution_gate({"execution_enabled":True,"supervised_e2e_passed":True})
        text=(TOOLS/"agent_runner.py").read_text()
        self.assertIn("if supervised:\n                # Only a real, fully validated supervised run",text)
    def test_runner_never_bypasses_sandbox(self):
        text=(TOOLS/"agent_runner.py").read_text()
        self.assertIn('"workspace-write"',text)
        self.assertIn('"acceptEdits"',text)
        self.assertNotIn('dangerously-skip-permissions',text)
        self.assertNotIn('dangerously-bypass-approvals',text)
        self.assertIn('execution_enabled',text)
        self.assertIn('git("revert","-m","1"',text)
    def test_first_supervised_run_requires_interactive_owner_consent(self):
        code=(TOOLS/"agent_runner.py").read_text(encoding="utf8")
        self.assertIn('mode.add_argument("--supervised"',code)
        self.assertIn("sys.stdin.isatty()",code)
        self.assertIn('typed != "SUPERVISE "+tid',code)
        self.assertIn("supervised_e2e_passed",code)

    def test_pickup_selects_highest_priority_without_ai(self):
        import agent_runner as ar
        from unittest.mock import patch
        queue={"TASK-0100":{"id":"TASK-0100","status":"todo","agent":"codex",
             "touches":"tools/tests/a.py","depends_on":"none",
             "text":"**Priority:** normal"},
             "TASK-0101":{"id":"TASK-0101","status":"todo","agent":"codex",
             "touches":"tools/tests/b.py","depends_on":"none",
             "text":"**Priority:** high"}}
        with patch.object(ar,"records",return_value=queue):
            self.assertEqual(ar.pick_next("codex"),"TASK-0101")
            self.assertIsNone(ar.pick_next("claude"))
    def test_execution_schedule_is_opt_in(self):
        content=(TOOLS/"setup_local_planner.ps1").read_text(encoding="utf8")
        self.assertIn("[switch]$InstallExecution",content)
        self.assertIn("supervised_e2e_passed",content)
        self.assertIn("execution_enabled",content)
        self.assertIn("$execPrefix",content)

    def test_untrusted_task_test_cannot_inject_shell(self):
        rs.safe_test(["python","-m","unittest","discover","-s","tools/tests"])
        for cmd in (["powershell","-Command","Remove-Item"],
                    ["python","-c","print(42)"],["python","-m","pip","install","bad"]):
            with self.assertRaises(ValueError):
                rs.safe_test(cmd)
    def test_dotted_task_test_becomes_runnable_discover(self):
        # TASK-0009 failed: "-m unittest tools.tests.test_map_layers" cannot import siblings.
        base=["py","-3","-m","unittest"]
        disc=base+["discover","-s","tools/tests","-p"]
        self.assertEqual(rs.normalize_test(base+["tools.tests.test_map_layers"]),disc+["test_map_layers.py"])
        self.assertEqual(rs.normalize_test(base+["-v","tools/tests/test_map_layers.py"]),disc+["test_map_layers.py","-v"])
        self.assertEqual(rs.normalize_test(base+["tools.tests.test_map_layers.FiveLevelMap.test_reject_cyclic_mount"]),
                         disc+["test_map_layers.py","-k","FiveLevelMap.test_reject_cyclic_mount"])
        for unchanged in (base+["discover","-s","tools/tests","-p","test_map_layers.py"],
                          base+["tools.tests.test_a","tools.tests.test_b"],base+["other.module"]):
            self.assertEqual(rs.normalize_test(unchanged),unchanged)
        self.assertEqual(rs.normalize_test_text("py -3 -m unittest tools.tests.test_map_layers"),
                         "py -3 -m unittest discover -s tools/tests -p test_map_layers.py")
        self.assertEqual(rs.normalize_test_text("python tools/map_factory_cli.py validate"),
                         "python tools/map_factory_cli.py validate")
    def test_normalized_task_command_runs(self):
        root=Path(__file__).resolve().parents[2]
        argv=rs.normalize_test(["py","-3","-m","unittest","tools.tests.test_map_navigation"])
        x=subprocess.run([sys.executable,*argv[2:]],cwd=root,capture_output=True,text=True)
        self.assertEqual(x.returncode,0,x.stderr[-800:])
        self.assertRegex(x.stderr,r"Ran [1-9]\d* tests?")
    def test_costs_aggregate_per_goal_and_preserve_unknown(self):
        summary=rs.receipt_goals([{"task_id":"TASK-0008","cost_usd":None,"tokens":None},
              {"task_id":"TASK-0009","cost_usd":0.42,
               "tokens":{"input_tokens":123,"output_tokens":45}}],
              {"TASK-0008":"GOAL-0001","TASK-0009":"GOAL-0001"})
        self.assertEqual(summary[0]["unknown_cost_receipts"],1)
        self.assertEqual(summary[0]["known_usd"],0.42)

if __name__=="__main__":
    unittest.main()
