"""Static and isolated proposal tests; never call a subscription or make Git pushes."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
class PlannerSafety(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)
        (self.root/".agents/tasks").mkdir(parents=True)
        (self.root/".agents/planner/goals/GOAL-0001").mkdir(parents=True)
        (self.root/"map_factory/scripts").mkdir(parents=True)
        (self.root/"map_factory/scripts/room_factory.gd").write_text("extends Node\n")
        self.env={**os.environ,"SKL_PLANNER_ROOT":str(self.root)}
    def apply(self,proposal,okay):
        data=self.root/"proposal.json"
        data.write_text(json.dumps(proposal),encoding="utf8")
        x=subprocess.run([sys.executable,str(ROOT/"tools/goal_task_factory.py"),
            "apply-proposal",str(data),"--run-key","test"],cwd=self.root,env=self.env,
            capture_output=True,text=True)
        self.assertEqual(x.returncode==0,okay,x.stderr)
        return x
    def task(self,**overrides):
        d={"title":"Repair wall", "problem":"observed wrong geometry",
           "file":"map_factory/scripts/room_factory.gd","done_when":"unit test passes",
           "test":"python -m unittest","priority":"high","kind":"bug",
           "agent":"codex","depends_on":[],"goal_id":"GOAL-0001"}
        d.update(overrides)
        return d
    def test_draft_goal_refused_without_partial_writes(self):
        self.apply({"tasks":[self.task()],"updates":[]},False)
        self.assertEqual(list((self.root/".agents/tasks").glob("TASK-*.md")),[])
    def test_owner_approval_allows_task_and_deduplicates(self):
        state={"status":"active","milestones_approved":True}
        (self.root/".agents/planner/goals/GOAL-0001/state.json").write_text(json.dumps(state))
        p={"tasks":[self.task()],"updates":[]}
        self.apply(p,True)
        self.apply(p,True)
        self.assertEqual(len(list((self.root/".agents/tasks").glob("TASK-*.md"))),1)
    def test_reject_art_and_unsafe_file(self):
        self.apply({"tasks":[self.task(file="map_factory/parts/ui/example.png")],"updates":[]},False)
        self.apply({"tasks":[self.task(agent="specialist",kind="art")],"updates":[]},False)
    def test_limit_4_per_run(self):
        self.apply({"tasks":[self.task()]*5,"updates":[]},False)
    def test_local_cli_flags_and_no_paid_provider_required(self):
        c=(ROOT/"tools/local_planner.py").read_text()
        self.assertIn('"--permission-mode", "plan"',c)
        self.assertIn('"--sandbox", "read-only"',c)
        self.assertIn('BANNED_ENV',c)
        self.assertIn('SKL_PLANNER_ROOT', (ROOT/"tools/goal_task_factory.py").read_text())
    def test_automation_disabled_by_default(self):
        cfg=json.loads((ROOT/".agents/planner/config.json").read_text())
        self.assertFalse(cfg["auto_activate"])
        self.assertFalse(cfg["execution_enabled"])
        self.assertEqual([s["agent"] for s in cfg["schedule"]],["claude","codex","claude","codex"])
    def test_codex_null_optionals_apply_as_absent(self):
        state={"status":"active","milestones_approved":True}
        (self.root/".agents/planner/goals/GOAL-0001/state.json").write_text(json.dumps(state))
        raw=json.dumps({"tasks":[self.task(line=None,touches=None)],"updates":[]})
        self.apply(local_planner.clean_data(raw,"codex"),True)

sys.path.insert(0,str(ROOT/"tools"))
import local_planner  # noqa: E402

class CodexStrictSchema(unittest.TestCase):
    def test_every_property_required_and_optionals_nullable(self):
        original=local_planner.schema()
        strict:dict=local_planner.strict_schema(original)  # type: ignore[assignment]
        def objects(node):
            if isinstance(node,dict):
                if "properties" in node:yield node
                for v in node.values():yield from objects(v)
            elif isinstance(node,list):
                for v in node:yield from objects(v)
        for obj in objects(strict):
            self.assertEqual(sorted(obj["required"]),sorted(obj["properties"]))
            self.assertIs(obj["additionalProperties"],False)
        task=strict["properties"]["tasks"]["items"]["properties"]
        self.assertEqual(task["goal_id"]["type"],["string","null"])
        self.assertEqual(task["touches"]["type"],["array","null"])
        self.assertEqual(task["line"]["type"],["integer","null"])
        self.assertEqual(task["title"]["type"],"string")
        self.assertNotIn("null",str(task["priority"]))
        self.assertEqual(original,local_planner.schema(),"Claude/validator schema must stay unchanged")
        self.assertNotIn("line",original["properties"]["tasks"]["items"]["required"])
    def test_nullable_without_type_uses_any_of(self):
        self.assertEqual(local_planner.nullable({"enum":["a"]}),{"anyOf":[{"enum":["a"]},{"type":"null"}]})
    def test_clean_data_drops_null_keys(self):
        raw=json.dumps({"tasks":[{"title":"t","line":None,"goal_id":None,"touches":["a"]}],
                        "updates":[{"task_id":"TASK-0001","reason":None}]})
        data=local_planner.clean_data(raw,"codex")
        self.assertEqual(data["tasks"],[{"title":"t","touches":["a"]}])
        self.assertEqual(data["updates"],[{"task_id":"TASK-0001"}])
    def test_stderr_tail_redacts_and_truncates(self):
        text="x"*3000+" Authorization: Bearer abc.def token=s3cr3t sk-proj1234567890abcd ghp_ABCDEFGH12345 schema error"
        tail=local_planner.stderr_tail(text)
        self.assertLessEqual(len(tail),1200)
        self.assertTrue(tail.endswith("schema error"))
        for secret in ("abc.def","s3cr3t","sk-proj1234567890abcd","ghp_ABCDEFGH12345"):
            self.assertNotIn(secret,tail)
        self.assertEqual(local_planner.stderr_tail(None),"")

if __name__=="__main__":
    unittest.main()
