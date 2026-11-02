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

class PlannerContext(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        (self.root/".agents/planner/goals/GOAL-0001").mkdir(parents=True)
        (self.root/".agents/planner/requests").mkdir(parents=True)
        (self.root/".agents/tasks").mkdir(parents=True)
        (self.root/"AGENTS.md").write_text("shared rules\n",encoding="utf-8")
        (self.root/".agents/planner/PROMPT_RULES.md").write_text("proposal rules\n",encoding="utf-8")
        (self.root/".agents/planner/goals/GOAL-0001/state.json").write_text(
            json.dumps({"milestones_approved":True}),encoding="utf-8")
        (self.root/".agents/planner/goals.json").write_text(json.dumps({"goals":[
            {"id":"GOAL-0001","title":"Approved","status":"active","outcome":"room",
             "verification":"owner signoff","constraints":"keep history",
             "steps":[
                 {"key":"finished","title":"Finished prerequisite","task_id":"TASK-0001","after":[],
                  "depends_on":[],"agent":"codex","priority":"critical","kind":"bug"},
                 {"key":"blocked-task","title":"Blocked assigned work","task_id":"TASK-0002","after":[],
                  "depends_on":[],"agent":"claude","priority":"high","kind":"feature","file":"tools/x.py",
                  "touches":["tools/x.py"],"test":"py -3 -m unittest","problem":"blocked evidence",
                  "done_when":"finish after prerequisite"},
                 {"key":"ready-next","title":"Ready unassigned work","after":["finished"],
                  "depends_on":[],"agent":"codex","priority":"high","kind":"feature","file":"tools/y.py",
                  "touches":["tools/y.py"],"test":"py -3 -m unittest","problem":"next work",
                  "done_when":"complete it"},
                 {"key":"waits-on-blocked","title":"Not ready","after":["blocked-task"],"depends_on":[],
                  "agent":"codex","priority":"low","kind":"feature"}]},
            {"id":"GOAL-0002","title":"Draft goal","status":"draft","steps":[{"key":"draft-step"}]}
        ]}),encoding="utf-8")
        self.write_task("TASK-0001","done",body="- Tests: passed")
        self.write_task("TASK-0002","blocked",body="- Blocker: waiting for reviewed measurements\n- Next: calibrate")
        self.write_task("TASK-0003","done",body="")
        self.write_request("REQ-open.json",{"status":"open","priority":"critical","title":"Open request",
            "problem":"observed issue","file":"tools/a.py","done_when":"fix it","test":"py -3 -m unittest",
            "kind":"bug","agent":"codex"})
        self.write_request("REQ-linked.json",{"status":"accepted","priority":"high","title":"Already tasked",
            "task_id":"TASK-0002","problem":"duplicate details"})
        self.write_request("REQ-finished.json",{"status":"accepted","priority":"high","title":"Finished request",
            "task_id":"TASK-0003"})

    def write_task(self,tid,status,body):
        path=self.root/".agents/tasks"/(tid+"_sample.md")
        path.write_text(f"---\nid: {tid}\nstatus: {status}\nbranch: test-branch\ndepends_on: none\n---\n## Evidence / handoff\n{body}\n",encoding="utf-8")

    def write_request(self,name,data):
        (self.root/".agents/planner/requests"/name).write_text(json.dumps(data),encoding="utf-8")

    def test_context_selects_open_requests_and_approved_current_goal_with_blockers(self):
        sections=local_planner.planner_sections(self.root)
        context="\n\n".join(sections)
        self.assertLessEqual(len(context),local_planner.CONTEXT_LIMIT)
        self.assertIn("open request REQ-open",context)
        self.assertNotIn("REQ-finished",context)
        self.assertIn("approved goal GOAL-0001",context)
        self.assertNotIn("draft-step",context)
        step=next(s for s in sections if s.startswith("--- approved goal step blocked-task"))
        data=json.loads(step.split("\n",1)[1])
        self.assertEqual(data["task_status"],"blocked")
        self.assertIn("waiting for reviewed measurements"," ".join(data["task_evidence"]))
        ready=next(s for s in sections if s.startswith("--- approved goal step ready-next"))
        self.assertTrue(json.loads(ready.split("\n",1)[1])["ready"])
        self.assertFalse(any("waits-on-blocked" in s for s in sections))
        self.assertEqual(sections,local_planner.planner_sections(self.root),"selection must be deterministic")

    def test_context_limit_drops_complete_low_priority_records(self):
        self.write_request("REQ-open-small.json",{"status":"open","priority":"low","title":"Small request"})
        full=local_planner.planner_sections(self.root)
        mandatory=full[:3]  # shared instructions and the approved goal summary
        first=next(s for s in full if s.startswith("--- open request REQ-open ---"))
        limit=len("\n\n".join(mandatory))+len(first)+2
        limited=local_planner.planner_sections(self.root,limit)
        rendered="\n\n".join(limited)
        self.assertLessEqual(len(rendered),limit)
        self.assertIn(first,limited)
        self.assertNotIn("Small request",rendered)
        for section in limited[3:]:
            if section.startswith("--- ") and " ---\n{" in section:
                json.loads(section.split("\n",1)[1])

    def test_task_state_index_reads_only_referenced_task_files(self):
        for tid in ("TASK-0004","TASK-0005","TASK-0006"):
            self.write_task(tid,"todo","")
        from unittest.mock import patch
        with patch.object(local_planner,"task_fields",wraps=local_planner.task_fields) as read_task:
            result=local_planner.task_state_index(self.root,["TASK-0004"])
        self.assertEqual(set(result),{"TASK-0004"})
        read_task.assert_called_once()

    def test_project_instruction_size_and_shared_skill_pointer(self):
        repo=Path(__file__).resolve().parents[2]
        self.assertLessEqual(len((repo/"AGENTS.md").read_text(encoding="utf-8")),3500)
        wrapper=(repo/".claude/skills/goal-task-factory/SKILL.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/goal-task-factory/SKILL.md",wrapper)
        self.assertLess(len(wrapper),500)

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
        for mode in ("unchanged", "cooldown", "rejected", "failure", "success", "merged", "ci_failed", "unsafe_diff"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp, ExitStack() as stack:
                base=Path(tmp)
                config={"planning_enabled":True,"schedule":[],"auto_merge_planning":mode in ("merged", "ci_failed", "unsafe_diff")}
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
                    if argv[:3]==["gh","pr","checks"]:
                        return SimpleNamespace(stdout="",stderr="",returncode=1 if mode=="ci_failed" else 0)
                    if argv[:3]==["gh","pr","diff"]:
                        path="tools/arbitrary.py" if mode=="unsafe_diff" else ".agents/tasks/TASK-0011_new.md"
                        return SimpleNamespace(stdout=path,stderr="",returncode=0)
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
                with patch.object(local_planner,"refresh_main") as refresh:
                    local_planner.run("claude")
                    self.assertEqual(refresh.call_count,1 if mode=="merged" else 0)
                self.assertEqual(any(e[0]=="ai" for e in events), mode not in ("unchanged","cooldown"))
                self.assertTrue(any(e[0]=="git" and e[1][0]=="commit" for e in events))
                self.assertTrue(any(e[0]=="git" and e[1][0]=="push" for e in events))
                logs=[p for p in (base/"runs").glob("*.json") if not p.stem.endswith(("-pulse","-proposal"))]
                self.assertEqual(json.loads(logs[0].read_text())["pulse"]["created"],["TASK-0011"])

class PlannerMainRefresh(unittest.TestCase):
    def test_refresh_requires_lock_clean_main_and_verified_commit(self):
        from unittest.mock import patch
        import agent_runner as ar
        from contextlib import contextmanager
        events=[]
        @contextmanager
        def locked(label):
            events.append(("lock",label))
            yield
            events.append(("unlock",label))
        def git(*args):
            events.append(("git",args))
            return "main" if args[0]=="branch" else ""
        with patch.object(ar,"exclusive",locked),patch.object(ar,"main_commit") as commit,patch.object(local_planner,"git",git):
            local_planner.refresh_main("claude")
            commit.assert_called_once_with("chore: refresh generated outputs after planning","claude","planning",verify=True)
        self.assertEqual(events[0],("lock","main-merge"))
        self.assertIn(("git",("pull","--ff-only","origin","main")),events)
        self.assertEqual(events[-1],("unlock","main-merge"))
        for branch,dirty in (("task", ""),("main"," M tools/changed.py")):
            with patch.object(ar,"exclusive",locked),patch.object(ar,"main_commit") as commit,patch.object(local_planner,"git",side_effect=[branch,dirty]):
                with self.assertRaisesRegex(RuntimeError,"clean main"):local_planner.refresh_main("codex")
                commit.assert_not_called()

    def test_planning_allowlist_rejects_generated_files_and_code(self):
        self.assertTrue(local_planner.planning_path(".agents/tasks/TASK-0011_plan.md"))
        self.assertTrue(local_planner.planning_path(".agents/planner/goals.json"))
        for bad in ("tools/code.py",".agents/tasks/FILES.md","tools/FILES.md",".agents/project/TASKS.md"):
            self.assertFalse(local_planner.planning_path(bad))

if __name__=="__main__":
    unittest.main()
