"""Every repo writer in tools/ must emit LF so Windows runs leave no CRLF-only diffs."""
import ast
from pathlib import Path
import unittest

TOOLS = Path(__file__).resolve().parents[1]


def mode_of(call, index):
    for k in call.keywords:
        if k.arg == "mode":
            return k.value.value if isinstance(k.value, ast.Constant) else None
    if len(call.args) > index and isinstance(call.args[index], ast.Constant):
        return call.args[index].value
    return "r" if len(call.args) <= index else None


def offenders(source, name):
    found = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        f, keys = node.func, {k.arg for k in node.keywords}
        where = f"{name}:{node.lineno}"
        if isinstance(f, ast.Attribute) and f.attr == "write_text" and "newline" not in keys:
            found.append(where + " write_text without newline")
        elif isinstance(f, ast.Attribute) and f.attr == "writer" and isinstance(f.value, ast.Name) \
                and f.value.id == "csv" and "lineterminator" not in keys:
            found.append(where + " csv.writer without lineterminator")
        else:
            index = {"open": 1, "fdopen": 1}.get(getattr(f, "id", None) or getattr(f, "attr", None) or "")
            if isinstance(f, ast.Attribute) and f.attr == "open":
                index = 0
            mode = mode_of(node, index) if index is not None else None
            if isinstance(mode, str) and any(c in mode for c in "wax") and "b" not in mode and "newline" not in keys:
                found.append(where + " text open without newline")
    return found


class LfWriterTests(unittest.TestCase):
    def test_tools_write_lf(self):
        found = []
        for path in sorted(TOOLS.glob("*.py")):
            found += offenders(path.read_text(encoding="utf-8"), path.name)
        self.assertEqual(found, [], "add newline=\"\\n\" (or lineterminator=\"\\n\" for csv)")

    def test_detector_flags_platform_newlines(self):
        bad = 'p.write_text("x")\nopen(f, "w")\ncsv.writer(h)\nq.open("a")\n'
        self.assertEqual(len(offenders(bad, "bad.py")), 4)
        good = ('p.write_text("x", newline="\\n")\nopen(f, "w", newline="\\n")\nopen(f, "rb")\n'
                'csv.writer(h, lineterminator="\\n")\nq.open()\n')
        self.assertEqual(offenders(good, "good.py"), [])


if __name__ == "__main__":
    unittest.main()
