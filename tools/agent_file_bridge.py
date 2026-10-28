#!/usr/bin/env python3
"""Task-scoped text file tools for the Codex worker (MCP over stdio).

Exposes only read_file / write_file / replace_in_file. Writes are limited to the
task's touches; reads add a minimal read-only instruction set. No shell, no git,
no images or binaries, no paths outside the worktree after symlink resolution.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys

PROTOCOL = "2024-11-05"
MAX_BYTES = 512_000
TEXT_SUFFIXES = {".md", ".json", ".py", ".gd", ".tscn", ".tres", ".godot",
                 ".cfg", ".ini", ".txt", ".yaml", ".yml", ".toml", ".ps1",
                 ".sh", ".uid", ".csv", ".tsv"}
PRIVATE_PARTS = {".git", ".hg", ".svn", ".codex", ".claude", ".aws"}
WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *("com"+str(n) for n in range(1,10)),
                    *("lpt"+str(n) for n in range(1,10))}
TOOLS = [
    {"name": "read_file", "description": "Read an authorized UTF-8 text file (repo-relative path).",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Create or overwrite an authorized task touches text file.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                     "required": ["path", "content"]}},
    {"name": "replace_in_file", "description": "Replace one exact unique string in an authorized touches file.",
     "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "old": {"type": "string"},
                                                       "new": {"type": "string"}},
                     "required": ["path", "old", "new"]}},
]


class Denied(Exception):
    pass


def _clean(entries):
    out = []
    for item in entries:
        item = item.strip().replace("\\", "/")
        if item and item != "none":
            out.append(item)
    return out


class Bridge:
    def __init__(self, root, touches, reads=()):
        self.root = Path(root).resolve()
        self.touches = _clean(touches)
        self.reads = _clean(reads)

    @staticmethod
    def _matches(rel, allowed):
        return any(rel == a or (a.endswith("/") and rel.startswith(a)) for a in allowed)

    def resolve(self, raw, write=False):
        if not isinstance(raw, str) or not raw or "\x00" in raw:
            raise Denied("invalid path")
        text = raw.replace("\\", "/")
        pure = PurePosixPath(text)
        if pure.is_absolute() or ":" in text or ".." in pure.parts:
            raise Denied("path must be repo-relative without traversal")
        rel = pure.as_posix()
        if any(part.lower() in PRIVATE_PARTS for part in pure.parts):
            raise Denied("private metadata is not accessible")
        if any(part.endswith((".", " ")) or part.split(".")[0].lower() in WINDOWS_RESERVED
               or any(ord(c) < 32 for c in part) for part in pure.parts):
            raise Denied("ambiguous or reserved path")
        if pure.suffix.lower() not in TEXT_SUFFIXES:
            raise Denied("only approved text extensions are accessible")
        lexical = self.root / rel
        # Reject links even within authorized directories: a second alias can mutate
        # another file. Reparse points also cover Windows directory junctions.
        for item in (lexical, *lexical.parents):
            if item == self.root:
                break
            if item.is_symlink() or (item.exists() and getattr(item.lstat(), "st_file_attributes", 0) & 0x400):
                raise Denied("links and reparse points are not accessible")
        target = lexical.resolve()
        try:
            resolved = target.relative_to(self.root).as_posix()
        except ValueError:
            raise Denied("path resolves outside the worktree")
        allowed = self.touches if write else self.touches + self.reads
        # Both the requested and the symlink-resolved path must be authorized.
        if not (self._matches(rel, allowed) and self._matches(resolved, allowed)):
            raise Denied(("write" if write else "read") + " not authorized for " + rel)
        if target.exists() and target.is_file() and target.stat().st_nlink > 1:
            raise Denied("hardlinked files are not accessible")
        return target

    def read(self, path):
        target = self.resolve(path)
        if not target.is_file():
            raise Denied("file not found: " + path)
        if target.stat().st_size > MAX_BYTES:
            raise Denied("file too large")
        with target.open("rb") as handle:
            data = handle.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise Denied("file too large")
        if b"\x00" in data:
            raise Denied("binary file rejected")
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            raise Denied("non-UTF-8 file rejected")

    def write(self, path, content):
        if not isinstance(content, str) or "\x00" in content:
            raise Denied("content must be bounded text")
        try:
            encoded = content.encode("utf-8")
        except UnicodeEncodeError:
            raise Denied("content must be UTF-8 text")
        if len(encoded) > MAX_BYTES:
            raise Denied("content must be bounded text")
        target = self.resolve(path, write=True)
        if target.exists():
            if not target.is_file():
                raise Denied("not a regular file")
            self.read(path)  # Never replace existing binary content under a text suffix.
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        return "wrote " + path

    def replace(self, path, old, new):
        if not isinstance(old, str) or not old or not isinstance(new, str):
            raise Denied("old must be non-empty text")
        self.resolve(path, write=True)
        text = self.read(path)
        count = text.count(old)
        if count != 1:
            raise Denied("old string must occur exactly once (found " + str(count) + ")")
        return self.write(path, text.replace(old, new, 1)).replace("wrote", "edited")

    def call(self, name, args):
        args = args or {}
        if not isinstance(args, dict):
            raise Denied("arguments must be an object")
        if name == "read_file":
            return self.read(args.get("path"))
        if name == "write_file":
            return self.write(args.get("path"), args.get("content"))
        if name == "replace_in_file":
            return self.replace(args.get("path"), args.get("old"), args.get("new"))
        raise Denied("unknown tool")

    def handle(self, msg):
        method, mid = msg.get("method"), msg.get("id")
        if mid is None:
            return None  # notification
        if method == "initialize":
            result = {"protocolVersion": PROTOCOL, "capabilities": {"tools": {}},
                      "serverInfo": {"name": "task_files", "version": "1"}}
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            params = msg.get("params") or {}
            try:
                if not isinstance(params, dict):
                    raise Denied("params must be an object")
                text, error = self.call(params.get("name"), params.get("arguments")), False
            except Denied as exc:
                text, error = "denied: " + str(exc), True
            except OSError as exc:
                text, error = "error: " + exc.__class__.__name__, True
            result = {"content": [{"type": "text", "text": text}], "isError": error}
        elif method == "ping":
            result = {}
        else:
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}}
        return {"jsonrpc": "2.0", "id": mid, "result": result}

    def serve(self, stdin, stdout):
        for line in stdin:
            if not line.strip():
                continue
            try:
                reply = self.handle(json.loads(line))
            except (ValueError, AttributeError):
                reply = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
            if reply is not None:
                stdout.write(json.dumps(reply) + "\n")
                stdout.flush()


def command(root, touches, reads):
    return [sys.executable, "-I", str(Path(__file__).resolve()), "--root", str(root),
            "--touches", ",".join(touches), "--reads", ",".join(reads)]


def preflight_requests(probe_path):
    msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": PROTOCOL}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "read_file", "arguments": {"path": probe_path}}}]
    return "".join(json.dumps(m) + "\n" for m in msgs)


def check_preflight(stdout):
    """Return None when the bridge listed its tools and read the probe file, else a reason."""
    try:
        replies = {r.get("id"): r for r in map(json.loads, filter(str.strip, stdout.splitlines()))}
    except (ValueError, AttributeError, TypeError):
        return "file bridge returned malformed output"
    names = {t.get("name") for t in replies.get(2, {}).get("result", {}).get("tools", [])}
    if names != {t["name"] for t in TOOLS}:
        return "file bridge did not list its tools"
    if replies.get(3, {}).get("result", {}).get("isError", True):
        return "file bridge could not read the task instructions"
    return None


def preflight(root, touches, reads, probe_path, timeout=30):
    proc = subprocess.run(command(root, touches, reads), input=preflight_requests(probe_path),
                          capture_output=True, text=True, timeout=timeout, encoding="utf-8")
    return check_preflight(proc.stdout) if proc.returncode == 0 else "file bridge exited " + str(proc.returncode)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True)
    parser.add_argument("--touches", default="")
    parser.add_argument("--reads", default="")
    opts = parser.parse_args(argv)
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8", newline="\n")
    Bridge(opts.root, opts.touches.split(","), opts.reads.split(",")).serve(sys.stdin, sys.stdout)


if __name__ == "__main__":
    main()
