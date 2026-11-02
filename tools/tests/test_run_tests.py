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

    def test_check_index_strict_on_main_tolerant_for_sources(self):
        # INDEX.md is main-only (ADR-006): PRs and task worktrees change test_map.json, not INDEX.md.
        saved = run_tests.INDEX
        self.addCleanup(setattr, run_tests, "INDEX", saved)
        with tempfile.TemporaryDirectory() as tmp:
            run_tests.INDEX = Path(tmp) / "INDEX.md"
            run_tests.INDEX.write_text("stale\n", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_tests.main(["--check-index"]), 1)
                self.assertEqual(run_tests.main(["--check-index", "--sources-only"]), 0)
                run_tests.INDEX.write_text(run_tests.render_index(run_tests.load_map()), encoding="utf-8")
                self.assertEqual(run_tests.main(["--check-index"]), 0)

    def test_godot_placeholder_resolves(self):
        argv = run_tests.resolve(entry("g", ["x"], ["{godot}", "--headless"], "godot"), "/opt/godot")
        self.assertEqual(argv, ["/opt/godot", "--headless"])
        self.assertEqual(run_tests.godot_executable("/explicit"), "/explicit")


class GodotImportPrerequisiteTests(unittest.TestCase):
    importer = entry("godot_import", ["**/*.gd"], ["{godot}", "--editor", "--quit"], "godot")
    smoke = entry("godot_map_smoke", ["map_factory/maps/**"], ["{godot}", "--script", "s.gd"], "godot")
    unit = entry("map_factory", ["map_factory/maps/**"])
    tests = [unit, importer, smoke]

    def root(self, cached):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        if cached:
            cache = Path(tmp.name) / run_tests.CLASS_CACHE
            cache.parent.mkdir(parents=True)
            cache.write_text("list=[]\n", encoding="utf-8")
        return Path(tmp.name)

    def ids(self, selected):
        return [t["id"] for t in selected]

    def test_fresh_worktree_imports_before_godot_scripts(self):
        # TASK-0008: maps-only change selected the smoke but not the import; RoomFactory undeclared.
        selected = run_tests.with_godot_import([self.unit, self.smoke], self.tests, self.root(False))
        self.assertEqual(self.ids(selected), ["map_factory", "godot_import", "godot_map_smoke"])

    def test_import_moves_ahead_when_already_selected(self):
        selected = run_tests.with_godot_import([self.smoke, self.importer], self.tests, self.root(False))
        self.assertEqual(self.ids(selected), ["godot_import", "godot_map_smoke"])

    def test_no_import_when_cached_or_no_godot_tests(self):
        self.assertEqual(self.ids(run_tests.with_godot_import([self.smoke], self.tests, self.root(True))),
                         ["godot_map_smoke"])
        self.assertEqual(self.ids(run_tests.with_godot_import([self.unit], self.tests, self.root(False))),
                         ["map_factory"])
        self.assertEqual(self.ids(run_tests.with_godot_import([self.importer], self.tests, self.root(False))),
                         ["godot_import"])

    def test_repository_map_has_import_entry(self):
        importer = next(t for t in run_tests.load_map() if t["id"] == run_tests.GODOT_IMPORT)
        self.assertEqual(importer["kind"], "godot")
        self.assertIn("--editor", importer["command"])


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

    def test_failure_prints_test_location_and_saves_complete_raw_output(self):
        script = ("print('FAIL: test_bad_case (suite.Sample)'); "
                  "print('  File \\\"tools/tests/test_sample.py\\\", line 42'); "
                  "print('AssertionError: expected 1'); "
                  "[print('raw detail '+str(i)) for i in range(40)]; raise SystemExit(2)")
        with tempfile.TemporaryDirectory() as tmp:
            log_dir = Path(tmp) / "test-logs"
            test = entry("diagnostic", ["x"], [sys.executable, "-c", script])
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = run_tests.run([test], "godot", 10, log_dir=log_dir)
            rendered = out.getvalue()
            logs = list(log_dir.glob("diagnostic_*.log"))
            self.assertEqual(code, 1)
            self.assertIn("FAIL: test_bad_case (suite.Sample)", rendered)
            self.assertIn('File "tools/tests/test_sample.py", line 42', rendered)
            self.assertIn("AssertionError: expected 1", rendered)
            self.assertIn("Full log:", rendered)
            self.assertEqual(len(logs), 1)
            saved = logs[0].read_text(encoding="utf-8")
            self.assertIn("raw detail 0", saved)
            self.assertIn("raw detail 39", saved)

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
