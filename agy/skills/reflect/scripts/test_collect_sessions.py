#!/usr/bin/env python3
# Adapted from warpdotdev/common-skills skill-doctor (MIT, Copyright (c) 2026 Denver Technologies, Inc.)
"""Tests for reflect session collection."""

import contextlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import collect_sessions
from collect_sessions import (
    detect_skills_from_entries,
    discover_hermes_databases,
    discover_skills,
    find_claude_session_files,
    find_hermes_sessions,
    parse_claude_session,
    parse_codex_session,
    parse_hermes_session,
    resolve_hermes_home,
    session_matches_repos,
)

PREVIOUS_FILE_LIMIT = 8 * 1024 * 1024
COLLECTOR = Path(collect_sessions.__file__).resolve()


def write_jsonl(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )


def write_jsonl_past_previous_limit(path, first_record, last_records):
    path.parent.mkdir(parents=True, exist_ok=True)
    filler = json.dumps({"type": "ignored", "padding": "x" * 1024}) + "\n"
    with path.open("w", encoding="utf-8") as stream:
        stream.write(json.dumps(first_record) + "\n")
        while stream.tell() <= PREVIOUS_FILE_LIMIT:
            stream.write(filler)
        for record in last_records:
            stream.write(json.dumps(record) + "\n")


def write_skill(skills_root, name, description="A skill", newline="\n"):
    path = skills_root / name / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = f"---\nname: {name}\ndescription: {description}\n---\nBody\n".replace("\n", newline)
    path.write_bytes(body.encode("utf-8"))
    return path


@contextlib.contextmanager
def fake_environment(home, local_app_data=None):
    """Point Path.home() and the Hermes/Claude/Codex env overrides at a temp tree."""
    with mock.patch.dict(os.environ, {"HOME": str(home), "USERPROFILE": str(home)}):
        for name in ("HERMES_HOME", "LOCALAPPDATA", "CLAUDE_CONFIG_DIR", "CODEX_HOME"):
            os.environ.pop(name, None)
        if local_app_data is not None:
            os.environ["LOCALAPPDATA"] = str(local_app_data)
        yield


