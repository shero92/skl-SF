"""Regression tests for tiny on-demand project file inventory."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from generate_project_indexes import render


class IndexGenerationTests(unittest.TestCase):
    def test_direct_children_and_nested_paths(self):
        generated = render([
            "README.md", "tools/build.py", "tools/tests/test_me.py",
            "map_factory/parts/floors/F001_Stone_Floor.png"])
        self.assertIn("FILES.md", generated)
        self.assertIn("tools/FILES.md", generated)
        self.assertIn("tools/tests/FILES.md", generated)
        self.assertIn("map_factory/parts/floors/FILES.md", generated)
        self.assertIn("[`tools/`](tools/FILES.md)", generated["FILES.md"])
        self.assertIn("[`build.py`](build.py)", generated["tools/FILES.md"])
        self.assertNotIn("test_me.py", generated["tools/FILES.md"])
        self.assertIn("F001_Stone_Floor.png", generated["map_factory/parts/floors/FILES.md"])
        self.assertNotIn("build.py", generated["map_factory/parts/floors/FILES.md"])

    def test_order_independent(self):
        paths = ["docs/b.md", "docs/a.md", "project.godot"]
        self.assertEqual(render(paths), render(list(reversed(paths))))


class GeneratedPRChecks(unittest.TestCase):
    def setUp(self):
        import tempfile
        import json
        import agent_workflow as aw
        import agent_costs as costs
        from unittest.mock import patch
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.git("init","-q","-b","main")
        self.git("config","user.name","Test")
        self.git("config","user.email","test@example.invalid")
        self.write("map_factory/metadata/asset_index.json",json.dumps({"assets":[]}))
        self.write("README.md","baseline\n")
        for path, content in aw.generated(self.root).items():
            self.write(path,content)
        with patch.object(costs,"ROOT",self.root),patch.object(costs,"BASE",self.root/".agents/monitoring"):
            costs.report()
        self.write("FILES.md","inherited inventory\n")
        self.git("add","-A")
        self.git("commit","-q","-m","base")
        self.base=self.git("rev-parse","HEAD").strip()
        self.git("switch","-q","-c","task")

    def git(self,*args):
        import subprocess
        return subprocess.run(["git",*args],cwd=self.root,check=True,capture_output=True,text=True).stdout

    def write(self,path,text):
        p=self.root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(text,encoding="utf-8",newline="\n")

    def sources(self):
        import json
        self.write(".agents/tasks/TASK-0001_plan.md",
                   "---\nid: TASK-0001\nstatus: todo\nowner: unassigned\nbranch: none\n"
                   "agent: codex\ntouches: tools/example.py\ntest: python -m unittest\n"
                   "done_when: test passes\ndepends_on: none\nissue: none\nart_request: none\n---\n# Plan\n")
        self.write(".agents/monitoring/receipts/TASK-0001_codex_test.json",json.dumps({
            "task_id":"TASK-0001","agent":"codex","cost_usd":None,"tokens":None}))

    def snapshot(self):
        return {p.relative_to(self.root).as_posix():p.read_bytes()
                for p in self.root.rglob("*") if p.is_file() and ".git" not in p.parts}

    def cli(self,module,mode):
        from unittest.mock import patch
        with patch.object(module,"ROOT",self.root),patch.object(sys,"argv",["test",mode,"--base",self.base]):
            return module.main()

    def test_sources_only_validates_new_records_without_writing_stale_outputs(self):
        import agent_workflow as aw
        import generate_project_indexes as indexes
        import agent_costs as costs
        from unittest.mock import patch
        self.sources()
        before=self.snapshot()
        self.assertEqual(self.cli(aw,"--sources-only"),0)
        self.assertEqual(self.cli(indexes,"--sources-only"),0)
        with patch.object(costs,"ROOT",self.root),patch.object(costs,"BASE",self.root/".agents/monitoring"):
            costs.report(sources_only=True,base=self.base)
            with self.assertRaisesRegex(ValueError,"Stale report"):
                costs.report(check=True)
        self.assertEqual(self.cli(aw,"--check"),1)
        self.assertEqual(self.cli(indexes,"--check"),1)
        self.assertEqual(self.snapshot(),before)

    def test_sources_only_rejects_invalid_task_and_receipt(self):
        import agent_workflow as aw
        import agent_costs as costs
        from unittest.mock import patch
        self.sources()
        self.write(".agents/tasks/TASK-0001_plan.md","# Missing frontmatter\n")
        self.assertEqual(self.cli(aw,"--sources-only"),1)
        self.write(".agents/monitoring/receipts/TASK-0001_codex_test.json","{}")
        with patch.object(costs,"ROOT",self.root),patch.object(costs,"BASE",self.root/".agents/monitoring"):
            with self.assertRaises(KeyError):costs.report(sources_only=True,base=self.base)

    def test_generated_edits_rejected_when_unstaged_staged_committed_or_renamed(self):
        import runner_safety as rs
        for state in ("unstaged","staged","committed"):
            with self.subTest(state=state):
                self.write("FILES.md",state+"\n")
                if state in ("staged","committed"):self.git("add","FILES.md")
                if state=="committed":self.git("commit","-q","-m","forbidden output")
                with self.assertRaisesRegex(ValueError,"main after merge"):
                    rs.check_pr_generated(self.root,self.base)
        self.git("mv","FILES.md","renamed.md")
        with self.assertRaisesRegex(ValueError,"FILES.md"):
            rs.check_pr_generated(self.root,self.base)

    def test_missing_base_and_untracked_generated_outputs_fail_closed(self):
        import subprocess
        import runner_safety as rs
        with self.assertRaises(subprocess.CalledProcessError):
            rs.check_pr_generated(self.root,"missing-base")
        self.write("tools/tests/INDEX.md","forbidden untracked output\n")
        with self.assertRaisesRegex(ValueError,"tools/tests/INDEX.md"):
            rs.check_pr_generated(self.root,self.base)

    def test_ci_keeps_main_strict_and_pr_checks_read_only(self):
        root=Path(__file__).resolve().parents[2]
        for name in ("agent_workflow","project_indexes","agent_costs"):
            workflow=(root/".github/workflows"/(name+".yml")).read_text(encoding="utf-8")
            self.assertIn("if: github.event_name != 'pull_request'",workflow)
            self.assertIn("if: github.event_name == 'pull_request'",workflow)
            self.assertIn("--sources-only --base origin/main",workflow)
            self.assertIn("fetch-depth: 0",workflow)
            self.assertNotIn("--write",workflow)

if __name__ == "__main__":
    unittest.main()
