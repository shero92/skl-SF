"""Manual coordinator behavior with fake task executors, no production AI/art."""
from contextlib import nullcontext
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import manual_agents as manual
import agent_runner as ar


class ManualSessionTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.root=Path(temp.name)
        (self.root/".agents/tasks").mkdir(parents=True)
        self.bind=manual.bind_runner(self.root);self.bind.__enter__();self.addCleanup(self.bind.__exit__,None,None,None)
        for name,value in [("execution_gate",lambda config:None),("read_json",lambda path,default:{"execution_timeout_seconds":1}),
                           ("coordination_lock",lambda:nullcontext()),("cooling_until",lambda agent:None),("refresh_queue",lambda agent:False)]:
            p=patch.object(ar,name,value);p.start();self.addCleanup(p.stop)
        self.task("TASK-0001","codex","tools/a.py")

    def task(self,tid,agent,path,depends="none",status="todo",extra=""):
        text=f"---\nid: {tid}\nstatus: {status}\nowner: unassigned\nbranch: none\nagent: {agent}\ntouches: {path}\ndepends_on: {depends}\ntest: python -m unittest\nart_request: none\n{extra}---\n**Priority:** high\n"
        (self.root/f".agents/tasks/{tid}_task.md").write_text(text,encoding="utf-8",newline="\n")

    def finish(self,task,deadline):
        file=task["file"];file.write_text(file.read_text().replace("status: todo","status: done"),newline="\n")
        return {"phase":"done"}

    def test_idle_has_no_model_invocation(self):
        self.task("TASK-0001","codex","tools/a.py",status="done")
        with patch.object(manual,"execute_task") as run:
            result=manual.run_batch(self.root,["codex"])
        self.assertEqual(result["attempted"],0);run.assert_not_called()

    def test_success_unlocks_dependent_in_same_session(self):
        self.task("TASK-0002","codex","tools/b.py",depends="TASK-0001")
        result=manual.run_batch(self.root,["codex"],executor=self.finish)
        self.assertEqual([r["task"]for r in result["results"]],["TASK-0001","TASK-0002"])

    def test_count_limit_is_global_across_agents(self):
        self.task("TASK-0002","claude","tools/b.py")
        self.task("TASK-0003","codex","tools/c.py")
        result=manual.run_batch(self.root,["codex","claude"],max_tasks=2,executor=self.finish)
        self.assertEqual(result["attempted"],2)
        self.assertEqual(manual.records(self.root)["TASK-0003"]["status"],"todo")

    def test_independent_agents_actually_overlap(self):
        self.task("TASK-0002","claude","tools/b.py")
        barrier=threading.Barrier(2)
        def execute(task,deadline):barrier.wait(timeout=2);return self.finish(task,deadline)
        result=manual.run_batch(self.root,["codex","claude"],executor=execute)
        self.assertEqual(result["attempted"],2)

    def test_overlapping_touches_serialize(self):
        self.task("TASK-0002","claude","tools/a.py")
        active=[];lock=threading.Lock()
        def execute(task,deadline):
            with lock:self.assertEqual(active,[]);active.append(task["id"])
            time.sleep(.01)
            with lock:active.clear()
            return self.finish(task,deadline)
        result=manual.run_batch(self.root,["codex","claude"],executor=execute)
        self.assertEqual(result["attempted"],2)

    def test_blocked_failure_does_not_stop_independent_task(self):
        self.task("TASK-0002","codex","tools/b.py")
        def execute(task,deadline):
            if task["id"]=="TASK-0001":
                task["file"].write_text(task["file"].read_text().replace("status: todo","status: blocked"),newline="\n")
                raise RuntimeError("test failed")
            return self.finish(task,deadline)
        with patch.object(ar,"dirty_paths",return_value=[]),patch.object(manual,"git",return_value="main"):
            result=manual.run_batch(self.root,["codex"],executor=execute)
        self.assertEqual([r["phase"]for r in result["results"]],["blocked","done"])

    def test_failure_without_canonical_block_stops(self):
        with self.assertRaises(manual.CoordinatorError):
            manual.run_batch(self.root,["codex"],executor=lambda *_:(_ for _ in ()).throw(RuntimeError("unsafe")))

    def test_no_start_if_task_cannot_fit_remaining_budget(self):
        called=[]
        result=manual.run_batch(self.root,["codex"],max_minutes=.001,executor=lambda *x:called.append(x))
        self.assertEqual(result["attempted"],0);self.assertEqual(called,[])

    def test_cooldown_stops_only_that_agent(self):
        self.task("TASK-0002","claude","tools/b.py")
        with patch.object(ar,"cooling_until",side_effect=lambda a:True if a=="codex" else None):
            result=manual.run_batch(self.root,["codex","claude"],executor=self.finish)
        self.assertEqual([r["agent"]for r in result["results"]],["claude"])

    def test_missing_evidence_blocks_only_affected_task(self):
        self.task("TASK-0001","codex","tools/a.py",extra="evidence_manifest: missing.json\n")
        self.task("TASK-0002","codex","tools/b.py")
        def amend(tid,status,**kwargs):
            task=manual.records(self.root)[tid];task["file"].write_text(task["text"].replace("status: todo","status: "+status),newline="\n")
        with patch.object(ar,"amend_status",side_effect=amend),patch.object(ar,"main_commit"):
            result=manual.run_batch(self.root,["codex"],executor=self.finish)
        self.assertEqual(result["prerequisite_blocks"],["TASK-0001"])
        self.assertEqual(result["results"][0]["task"],"TASK-0002")

    def test_art_missing_tool_never_calls_model(self):
        self.task("TASK-0001","codex","tools/a.py",extra="")
        file=self.root/".agents/tasks/TASK-0001_task.md";file.write_text(file.read_text().replace("art_request: none","art_request: ART-0001"),newline="\n")
        task=manual.records(self.root)["TASK-0001"]
        self.assertIn("approved image-tool adapter unavailable",manual.task_blockers(task,{task["id"]:task},self.root,["codex"],True))

    def test_dry_run_does_not_write_or_call_model(self):
        before={p:p.read_bytes()for p in self.root.rglob("*")if p.is_file()}
        with patch.object(sys,"stdout",io.StringIO()),patch.object(manual,"preflight") as preflight:
            self.assertEqual(manual.main(["--source",str(self.root),"--dry-run"]),0)
        preflight.assert_not_called()
        self.assertEqual(before,{p:p.read_bytes()for p in self.root.rglob("*")if p.is_file()})

    def test_duplicate_task_ids_are_fatal(self):
        source=self.root/".agents/tasks/TASK-0001_task.md"
        (source.parent/"TASK-0001_duplicate.md").write_text(source.read_text(),newline="\n")
        with self.assertRaisesRegex(manual.CoordinatorError,"Duplicate"):manual.records(self.root)

    def test_nonfinite_limits_fail_closed(self):
        for value in (float("nan"),float("inf")):
            with self.assertRaises(ValueError):manual.run_batch(self.root,["codex"],max_minutes=value)

    def test_art_respects_existing_active_agent_and_touch_claims(self):
        self.task("TASK-0002","codex","tools/b.py",status="in_progress")
        tasks=manual.records(self.root);task=tasks["TASK-0001"];task["art_request"]="ART-0001"
        reasons=manual.task_blockers(task,tasks,self.root,["codex"],True)
        self.assertIn("agent already has an active task",reasons)

    def test_art_delivery_requires_all_requested_files_and_rejects_nested_approval(self):
        import hashlib,struct,zlib
        folder=self.root/".agents/graphics/deliveries/ART-0001";folder.mkdir(parents=True)
        def chunk(kind,data):return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data)&0xffffffff)
        data=b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",1,1,8,6,0,0,0))+chunk(b"IDAT",zlib.compress(b"\0\0\0\0\0"))+chunk(b"IEND",b"")
        image=folder/"north.png";image.write_bytes(data)
        relative=image.relative_to(self.root).as_posix();sha="a"*64
        manifest={"request_id":"ART-0001","producer":"codex","tool":"approved-test-fixture","model":"test",
            "reference_sha256":sha,"files":[{"path":relative,"sha256":hashlib.sha256(data).hexdigest(),
            "pixel_size":[1,1],"origin":[0,1],"footprint":[1,1],"collision":{"enabled":False},"shadow":{"type":"none"}}]}
        file=folder/"manifest.json";file.write_text(json.dumps(manifest),newline="\n")
        changed=[relative,file.relative_to(self.root).as_posix()]
        with patch.object(ar,"changed_paths",return_value=changed):
            self.assertEqual(manual.validate_art_output(self.root,"ART-0001",[relative],sha),sorted(changed))
            with self.assertRaisesRegex(ValueError,"every requested"):
                manual.validate_art_output(self.root,"ART-0001",[relative,"missing.png"],sha)
            manifest["assets"]=[{"visual_qa":{"status":"approved"}}]
            file.write_text(json.dumps(manifest),newline="\n")
            with self.assertRaisesRegex(ValueError,"independent approval"):
                manual.validate_art_output(self.root,"ART-0001",[relative],sha)

    def test_coordinator_preserves_dirty_source_and_cross_clone_lease(self):
        import os
        base=self.root/"git-fixture";base.mkdir()
        origin=base/"origin.git";source=base/"source"
        def run(*args,cwd=base):
            return subprocess.run(["git",*map(str,args)],cwd=cwd,check=True,capture_output=True,text=True).stdout
        run("init","--bare","-b","main",origin)
        run("clone",origin,source)
        run("config","user.email","test@example.invalid",cwd=source);run("config","user.name","test",cwd=source)
        (source/"owned.txt").write_text("committed",newline="\n")
        run("add","owned.txt",cwd=source);run("commit","-m","base",cwd=source);run("push","origin","main",cwd=source)
        (source/"owned.txt").write_text("user edits must survive",newline="\n")
        with patch.dict(os.environ,{"LOCALAPPDATA":str(base/"local")}):
            clone=manual.coordinator(source,time.monotonic()+20)
        self.assertEqual((source/"owned.txt").read_text(),"user edits must survive")
        self.assertEqual((clone/"owned.txt").read_text(),"committed")
        with manual.repository_lease(source):
            code="import sys;sys.path.insert(0,sys.argv[1]);from pathlib import Path;from manual_agents import repository_lease,Busy\ntry:\n with repository_lease(Path(sys.argv[2])):sys.exit(7)\nexcept Busy:sys.exit(0)"
            proc=subprocess.run([sys.executable,"-c",code,str(Path(manual.__file__).parent),str(clone)],capture_output=True,text=True,timeout=10)
            self.assertEqual(proc.returncode,0,proc.stderr)

    def test_fake_cli_trial_executes_only_bounded_selected_tasks(self):
        self.task("TASK-0002","claude","tools/b.py")
        def execute(task,deadline):
            with ar.execution_budget(deadline):
                result=ar.execute([sys.executable,"-c","print('fake CLI completed')"],self.root)
            self.assertEqual(result.stdout.strip(),"fake CLI completed")
            return self.finish(task,deadline)
        result=manual.run_batch(self.root,["codex","claude"],max_tasks=1,executor=execute)
        self.assertEqual(result["attempted"],1)


if __name__=="__main__":unittest.main()