class ClaudeSessionTests(unittest.TestCase):
    def test_discovers_skills_and_matches_sessions_across_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            first = root / "first"
            second = root / "second"
            first_skill = first / ".agents" / "skills" / "alpha" / "SKILL.md"
            second_skill = second / ".claude" / "skills" / "beta" / "SKILL.md"
            first_skill.parent.mkdir(parents=True)
            second_skill.parent.mkdir(parents=True)
            first_skill.write_text("---\ndescription: Alpha\n---\n")
            second_skill.write_text("---\ndescription: Beta\n---\n")

            skills = discover_skills(
                [first, second],
                root / "codex-home",
                [],
                False,
            )

            self.assertEqual(set(skills), {"alpha", "beta"})
            self.assertTrue(
                session_matches_repos(second / "src", [first, second])
            )
            self.assertFalse(
                session_matches_repos(root / "elsewhere", [first, second])
            )


    def test_detects_skills_from_deferred_tool_entries(self):
        entries = [
            ("tool:Skill", '{"skill": "alpha"}'),
            ("tool:read", '{"path": "/repo/.agents/skills/beta/SKILL.md"}'),
            ("assistant", "Mentioning gamma here does not count."),
        ]

        self.assertEqual(
            detect_skills_from_entries(entries, {"alpha", "beta", "gamma"}),
            {"alpha", "beta"},
        )

    def test_discovers_parent_sessions_and_optional_subagents(self):
        with tempfile.TemporaryDirectory() as tmp:
            claude_home = Path(tmp)
            parent = claude_home / "projects" / "-repo" / "parent.jsonl"
            subagent = (
                claude_home
                / "projects"
                / "-repo"
                / "parent"
                / "subagents"
                / "agent-child.jsonl"
            )
            old = claude_home / "projects" / "-repo" / "old.jsonl"
            for path in (parent, subagent, old):
                write_jsonl(path, [{"type": "user"}])
            old_time = (datetime.now(timezone.utc) - timedelta(days=10)).timestamp()
            os.utime(old, (old_time, old_time))
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)

            parents = find_claude_session_files(claude_home, cutoff, False)
            with_subagents = find_claude_session_files(claude_home, cutoff, True)

            self.assertEqual([path for _, path in parents], [parent])
            self.assertEqual(
                {path for _, path in with_subagents},
                {parent, subagent},
            )

    def test_parses_messages_tools_skills_and_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "session.jsonl"
            common = {
                "sessionId": "session-1",
                "cwd": "/tmp/repo",
                "timestamp": "2026-08-20T10:00:00Z",
                "version": "1.0.0",
            }
            write_jsonl(path, [
                {
                    **common,
                    "type": "user",
                    "uuid": "user-1",
                    "message": {"role": "user", "content": "Improve my skill"},
                },
                {
                    **common,
                    "type": "assistant",
                    "uuid": "assistant-1",
                    "message": {
                        "id": "message-1",
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "I will inspect it."},
                            {
                                "type": "tool_use",
                                "name": "Skill",
                                "input": {"skill": "update-skill"},
                            },
                        ],
                    },
                },
                {
                    **common,
                    "type": "assistant",
                    "uuid": "assistant-2",
                    "message": {
                        "id": "message-1",
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "name": "Edit",
                                "input": {"file_path": "/tmp/repo/SKILL.md"},
                            }
                        ],
                    },
                },
                {
                    **common,
                    "type": "user",
                    "uuid": "result-1",
                    "message": {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "is_error": True,
                                "content": "permission denied",
                            }
                        ],
                    },
                },
            ])

            meta, stats, entries, skills = parse_claude_session(
                path,
                {"update-skill"},
                False,
            )

            self.assertEqual(meta["id"], "session-1")
            self.assertEqual(meta["cwd"], "/tmp/repo")
            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["assistant_turns"], 1)
            self.assertEqual(stats["tool_calls"], 2)
            self.assertEqual(stats["error_outputs"], 1)
            self.assertTrue(stats["has_code_edits"])
            self.assertEqual(skills, ["update-skill"])
            self.assertIn(("user", "Improve my skill"), entries)
            self.assertIn(("assistant", "I will inspect it."), entries)

    def test_excludes_sidechains_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "agent-child.jsonl"
            write_jsonl(path, [{
                "type": "user",
                "sessionId": "session-1",
                "agentId": "child-1",
                "isSidechain": True,
                "cwd": "/tmp/repo",
                "timestamp": "2026-08-20T10:00:00Z",
                "message": {"role": "user", "content": "Investigate"},
            }])

            self.assertIsNone(parse_claude_session(path, set(), False))
            parsed = parse_claude_session(path, set(), True)
            self.assertEqual(parsed[0]["id"], "session-1-child-1")
            self.assertEqual(parsed[0]["thread_source"], "subagent")



class StreamingSessionReadTests(unittest.TestCase):
    def test_claude_and_codex_parse_records_after_previous_file_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude_path = root / "claude.jsonl"
            codex_path = root / "codex.jsonl"
            write_jsonl_past_previous_limit(
                claude_path,
                {
                    "type": "user",
                    "sessionId": "claude-session",
                    "cwd": "/tmp/repo",
                    "timestamp": "2026-08-30T10:00:00Z",
                    "message": {"role": "user", "content": "hello"},
                },
                [{
                    "type": "assistant",
                    "sessionId": "claude-session",
                    "cwd": "/tmp/repo",
                    "timestamp": "2026-08-30T10:01:00Z",
                    "message": {
                        "id": "late-message",
                        "role": "assistant",
                        "content": [
                            {"type": "text", "text": "late claude message"},
                            {
                                "type": "tool_use",
                                "name": "Read",
                                "input": {
                                    "file_path": "/tmp/.agents/skills/late-skill/SKILL.md"
                                },
                            },
                        ],
                    },
                }],
            )
            write_jsonl_past_previous_limit(
                codex_path,
                {
                    "type": "session_meta",
                    "payload": {"id": "codex-session", "cwd": "/tmp/repo"},
                },
                [{
                    "type": "response_item",
                    "timestamp": "2026-08-30T10:00:30Z",
                    "payload": {
                        "type": "function_call",
                        "name": "read_file",
                        "arguments": {
                            "path": "/tmp/.codex/skills/late-skill/SKILL.md",
                            "operation": "apply_patch",
                        },
                    },
                }, {
                    "type": "response_item",
                    "timestamp": "2026-08-30T10:01:00Z",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "text", "text": "late codex message"}],
                    },
                }],
            )

            parsed_claude = parse_claude_session(claude_path, {"late-skill"}, False)
            parsed_codex = parse_codex_session(codex_path, {"late-skill"}, False)

            self.assertEqual(parsed_claude[1]["assistant_turns"], 1)
            self.assertEqual(parsed_claude[1]["tool_calls"], 1)
            self.assertEqual(parsed_claude[3], ["late-skill"])
            self.assertIn(("assistant", "late claude message"), parsed_claude[2])
            self.assertEqual(parsed_codex[1]["tool_calls"], 1)
            self.assertTrue(parsed_codex[1]["has_code_edits"])
            self.assertEqual(parsed_codex[3], ["late-skill"])
            self.assertIn(("assistant", "late codex message"), parsed_codex[2])

    def test_codex_keeps_only_transcript_head_and_tail_while_parsing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "codex.jsonl"
            records = [{
                "type": "session_meta",
                "payload": {"id": "codex-session", "cwd": "/tmp/repo"},
            }]
            for index in range(201):
                records.extend(({
                    "type": "event_msg",
                    "payload": {"type": "agent_message"},
                }, {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "text", "text": f"message-{index}"}],
                    },
                }))
            write_jsonl(path, records)

            _, stats, entries, _ = parse_codex_session(path, set(), False)

            self.assertEqual(stats["assistant_turns"], 201)
            self.assertEqual(len(entries), 141)
            self.assertEqual(entries[0], ("assistant", "message-0"))
            self.assertEqual(entries[99], ("assistant", "message-99"))
            self.assertEqual(entries[100], ("note", "[... 61 entries omitted ...]"))
            self.assertEqual(entries[101], ("assistant", "message-161"))
            self.assertEqual(entries[-1], ("assistant", "message-200"))



