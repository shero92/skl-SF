"""Task-scoped Codex file bridge: allowed text read/edit only (TASK-0061). No model calls."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import agent_file_bridge as fb  # noqa: E402


def call(name, rid, **arguments):
    return {"jsonrpc": "2.0", "id": rid, "method": "tools/call", "params": {"name": name, "arguments": arguments}}


class BridgeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "work"
        (self.root / "tools").mkdir(parents=True)
        (self.root / "AGENTS.md").write_bytes(b"contract\n")
        (self.root / "tools/x.py").write_bytes(b"x = 1\n")
        (self.root / "tools/other.py").write_bytes(b"secret = 1\n")
        (Path(tmp.name) / "outside.txt").write_bytes(b"outside\n")
        self.bridge = fb.Bridge(self.root, ["tools/x.py", "tools/new/"], ["AGENTS.md"])

    def denied(self, func, *args):
        with self.assertRaises(fb.Denied):
            func(*args)

    def test_reads_and_edits_allowed_text(self):
        self.assertEqual(self.bridge.read("tools/x.py"), "x = 1\n")
        self.assertEqual(self.bridge.read("AGENTS.md"), "contract\n")
        self.bridge.replace("tools/x.py", "x = 1", "x = 2")
        self.bridge.write("tools/new/y.py", "y = 1\n")
        self.assertEqual((self.root / "tools/x.py").read_text(encoding="utf-8"), "x = 2\n")
        self.assertTrue((self.root / "tools/new/y.py").is_file())

    def test_rejects_out_of_scope_traversal_and_readonly_writes(self):
        self.denied(self.bridge.read, "tools/other.py")
        self.denied(self.bridge.read, "../outside.txt")
        self.denied(self.bridge.read, "tools/../../outside.txt")
        self.denied(self.bridge.read, str(self.root / "tools/x.py"))
        self.denied(self.bridge.read, ".git/config")
        self.denied(self.bridge.write, "AGENTS.md", "changed")
        self.denied(self.bridge.write, "tools/other.py", "changed")
        self.denied(self.bridge.replace, "tools/x.py", "missing", "y")
        self.assertEqual((self.root / "AGENTS.md").read_text(encoding="utf-8"), "contract\n")

    def test_rejects_images_and_binaries(self):
        bridge = fb.Bridge(self.root, ["tools/"], [])
        (self.root / "tools/a.png").write_bytes(b"\x89PNG\r\n")
        (self.root / "tools/b.dat").write_bytes(b"a\x00b")
        self.denied(bridge.read, "tools/a.png")
        self.denied(bridge.read, "tools/A.PNG")
        self.denied(bridge.write, "tools/c.svg", "<svg/>")
        self.denied(bridge.read, "tools/b.dat")
        self.denied(bridge.write, "tools/d.py", "a\x00b")

    def test_rejects_symlink_escape(self):
        link = self.root / "tools/new/link.py"
        link.parent.mkdir(parents=True)
        try:
            os.symlink(self.root / "tools/other.py", link)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.denied(self.bridge.read, "tools/new/link.py")
        self.denied(self.bridge.write, "tools/new/link.py", "pwned")
        self.assertEqual((self.root / "tools/other.py").read_text(encoding="utf-8"), "secret = 1\n")

    def test_text_extension_allowlist_and_windows_aliases(self):
        bridge = fb.Bridge(self.root, ["tools/"], [])
        for path in ("tools/secret.env", "tools/file.bin", "tools/script.bat", "tools/archive.tar",
                     "tools/.GIT/config.py", "tools/.codex/config.toml", "tools/nul.py", "tools/x.py "):
            with self.subTest(path=path):
                self.denied(bridge.write, path, "text")
        (self.root / "tools/binary.py").write_bytes(b"binary\0content")
        self.denied(bridge.write, "tools/binary.py", "new text")

    def test_rejects_hardlink_alias(self):
        link = self.root / "tools/new/alias.py"
        link.parent.mkdir(parents=True)
        try:
            os.link(self.root / "tools/other.py", link)
        except (OSError, NotImplementedError):
            self.skipTest("hardlinks unavailable")
        self.denied(self.bridge.read, "tools/new/alias.py")
        self.denied(self.bridge.write, "tools/new/alias.py", "changed")
        self.assertEqual((self.root / "tools/other.py").read_bytes(), b"secret = 1\n")

    def test_stdio_roundtrip_preserves_lf_crlf_and_unicode_bytes(self):
        for ending in ("\n", "\r\n"):
            original = ("# cafÃ©" + ending + "x = 1" + ending).encode("utf-8")
            (self.root / "tools/x.py").write_bytes(original)
            msgs = [call("read_file", 1, path="tools/x.py"),
                    call("write_file", 2, path="tools/x.py", content=original.decode("utf-8")),
                    call("replace_in_file", 3, path="tools/x.py", old="x = 1", new="x = 2")]
            proc = subprocess.run(fb.command(self.root, ["tools/x.py"], []),
                                  input="".join(json.dumps(m)+"\n" for m in msgs),
                                  capture_output=True, text=True, timeout=30, encoding="utf-8")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            replies = [json.loads(line) for line in proc.stdout.splitlines()]
            self.assertEqual(replies[0]["result"]["content"][0]["text"].encode("utf-8"), original)
            self.assertFalse(any(reply["result"]["isError"] for reply in replies))
            self.assertEqual((self.root / "tools/x.py").read_bytes(), original.replace(b"x = 1", b"x = 2"))

    def test_only_file_tools_are_exposed(self):
        self.assertEqual({t["name"] for t in fb.TOOLS}, {"read_file", "write_file", "replace_in_file"})
        reply = self.bridge.handle(call("run_shell", 9, command="dir"))
        self.assertTrue(reply["result"]["isError"])

    def test_fake_cli_reads_and_edits_through_stdio_server(self):
        # A fake Codex client speaks MCP JSON-RPC to the real bridge subprocess.
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                call("read_file", 2, path="tools/x.py"),
                call("replace_in_file", 3, path="tools/x.py", old="x = 1", new="x = 3"),
                call("read_file", 4, path="tools/other.py"),
                call("read_file", 5, path="art/hero.png"),
                call("write_file", 6, path="../escape.py", content="bad")]
        proc = subprocess.run(fb.command(self.root, ["tools/x.py"], ["AGENTS.md"]),
                              input="".join(json.dumps(m) + "\n" for m in msgs),
                              capture_output=True, text=True, timeout=30, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        replies = {r["id"]: r["result"] for r in map(json.loads, proc.stdout.splitlines())}
        self.assertEqual(replies[2]["content"][0]["text"], "x = 1\n")
        self.assertFalse(replies[3]["isError"])
        for rid in (4, 5, 6):
            self.assertTrue(replies[rid]["isError"], rid)
        self.assertEqual((self.root / "tools/x.py").read_text(encoding="utf-8"), "x = 3\n")
        self.assertFalse((self.root.parent / "escape.py").exists())

    def test_runner_bridge_exposes_only_present_instruction_documents(self):
        import agent_runner as ar
        instruction = self.root / ".agents/workflows/TASKS.md"
        instruction.parent.mkdir(parents=True)
        instruction.write_bytes(b"workflow\n")
        task = self.root / ".agents/tasks/TASK-0001_task.md"
        task.parent.mkdir(parents=True)
        task.write_bytes(b"---\nid: TASK-0001\ntouches: tools/x.py\n---\n")
        (self.root / "INDEX.md").write_bytes(b"navigation\n")
        result=ar.codex_bridge(self.root,"TASK-0001")
        self.assertIn("INDEX.md", result["reads"])
        self.assertIn(".agents/workflows/TASKS.md", result["reads"])
        self.assertNotIn("tools/INDEX.md", result["reads"])
        self.assertNotIn(".claude/settings.json", result["reads"])
        bridge=fb.Bridge(self.root,result["touches"],result["reads"])
        self.assertEqual(bridge.read(".agents/workflows/TASKS.md"),"workflow\n")
        self.denied(bridge.write,".agents/workflows/TASKS.md","changed")
        self.denied(bridge.read,"tools/other.py")

    def test_preflight_reports_real_capability(self):
        self.assertIsNone(fb.preflight(self.root, ["tools/x.py"], ["AGENTS.md"], "AGENTS.md"))
        self.assertIn("could not read", fb.preflight(self.root, ["tools/x.py"], [], "AGENTS.md"))
        self.assertIn("malformed", fb.check_preflight("not json"))


if __name__ == "__main__":
    unittest.main()
