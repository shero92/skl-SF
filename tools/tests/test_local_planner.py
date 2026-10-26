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
    def test_request_record_touches_allowed_but_binary_and_deliveries_rejected(self):
        good=[".agents/graphics/requests/", ".agents/graphics/QUEUE.md"]
        # goal_id absent is the manual/non-goal proposal form.
        task=self.task(touches=good)
        task.pop("goal_id")
        self.apply({"tasks":[task],"updates":[]},True)
        bad=[".agents/graphics/deliveries/a.md", ".agents/graphics/requests/a.py", "tools/a.bin"]
        bad += ["tools/a"+ext for ext in local_planner_safety.IMAGE_EXT]
        for path in bad:
            with self.subTest(path=path):
                self.apply({"tasks":[{**task,"touches":[path]}],"updates":[]},False)

    def test_ai_extras_share_daily_and_run_caps_with_pulse(self):
        task=self.task()
        task.pop("goal_id")
        runs=self.root/".agents/planner/runs"
        runs.mkdir()
        (runs/"test-pulse.json").write_text(json.dumps({"created":["TASK-0900"]}))
        (self.root/".agents/planner/config.json").write_text(json.dumps({"max_tasks_per_run":2}))
        proposal={"tasks":[{**task,"problem":"extra task "+str(i)} for i in range(3)],"updates":[]}
        self.assertEqual(len(json.loads(self.apply(proposal,True).stdout)["created"]),1)
        (runs/"test-pulse.json").unlink()
        self.assertEqual(len(json.loads(self.apply(proposal,True).stdout)["created"]),2)
        self.assertEqual(json.loads(self.apply(proposal,True).stdout)["created"],[])

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
        # Execution may only be on with runner-recorded supervised evidence.
        self.assertEqual(local_planner_safety.supervised_problems(cfg,ROOT),[])
        self.assertEqual([s["agent"] for s in cfg["schedule"]],["claude","codex","claude","codex"])
    def test_planner_dotted_test_is_stored_runnable(self):
        state={"status":"active","milestones_approved":True}
        (self.root/".agents/planner/goals/GOAL-0001/state.json").write_text(json.dumps(state))
        self.apply({"tasks":[self.task(test="py -3 -m unittest tools.tests.test_map_layers")],"updates":[]},True)
        text=next((self.root/".agents/tasks").glob("TASK-*.md")).read_text(encoding="utf-8")
        self.assertIn("test: py -3 -m unittest discover -s tools/tests -p test_map_layers.py",text)
        self.assertNotIn("tools.tests.test_map_layers",text)
    def test_codex_null_optionals_apply_as_absent(self):
        state={"status":"active","milestones_approved":True}
        (self.root/".agents/planner/goals/GOAL-0001/state.json").write_text(json.dumps(state))
        raw=json.dumps({"tasks":[self.task(line=None,touches=None)],"updates":[]})
        self.apply(local_planner.clean_data(raw,"codex"),True)

sys.path.insert(0,str(ROOT/"tools"))
import local_planner  # noqa: E402
import runner_safety as local_planner_safety  # noqa: E402

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

class PlannerPulseRun(unittest.TestCase):
    def test_pulse_precedes_ai_and_commits_when_ai_skipped_or_rejected(self):
        from unittest.mock import patch
        from contextlib import ExitStack
        from types import SimpleNamespace
        for mode in ("unchanged", "cooldown", "rejected", "failure", "success"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
                base=Path(tmp)
                config={"planning_enabled":True,"schedule":[],"auto_merge_planning":False}
                events=[]
                def load(path, default):
                    if path == local_planner.CONFIG: return config
                    if path.name == "checkpoint.json": return {"digest":"same" if mode=="unchanged" else "old"}
                    if path.name == "cooldowns.json" and mode=="cooldown":
                        return {a:{"retry_after":"2999-01-01T00:00:00+01:00"} for a in ("claude","codex")}
                    return default
                def git(*args):
                    events.append(("git",args))
                    if args[:2] == ("branch","--show-current"): return "main"
                    if args[:3] == ("diff","--cached","--name-only"): return ".agents/tasks/TASK-0011_new.md"
                    return ""
                def invoke(argv, **kwargs):
                    events.append(("invoke",argv))
                    if "pulse" in argv: return SimpleNamespace(stdout='{"created":["TASK-0011"]}',stderr="",returncode=0)
                    if "apply-proposal" in argv:
                        return SimpleNamespace(stdout='{"created":[],"updated":[]}',stderr="rejected",returncode=1 if mode=="rejected" else 0)
                    return SimpleNamespace(stdout="https://github.com/example/pull/1",stderr="",returncode=0)
                def ai(*args):
                    events.append(("ai",args))
                    self.assertTrue(any(e[0]=="invoke" and "pulse" in e[1] for e in events))
                    return {"agent":"claude","exit":1 if mode=="failure" else 0,
                            "stdout":'{"tasks":[],"updates":[]}',"error":"failure",
                            "duration_seconds":1,"usage":None,"api_equivalent_usd":None}
                for name,value in (("BASE",base),("load",load),("git",git),("invoke",invoke),
                                   ("digest",lambda:"same"),("context",lambda:"context"),("local_ai",ai)):
                    stack.enter_context(patch.object(local_planner,name,value))
                # This is an isolated Windows-run simulation, also exercised on Linux CI.
                stack.enter_context(patch.object(local_planner,"os",SimpleNamespace(name="nt")))
                local_planner.run("claude")
                self.assertEqual(any(e[0]=="ai" for e in events), mode not in ("unchanged","cooldown"))
                self.assertTrue(any(e[0]=="git" and e[1][0]=="commit" for e in events))
                self.assertTrue(any(e[0]=="git" and e[1][0]=="push" for e in events))
                logs=[p for p in (base/"runs").glob("*.json") if not p.stem.endswith(("-pulse","-proposal"))]
                self.assertEqual(json.loads(logs[0].read_text())["pulse"]["created"],["TASK-0011"])

if __name__=="__main__":
    unittest.main()