class CodexMessageCountTests(unittest.TestCase):
    def test_counts_turns_from_response_items_when_no_event_msgs_exist(self):
        # Current Codex rollouts carry no user_message/agent_message events.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rollout-new.jsonl"
            write_jsonl(path, [
                {"type": "session_meta", "payload": {"id": "new", "cwd": "/tmp/repo"}},
                {"type": "response_item", "payload": {
                    "type": "message", "role": "user",
                    "content": [{"type": "input_text", "text": "Fix it"}]}},
                {"type": "response_item", "payload": {
                    "type": "message", "role": "assistant",
                    "content": [{"type": "output_text", "text": "Looking."}]}},
                {"type": "response_item", "payload": {
                    "type": "custom_tool_call", "name": "apply_patch", "input": "*** Begin Patch"}},
            ])

            _, stats, _, _ = parse_codex_session(path, set(), False)

            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["assistant_turns"], 1)
            self.assertEqual(stats["tool_calls"], 1)


class HermesCollectorTests(unittest.TestCase):
    @contextlib.contextmanager
    def hermes_tmp(self):
        """Temp dir whose sqlite connections are closed first (Windows can't delete open files)."""
        self._connections = []
        with tempfile.TemporaryDirectory() as tmp:
            try:
                yield tmp
            finally:
                for connection in self._connections:
                    connection.close()

    def _make_db(self, root):
        db_path = root / "state.db"
        conn = sqlite3.connect(db_path)
        conn.execute(
            """CREATE TABLE sessions (
                id TEXT, source TEXT, cwd TEXT, title TEXT, display_name TEXT,
                parent_session_id TEXT, started_at REAL, last_activity_at REAL, ended_at REAL)"""
        )
        conn.execute(
            """CREATE TABLE messages (
                session_id TEXT, role TEXT, content TEXT, tool_calls TEXT, timestamp REAL)"""
        )
        self._connections.append(conn)
        return conn

    def test_parse_hermes_session_extracts_stats_and_skills(self):
        with self.hermes_tmp() as tmp:
            conn = self._make_db(Path(tmp))
            base = 1_800_000_000.0
            conn.execute(
                "INSERT INTO sessions VALUES ('s1','cli','/tmp/repo','t','d',NULL,?,?,?)",
                (base, base + 60, base + 60),
            )
            conn.execute(
                "INSERT INTO messages VALUES ('s1','user','do the thing',NULL,?)", (base,)
            )
            tool_calls = json.dumps([
                {"function": {"name": "skill_view", "arguments": "{\"name\":\"my-skill\"}"}},
                {"function": {"name": "terminal", "arguments": "ls"}},
            ])
            conn.execute(
                "INSERT INTO messages VALUES ('s1','assistant','ok',?,?)", (tool_calls, base + 1)
            )
            conn.execute(
                "INSERT INTO messages VALUES ('s1','tool','error: boom',NULL,?)", (base + 2,)
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions").fetchone()

            parsed = parse_hermes_session(conn, row, {"my-skill"}, False)

            self.assertIsNotNone(parsed)
            meta, stats, entries, skills_used = parsed
            self.assertEqual(meta["id"], "s1")
            self.assertEqual(meta["started_at"], datetime.fromtimestamp(base, tz=timezone.utc).isoformat())
            self.assertEqual(meta["timestamp"], datetime.fromtimestamp(base + 2, tz=timezone.utc).isoformat())
            self.assertEqual(stats["user_turns"], 1)
            self.assertEqual(stats["assistant_turns"], 1)
            self.assertEqual(stats["tool_calls"], 2)
            self.assertEqual(stats["error_outputs"], 1)
            self.assertEqual(stats["first_ts"], datetime.fromtimestamp(base, tz=timezone.utc).isoformat())
            self.assertEqual(stats["last_ts"], datetime.fromtimestamp(base + 2, tz=timezone.utc).isoformat())
            self.assertEqual(skills_used, ["my-skill"])

    def test_parse_hermes_session_skips_injected_user_content(self):
        with self.hermes_tmp() as tmp:
            conn = self._make_db(Path(tmp))
            base = 1_800_000_000.0
            conn.execute(
                "INSERT INTO sessions VALUES ('s-inj','cli','/tmp/repo',NULL,NULL,NULL,?,?,?)",
                (base, base + 60, base + 60),
            )
            conn.execute(
                "INSERT INTO messages VALUES ('s-inj','user','<environment_context injected>',NULL,?)",
                (base,),
            )
            conn.execute(
                "INSERT INTO messages VALUES ('s-inj','assistant','ok',?,?)",
                (json.dumps([{"function": {"name": "terminal", "arguments": "ls"}}]), base + 1),
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions WHERE id='s-inj'").fetchone()

            parsed = parse_hermes_session(conn, row, set(), False)

            self.assertIsNotNone(parsed)
            _, stats, entries, _ = parsed
            self.assertEqual(stats["user_turns"], 0)
            self.assertFalse(any(role == "user" for role, _ in entries))

    def test_parse_hermes_session_skips_subagents(self):
        with self.hermes_tmp() as tmp:
            conn = self._make_db(Path(tmp))
            base = 1_800_000_000.0
            conn.execute(
                "INSERT INTO sessions VALUES ('s2','subagent','/tmp',NULL,NULL,'parent',?,?,?)",
                (base, base, base),
            )
            conn.execute(
                "INSERT INTO messages VALUES ('s2','assistant','hi',?,?)",
                (json.dumps([{"function": {"name": "terminal", "arguments": "ls"}}]), base),
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions").fetchone()

            self.assertIsNone(parse_hermes_session(conn, row, set(), False))
            self.assertIsNotNone(parse_hermes_session(conn, row, set(), True))

    def test_find_hermes_sessions_filters_by_cutoff(self):
        with self.hermes_tmp() as tmp:
            root = Path(tmp)
            conn = self._make_db(root)
            old, new = 1_000_000_000.0, datetime.now(tz=timezone.utc).timestamp()
            for sid, started_at, last_activity_at, ended_at in (
                ("old", old, old, old),
                ("recent", new - 30, new - 30, new - 30),
                ("completed", old, None, new),
            ):
                conn.execute(
                    "INSERT INTO sessions VALUES (?,?,?,?,?,NULL,?,?,?)",
                    (sid, "cli", "/tmp", None, None, started_at, last_activity_at, ended_at),
                )
            conn.commit()
            conn.close()

            records, scanned = find_hermes_sessions(
                [root / "state.db"], datetime.fromtimestamp(new - 60, tz=timezone.utc)
            )

            self.assertEqual(scanned, 2)
            self.assertEqual([row["id"] for _, row in records], ["completed", "recent"])

    def test_find_hermes_sessions_skips_incompatible_messages_schema(self):
        with self.hermes_tmp() as tmp:
            root = Path(tmp)
            db_path = root / "state.db"
            conn = sqlite3.connect(db_path)
            conn.execute(
                """CREATE TABLE sessions (
                    id TEXT, source TEXT, cwd TEXT, title TEXT, display_name TEXT,
                    parent_session_id TEXT, started_at REAL, last_activity_at REAL, ended_at REAL)"""
            )
            conn.execute(
                """CREATE TABLE messages (
                    session_id TEXT, role TEXT, content TEXT, timestamp REAL)"""
            )
            ts = datetime.now(tz=timezone.utc).timestamp()
            conn.execute(
                "INSERT INTO sessions VALUES ('bad','cli','/tmp',NULL,NULL,NULL,?,?,?)",
                (ts, ts, ts),
            )
            conn.commit()
            conn.close()

            records, scanned = find_hermes_sessions(
                [db_path], datetime.fromtimestamp(ts - 60, tz=timezone.utc)
            )

            self.assertEqual(records, [])
            self.assertEqual(scanned, 0)

    def test_parse_hermes_session_counts_repeated_calls_by_name_and_args(self):
        with self.hermes_tmp() as tmp:
            conn = self._make_db(Path(tmp))
            base = 1_800_000_000.0
            conn.execute(
                "INSERT INTO sessions VALUES ('s3','cli','/tmp/repo',NULL,NULL,NULL,?,?,?)",
                (base, base + 60, base + 60),
            )
            tool_calls = json.dumps([
                {"function": {"name": "terminal", "arguments": "ls"}},
                {"function": {"name": "terminal", "arguments": "pwd"}},
                {"function": {"name": "terminal", "arguments": "ls"}},
            ])
            conn.execute(
                "INSERT INTO messages VALUES ('s3','assistant','ok',?,?)", (tool_calls, base + 1)
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions WHERE id='s3'").fetchone()

            parsed = parse_hermes_session(conn, row, set(), False)

            self.assertIsNotNone(parsed)
            _, stats, _, _ = parsed
            self.assertEqual(stats["tool_calls"], 3)
            self.assertEqual(stats["repeated_tool_calls"], 1)

    def test_parse_hermes_session_handles_non_string_tool_args(self):
        with self.hermes_tmp() as tmp:
            conn = self._make_db(Path(tmp))
            base = 1_800_000_000.0
            conn.execute(
                "INSERT INTO sessions VALUES ('s4','cli','/tmp/repo',NULL,NULL,NULL,?,?,?)",
                (base, base + 60, base + 60),
            )
            tool_calls = json.dumps([
                {"function": {"name": "skill_view", "arguments": {"name": "my-skill"}}},
            ])
            conn.execute(
                "INSERT INTO messages VALUES ('s4','assistant','ok',?,?)", (tool_calls, base + 1)
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions WHERE id='s4'").fetchone()

            parsed = parse_hermes_session(conn, row, {"my-skill"}, False)

            self.assertIsNotNone(parsed)
            _, stats, entries, skills_used = parsed
            self.assertEqual(stats["tool_calls"], 1)
            self.assertIn(("tool:skill_view", '{"name": "my-skill"}'), entries)
            self.assertEqual(skills_used, ["my-skill"])

    def test_parse_hermes_session_reads_top_level_tool_call_shape(self):
        with self.hermes_tmp() as tmp:
            conn = self._make_db(Path(tmp))
            base = 1_800_000_000.0
            conn.execute(
                "INSERT INTO sessions VALUES ('s5','cli','/tmp/repo',NULL,NULL,NULL,?,?,?)",
                (base, base + 60, base + 60),
            )
            tool_calls = json.dumps([
                {"name": "skill_view", "arguments": '{"name":"my-skill"}'},
            ])
            conn.execute(
                "INSERT INTO messages VALUES ('s5','assistant','ok',?,?)", (tool_calls, base + 1)
            )
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM sessions WHERE id='s5'").fetchone()

            parsed = parse_hermes_session(conn, row, {"my-skill"}, False)

            self.assertIsNotNone(parsed)
            _, stats, entries, skills_used = parsed
            self.assertEqual(stats["tool_calls"], 1)
            self.assertIn(("tool:skill_view", '{"name":"my-skill"}'), entries)
            self.assertEqual(skills_used, ["my-skill"])

    def test_discover_hermes_databases_resolves_relative_home(self):
        with self.hermes_tmp() as tmp:
            root = Path(tmp)
            hermes_home = root / "hermes-home"
            hermes_home.mkdir()
            (hermes_home / "state.db").write_text("sqlite", encoding="utf-8")

            old_cwd = Path.cwd()
            try:
                os.chdir(root)
                discovered = discover_hermes_databases("hermes-home")
            finally:
                os.chdir(old_cwd)

            self.assertEqual(discovered[0], (hermes_home / "state.db").resolve())

    def test_discover_hermes_databases_explicit_path_is_authoritative(self):
        with self.hermes_tmp() as tmp:
            home = Path(tmp)
            env_home = home / "env-hermes"
            env_home.mkdir()
            (env_home / "state.db").write_text("sqlite", encoding="utf-8")
            bad_path = home / "does-not-exist"

            with fake_environment(home):
                os.environ["HERMES_HOME"] = str(env_home)
                discovered = discover_hermes_databases(str(bad_path))

            self.assertEqual(discovered, [])

    def test_resolve_hermes_home_prefers_dot_hermes_when_present(self):
        with self.hermes_tmp() as tmp:
            home = Path(tmp)
            dot_hermes = home / ".hermes"
            dot_hermes.mkdir()
            (dot_hermes / "state.db").write_text("sqlite", encoding="utf-8")

            with fake_environment(home):
                resolved = resolve_hermes_home(None)

            self.assertEqual(resolved, dot_hermes.resolve())


class HermesWindowsLocationTests(unittest.TestCase):
    """Hermes on Windows keeps state.db under %LOCALAPPDATA%\\hermes, not ~/.hermes."""

    def test_discovers_state_db_under_localappdata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            local_hermes = root / "AppData" / "Local" / "hermes"
            local_hermes.mkdir(parents=True)
            (local_hermes / "state.db").write_text("sqlite", encoding="utf-8")

            with fake_environment(root / "home", local_app_data=root / "AppData" / "Local"):
                discovered = discover_hermes_databases(None)
                resolved = resolve_hermes_home(None)

            self.assertEqual(discovered, [(local_hermes / "state.db").resolve()])
            self.assertEqual(resolved, local_hermes.resolve())

    def test_hermes_home_env_wins_then_dot_hermes_is_a_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            env_home = root / "env-hermes"
            local_hermes = root / "local" / "hermes"
            dot_hermes = home / ".hermes"
            for directory in (env_home, local_hermes, dot_hermes):
                directory.mkdir(parents=True)
                (directory / "state.db").write_text("sqlite", encoding="utf-8")

            with fake_environment(home, local_app_data=root / "local"):
                everywhere = discover_hermes_databases(None)
                os.environ["HERMES_HOME"] = str(env_home)
                with_env = discover_hermes_databases(None)
                os.environ.pop("HERMES_HOME")
                (local_hermes / "state.db").unlink()
                fallback = discover_hermes_databases(None)

            self.assertEqual(
                everywhere,
                [(local_hermes / "state.db").resolve(), (dot_hermes / "state.db").resolve()],
            )
            self.assertEqual(with_env[0], (env_home / "state.db").resolve())
            self.assertEqual(fallback, [(dot_hermes / "state.db").resolve()])


class ClaudeProjectSlugTests(unittest.TestCase):
    def test_every_non_alphanumeric_becomes_a_dash(self):
        slug = collect_sessions.claude_project_slug
        self.assertEqual(slug(r"C:\Users\me\repo"), "C--Users-me-repo")
        self.assertEqual(slug(r"C:\Users\me\my repo.v2_x"), "C--Users-me-my-repo-v2-x")
        self.assertEqual(slug("/home/me/repo"), "-home-me-repo")

    @unittest.skipUnless(os.name == "nt", "needs Windows path semantics")
    def test_session_file_in_matching_project_dir_is_in_scope_without_cwd(self):
        claude_home = Path("claude-home")
        repo = Path(r"C:\Users\me\repo")
        parent = claude_home / "projects" / "C--Users-me-repo" / "s.jsonl"
        subagent = claude_home / "projects" / "C--Users-me-repo" / "s" / "subagents" / "a.jsonl"
        other = claude_home / "projects" / "C--Users-me-other" / "s.jsonl"

        matches = collect_sessions.claude_file_matches_repos
        self.assertTrue(matches(parent, claude_home, [repo]))
        self.assertTrue(matches(subagent, claude_home, [repo]))
        self.assertFalse(matches(other, claude_home, [repo]))


class SkillDiscoveryTests(unittest.TestCase):
    def test_discovers_global_skills_from_every_known_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            hermes_home = root / "local" / "hermes"
            write_skill(home / ".claude" / "skills", "claude-skill")
            write_skill(home / ".agents" / "skills", "agents-skill")
            write_skill(home / ".codex" / "skills", "codex-skill")
            write_skill(home / ".config" / "opencode" / "skills", "opencode-skill")
            write_skill(hermes_home / "skills" / "devops", "hermes-skill")

            with fake_environment(home):
                skills = discover_skills(
                    [], home / ".codex", [], True, hermes_home=hermes_home
                )
                project_only = discover_skills([], home / ".codex", [], False)

            self.assertEqual(
                {name: skill["source"] for name, skill in skills.items()},
                {
                    "claude-skill": "claude",
                    "agents-skill": "agents",
                    "codex-skill": "codex",
                    "opencode-skill": "opencode",
                    "hermes-skill": "hermes",
                },
            )
            self.assertEqual(project_only, {})

    def test_discovers_project_skills_in_all_four_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            for directory, name in (
                (".agents", "a"), (".claude", "b"), (".codex", "c"), (".opencode", "d"),
            ):
                write_skill(repo / directory / "skills", name)

            skills = discover_skills([repo], Path(tmp) / "codex-home", [], False)

            self.assertEqual(set(skills), {"a", "b", "c", "d"})
            self.assertEqual({s["source"] for s in skills.values()}, {"project"})

    def test_nested_hermes_skills_are_found_and_archive_and_hub_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hermes_home = root / "hermes"
            skills_root = hermes_home / "skills"
            write_skill(skills_root / "devops", "deploy-helper")
            write_skill(skills_root / "mlops" / "inference", "llama-cpp")
            write_skill(skills_root, "top-level")
            write_skill(skills_root / ".archive", "retired")
            write_skill(skills_root / ".hub" / "official", "hub-skill")
            write_skill(skills_root / "devops" / ".archive", "retired-in-category")

            with fake_environment(root / "home"):
                skills = discover_skills(
                    [], root / "codex-home", [], True, hermes_home=hermes_home
                )

            self.assertEqual(set(skills), {"deploy-helper", "llama-cpp", "top-level"})
            self.assertEqual(
                skills["deploy-helper"]["path"],
                str(skills_root / "devops" / "deploy-helper" / "SKILL.md"),
            )

    def test_mirrored_skills_count_once_and_record_every_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            hermes_home = root / "hermes"
            mirrors = [
                write_skill(home / ".claude" / "skills", "mirrored"),
                write_skill(home / ".agents" / "skills", "mirrored"),
                # A CRLF checkout of the same content is still the same skill.
                write_skill(home / ".codex" / "skills", "mirrored", newline="\r\n"),
                write_skill(hermes_home / "skills" / "tools", "mirrored"),
            ]
            write_skill(home / ".agents" / "skills", "unique")

            with fake_environment(home):
                skills = discover_skills(
                    [], home / ".codex", [], True, hermes_home=hermes_home
                )

            self.assertEqual(set(skills), {"mirrored", "unique"})
            self.assertEqual(skills["mirrored"]["paths"], [str(path) for path in mirrors])
            self.assertEqual(
                skills["mirrored"]["sources"], ["claude", "agents", "codex", "hermes"]
            )
            self.assertEqual(skills["mirrored"]["path"], str(mirrors[0]))
            self.assertNotIn("shadowed_paths", skills["mirrored"])

    def test_same_name_with_different_content_is_not_merged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            first = write_skill(home / ".claude" / "skills", "forked", "Version one")
            second = write_skill(home / ".agents" / "skills", "forked", "Version two")

            with fake_environment(home):
                skills = discover_skills([], home / ".codex", [], True)

            self.assertEqual(skills["forked"]["description"], "Version one")
            self.assertEqual(skills["forked"]["paths"], [str(first)])
            self.assertEqual(skills["forked"]["shadowed_paths"], [str(second)])


class CollectorCliTests(unittest.TestCase):
    """Run the collector end to end against a synthetic Windows-style home."""

    def test_collects_all_three_sources_and_writes_utf8_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            local_app_data = root / "AppData" / "Local"
            repo = root / "work" / "my répo"
            repo.mkdir(parents=True)
            now = datetime.now(timezone.utc)
            stamp = now.isoformat()
            accent = "caf\u00e9 \u2713"

            write_skill(home / ".claude" / "skills", "alpha")
            write_skill(home / ".agents" / "skills", "alpha")
            write_skill(local_app_data / "hermes" / "skills" / "notes", "beta")
            write_skill(local_app_data / "hermes" / "skills" / ".archive", "gone")

            slug = collect_sessions.claude_project_slug(repo)
            common = {"sessionId": "claude-1", "cwd": str(repo), "timestamp": stamp}
            write_jsonl(home / ".claude" / "projects" / slug / "claude-1.jsonl", [
                {**common, "type": "user",
                 "message": {"role": "user", "content": f"Please review {accent}"}},
                {**common, "type": "assistant", "message": {
                    "id": "m1", "role": "assistant", "content": [
                        {"type": "text", "text": "On it."},
                        {"type": "tool_use", "name": "Skill", "input": {"skill": "alpha"}},
                    ]}},
            ])
            write_jsonl(home / ".codex" / "sessions" / "2026" / "rollout-codex-1.jsonl", [
                {"type": "session_meta",
                 "payload": {"id": "codex-1", "cwd": str(repo), "timestamp": stamp}},
                {"type": "event_msg", "timestamp": stamp,
                 "payload": {"type": "agent_message"}},
                {"type": "response_item", "timestamp": stamp, "payload": {
                    "type": "message", "role": "assistant",
                    "content": [{"type": "output_text", "text": "Reading."}]}},
                {"type": "response_item", "timestamp": stamp, "payload": {
                    "type": "function_call", "name": "shell", "arguments": "{\"cmd\": \"ls\"}"}},
            ])

            hermes_dir = local_app_data / "hermes"
            connection = sqlite3.connect(hermes_dir / "state.db")
            connection.execute(
                """CREATE TABLE sessions (
                    id TEXT, source TEXT, cwd TEXT, title TEXT, display_name TEXT,
                    parent_session_id TEXT, started_at REAL, last_activity_at REAL, ended_at REAL)"""
            )
            connection.execute(
                """CREATE TABLE messages (
                    session_id TEXT, role TEXT, content TEXT, tool_calls TEXT, timestamp REAL)"""
            )
            epoch = now.timestamp()
            connection.execute(
                "INSERT INTO sessions VALUES ('hermes-1','cli',?,NULL,NULL,NULL,?,?,?)",
                (str(repo), epoch, epoch, epoch),
            )
            connection.execute(
                "INSERT INTO messages VALUES ('hermes-1','assistant','ok',?,?)",
                (json.dumps([{"function": {"name": "skill_view",
                                           "arguments": "{\"name\": \"beta\"}"}}]), epoch),
            )
            connection.commit()
            connection.close()

            out = root / "out"
            env = {
                key: value for key, value in os.environ.items()
                if key not in ("HERMES_HOME", "CLAUDE_CONFIG_DIR", "CODEX_HOME")
            }
            env.update(
                HOME=str(home), USERPROFILE=str(home), LOCALAPPDATA=str(local_app_data)
            )
            result = subprocess.run(
                [sys.executable, "-I", str(COLLECTOR), "--out", str(out),
                 "--repo", str(repo), "--include-global-skills"],
                capture_output=True, text=True, encoding="utf-8", env=env, timeout=120,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            raw = (out / "inventory.json").read_text(encoding="utf-8")
            inventory = json.loads(raw)
            self.assertEqual(set(inventory["sources"]), {"claude", "codex", "hermes"})
            self.assertEqual(inventory["hermes_home"], str((local_app_data / "hermes").resolve()))
            self.assertEqual({s["name"] for s in inventory["skills"]}, {"alpha", "beta"})
            alpha = next(s for s in inventory["skills"] if s["name"] == "alpha")
            self.assertEqual(len(alpha["paths"]), 2)
            self.assertEqual(inventory["stats"]["skills_found"], 2)
            self.assertEqual(inventory["stats"]["sessions_sampled"], 3)
            self.assertEqual(inventory["skill_usage"], {"alpha": 1, "beta": 1})
            self.assertIn("my répo", raw)  # ensure_ascii=False keeps non-ASCII unescaped
            transcripts = sorted(path.name for path in (out / "transcripts").iterdir())
            self.assertEqual(
                transcripts,
                ["claude-claude-1.md", "codex-codex-1.md", "hermes-hermes-1.md"],
            )
            transcript = (out / "transcripts" / "claude-claude-1.md").read_text(encoding="utf-8")
            self.assertIn(accent, transcript)


if __name__ == "__main__":
    unittest.main()
