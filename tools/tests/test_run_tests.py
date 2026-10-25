import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import run_tests  # noqa: E402


def entry(test_id, paths, command=None, kind="python"):
    return {"id": test_id, "kind": kind, "covers": test_id,
            "command": command or ["{python}", "-c", "pass"], "paths": paths}


class GlobTests(unittest.TestCase):
    def test_single_star_stays_in_folder(self):
        self.assertTrue(run_tests.matches("tools/tests/test_map_x.py", ["tools/tests/test_map*.py"]))
        self.assertFalse(run_tests.matches("tools/tests/sub/test_map_x.py", ["tools/tests/test_map*.py"]))

    def test_double_star_crosses_folders(self):
        self.assertTrue(run_tests.matches("map_factory/maps/a/v/1.json", ["map_factory/maps/**"]))
        self.assertTrue(run_tests.matches("project.gd", ["**/*.gd"]))
        self.assertTrue(run_tests.matches("a/b/c.gd", ["**/*.gd"]))
        self.assertFalse(run_tests.matches("a/b/c.gd.uid", ["**/*.gd"]))

    def test_literal_characters_and_backslashes(self):
        self.assertTrue(run_tests.matches(".agents\\planner\\config.json", [".agents/planner/config.json"]))
        self.assertFalse(run_tests.matches("xagents/planner/config.json", [".agents/planner/config.json"]))


class SelectTests(unittest.TestCase):
    tests = [entry("a", ["tools/a.py"]), entry("b", ["tools/b/**"]), entry("c", ["docs/*.md"])]

    def test_selects_only_matching_tests(self):
        selected, unmatched = run_tests.select(self.tests, ["tools/b/x/y.py"])
        self.assertEqual([t["id"] for t in selected], ["b"])
        self.assertEqual(unmatched, [])

    def test_unmatched_path_runs_all(self):
        selected, unmatched = run_tests.select(self.tests, ["tools/a.py", "README.md"])
        self.assertEqual([t["id"] for t in selected], ["a", "b", "c"])
        self.assertEqual(unmatched, ["README.md"])

    def test_no_changes_selects_nothing(self):
        self.assertEqual(run_tests.select(self.tests, []), ([], []))


class MapTests(unittest.TestCase):
    def test_repository_map_is_valid(self):
        tests = run_tests.load_map()
        self.assertTrue(tests)
        self.assertEqual({t["kind"] for t in tests}, {"python", "godot"})

    def test_every_test_file_is_routed(self):
        commands = [" ".join(t["command"]) for t in run_tests.load_map()]
        files = sorted((ROOT / "tools/tests").glob("test_*.py"))
        files += sorted((ROOT / "map_factory/tests").glob("**/test_*.py"))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=path.name):
                self.assertTrue(any(path.name in c for c in commands), path.name + " has no router entry")

    def test_godot_smoke_scripts_are_routed(self):
        commands = " ".join(" ".join(t["command"]) for t in run_tests.load_map() if t["kind"] == "godot")
        self.assertIn("res://tools/map_factory_godot_smoke.gd", commands)
        self.assertIn("res://tools/test_cardinal_map_blocks.gd", commands)

    def test_invalid_maps_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "map.json"
            for tests in ([entry("a", ["x"]), entry("a", ["y"])],
                          [entry("a", ["x"], kind="shell")],
                          [entry("a", [])]):
                bad.write_text(json.dumps({"tests": tests}), encoding="utf-8")
                with self.subTest(tests=tests), self.assertRaises(ValueError):
                    run_tests.load_map(bad)

    def test_index_is_up_to_date(self):
        self.assertEqual(run_tests.INDEX.read_text(encoding="utf-8"), run_tests.render_index(run_tests.load_map()))

    def test_godot_placeholder_resolves(self):
        argv = run_tests.resolve(entry("g", ["x"], ["{godot}", "--headless"], "godot"), "/opt/godot")
        self.assertEqual(argv, ["/opt/godot", "--headless"])
        self.assertEqual(run_tests.godot_executable("/explicit"), "/explicit")


