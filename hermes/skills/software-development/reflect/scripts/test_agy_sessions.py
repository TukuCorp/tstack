#!/usr/bin/env python3
"""Tests for reading agy (Antigravity CLI) conversations, built in agy's real protobuf wire layout."""

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import collect_sessions
from agy_sessions import find_agy_sessions, parse_agy_session

COLLECTOR = Path(collect_sessions.__file__).resolve()


def varint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | (0x80 if n else 0))
        if not n:
            return bytes(out)


def fld(num, value):
    if isinstance(value, int):
        return varint(num << 3) + varint(value)
    if isinstance(value, str):
        value = value.encode("utf-8")
    return varint(num << 3 | 2) + varint(len(value)) + value


def msg(*parts):
    return b"".join(parts)


def meta(epoch):
    return fld(5, msg(fld(1, msg(fld(1, epoch), fld(2, 5)))))


def user_step(text, workspace_uri, epoch):
    return msg(fld(1, 14), meta(epoch), fld(19, msg(fld(2, text), fld(12, msg(fld(12, workspace_uri))))))


def model_step(reply, calls, epoch):
    body = [fld(3, "thinking...")]
    if reply:
        body.insert(0, fld(1, reply))
    for cid, name, args in calls:
        body.append(fld(7, msg(fld(1, cid), fld(2, name), fld(3, json.dumps(args)))))
    return msg(fld(1, 15), meta(epoch), fld(20, msg(*body)))


def result_step(text, epoch):
    return msg(fld(1, 132), meta(epoch), fld(140, msg(fld(1, msg(fld(1, "Path"), fld(2, "x"))),
                                                     fld(2, msg(fld(1, text))))))


def write_conversation(path, steps):
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE steps (idx integer, step_type integer, step_payload blob)")
    for i, payload in enumerate(steps):
        step_type = {14: 14, 15: 15, 132: 132}[payload[1]]  # payload starts with field 1 (type)
        con.execute("INSERT INTO steps VALUES (?,?,?)", (i, step_type, payload))
    con.commit()
    con.close()


def sample_steps(repo, epoch):
    uri = "file:///" + str(repo).replace("\\", "/")
    return [
        user_step("\x1b]11;rgb:0d0d/0202/0808Coop run. Fix the deck", uri, epoch),
        model_step("", [("c1", "read_file", {"Path": "C:/Users/x/.gemini/config/skills/coop/SKILL.md"}),
                        ("c2", "run_command", {"CommandLine": "python -X utf8 build.py"})], epoch + 1),
        result_step("Traceback (most recent call last): boom", epoch + 2),
        model_step("", [("c3", "run_command", {"CommandLine": "python -X utf8 build.py"})], epoch + 3),
        model_step("Done: PASS", [("c4", "write_file", {"TargetFile": "a.py"})], epoch + 4),
    ]


class AgyParseTests(unittest.TestCase):
    def test_parses_turns_tools_cwd_and_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "work" / "deck"
            db = Path(tmp) / "conversations" / "conv-1.db"
            epoch = int(time.time())
            write_conversation(db, sample_steps(repo, epoch))
            meta, stats, entries, skills = parse_agy_session(db, {"coop", "verify"}, {})
        self.assertEqual(meta["id"], "conv-1")
        self.assertEqual(Path(meta["cwd"]), repo)
        self.assertEqual(stats["user_turns"], 1)
        self.assertEqual(stats["assistant_turns"], 3)
        self.assertEqual(stats["tool_calls"], 4)
        self.assertEqual(stats["repeated_tool_calls"], 1)
        self.assertEqual(stats["error_outputs"], 1)
        self.assertTrue(stats["has_code_edits"])
        self.assertEqual(skills, ["coop"])
        text = "\n".join(str(e) for e in entries)
        self.assertIn("Coop run. Fix the deck", text)
        self.assertNotIn("rgb:0d0d", text)  # herdr's terminal colour reply is stripped
        self.assertIn("Done: PASS", text)
        self.assertIn("tool:run_command", text)
        self.assertIn("Traceback", text)

    def test_cutoff_and_empty_conversations(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            epoch = int(time.time())
            write_conversation(home / "conversations" / "new.db", sample_steps(home, epoch))
            write_conversation(home / "conversations" / "old.db", sample_steps(home, epoch))
            old = time.time() - 10 * 86400
            os.utime(home / "conversations" / "old.db", (old, old))
            write_conversation(home / "conversations" / "empty.db", [user_step("hi", "", epoch)])
            dbs, scanned = find_agy_sessions(home, datetime.now(timezone.utc) - timedelta(days=4))
            self.assertEqual(sorted(p.stem for p in dbs), ["empty", "new"])
            self.assertIsNone(parse_agy_session(home / "conversations" / "empty.db", set(), {}))


class AgyCollectorCliTests(unittest.TestCase):
    def test_collector_reads_agy_home_and_agy_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            repo = root / "work" / "deck"
            repo.mkdir(parents=True)
            skill = home / ".gemini" / "config" / "skills" / "coop"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: coop\ndescription: pair run\n---\nbody\n", encoding="utf-8")
            agy_home = home / ".gemini" / "antigravity-cli"
            write_conversation(agy_home / "conversations" / "conv-9.db", sample_steps(repo, int(time.time())))
            out = root / "out"
            env = {k: v for k, v in os.environ.items() if k not in ("HERMES_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME")}
            env.update(HOME=str(home), USERPROFILE=str(home), LOCALAPPDATA=str(root / "AppData" / "Local"))
            result = subprocess.run(
                [sys.executable, "-I", str(COLLECTOR), "--out", str(out), "--harness", "agy",
                 "--all-conversations", "--include-global-skills", "--days", "4"],
                capture_output=True, text=True, encoding="utf-8", env=env, timeout=120)
            self.assertEqual(result.returncode, 0, result.stderr)
            inv = json.loads((out / "inventory.json").read_text(encoding="utf-8"))
            self.assertEqual(set(inv["sources"]), {"agy"})
            self.assertEqual(inv["skill_usage"], {"coop": 1})
            self.assertEqual([p.name for p in (out / "transcripts").iterdir()], ["agy-conv-9.md"])


if __name__ == "__main__":
    unittest.main()