class ChangedPathTests(unittest.TestCase):
    def git(self, repo, *args):
        subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

    def test_includes_committed_staged_unstaged_and_untracked(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.git(repo, "init", "-q", "-b", "base")
            self.git(repo, "config", "user.email", "t@example.invalid")
            self.git(repo, "config", "user.name", "t")
            for name in ("keep.txt", "edit.txt", "stage.txt"):
                (repo / name).write_text("0\n", encoding="utf-8")
            self.git(repo, "add", ".")
            self.git(repo, "commit", "-q", "-m", "base")
            self.git(repo, "checkout", "-q", "-b", "work")
            (repo / "committed.txt").write_text("1\n", encoding="utf-8")
            self.git(repo, "add", "committed.txt")
            self.git(repo, "commit", "-q", "-m", "work")
            (repo / "edit.txt").write_text("2\n", encoding="utf-8")
            (repo / "stage.txt").write_text("3\n", encoding="utf-8")
            self.git(repo, "add", "stage.txt")
            (repo / "new.txt").write_text("4\n", encoding="utf-8")
            self.assertEqual(run_tests.changed_paths("base", repo),
                             ["committed.txt", "edit.txt", "new.txt", "stage.txt"])

    def test_undo_side_effects_keeps_pre_existing_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            self.git(repo, "init", "-q")
            self.git(repo, "config", "user.email", "t@example.invalid")
            self.git(repo, "config", "user.name", "t")
            for name in ("clean.gd", "mine.gd"):
                (repo / name).write_text("0\n", encoding="utf-8")
            self.git(repo, "add", ".")
            self.git(repo, "commit", "-q", "-m", "base")
            (repo / "mine.gd").write_text("my edit\n", encoding="utf-8")
            (repo / "mine_new.txt").write_text("mine\n", encoding="utf-8")
            before = run_tests.tree_state(repo)
            (repo / "clean.gd").write_text("\trewritten\n", encoding="utf-8")
            (repo / "mine.gd").write_text("my edit, then godot\n", encoding="utf-8")
            (repo / "x.csv.import").write_text("import\n", encoding="utf-8")
            self.assertEqual(run_tests.undo_side_effects(before, repo), ["clean.gd", "x.csv.import"])
            self.assertEqual((repo / "clean.gd").read_text(encoding="utf-8"), "0\n")
            self.assertFalse((repo / "x.csv.import").exists())
            self.assertEqual((repo / "mine.gd").read_text(encoding="utf-8"), "my edit, then godot\n")
            self.assertTrue((repo / "mine_new.txt").exists())

    def test_unknown_base_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.git(tmp, "init", "-q")
            with self.assertRaises(RuntimeError):
                run_tests.changed_paths("no-such-ref", Path(tmp))


class RunTests(unittest.TestCase):
    def main(self, tests, *args):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "map.json"
            path.write_text(json.dumps({"tests": tests}), encoding="utf-8")
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = run_tests.main(["--map", str(path), *args])
            return code, out.getvalue()

    def test_failure_exits_non_zero_with_summary(self):
        code, out = self.main([entry("ok", ["x"]), entry("bad", ["y"], ["{python}", "-c", "raise SystemExit(3)"])],
                              "--all")
        self.assertEqual(code, 1)
        self.assertIn("PASS ok", out)
        self.assertIn("FAIL bad", out)
        self.assertIn("1/2 passed: failed bad", out)

    def test_dry_run_executes_nothing(self):
        marker = Path(tempfile.gettempdir()) / "run_tests_dry_run_marker"
        marker.unlink(missing_ok=True)
        code, out = self.main([entry("touch", ["x"], ["{python}", "-c", f"open({str(marker)!r},'w')"])],
                              "--all", "--dry-run")
        self.assertEqual(code, 0)
        self.assertFalse(marker.exists())
        self.assertIn("1 test(s) selected (dry run)", out)

    def test_missing_godot_fails_closed(self):
        code, out = self.main([entry("g", ["x"], ["{godot}", "--version"], "godot")],
                              "--all", "--godot", str(Path(tempfile.gettempdir()) / "no-godot-here.exe"))
        self.assertEqual(code, 1)
        self.assertIn("godot executable not found", out)

    def test_kind_and_only_filters(self):
        tests = [entry("p", ["x"]), entry("g", ["y"], ["{godot}"], "godot")]
        self.assertIn("No tests selected", self.main(tests, "--only", "g", "--kind", "python")[1])
        self.assertEqual(self.main(tests, "--only", "missing")[0], 2)
        code, out = self.main(tests, "--list")
        self.assertEqual(code, 0)
        self.assertIn("p ", out)


if __name__ == "__main__":
    unittest.main()
