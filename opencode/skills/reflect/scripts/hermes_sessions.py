# Adapted from warpdotdev/common-skills skill-doctor (MIT, Copyright (c) 2026 Denver Technologies, Inc.)
"""Read Hermes Agent sessions from its state.db for collect_sessions.py."""

import hashlib
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from session_common import (
    CODE_EDIT_HINTS,
    GENERIC_EDIT_TOOLS,
    MAX_MSG_CHARS,
    MAX_TOOL_CHARS,
    TranscriptBuffer,
    detect_skill_candidates,
    looks_injected,
    truncate,
)


def open_readonly_database(path):
    connection = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True, timeout=2)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only = ON")
    return connection


def sqlite_table_columns(connection, table):
    return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}


def hermes_default_roots():
    """Candidate Hermes homes: HERMES_HOME, %LOCALAPPDATA%/hermes, ~/.hermes, then ~."""
    roots = []
    env_home = os.environ.get("HERMES_HOME")
    if env_home:
        roots.append(Path(env_home).expanduser())
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        roots.append(Path(local_app_data) / "hermes")
    roots.extend((Path.home() / ".hermes", Path.home()))
    return roots


def resolve_hermes_home(explicit_path=None):
    """Resolve the Hermes home used for global skill discovery.

    Preference order matches database discovery: explicit path, HERMES_HOME,
    %LOCALAPPDATA%/hermes, ~/.hermes, then ~/.
    """
    roots = []
    if explicit_path:
        roots.append(Path(explicit_path).expanduser())
    roots.extend(hermes_default_roots())

    resolved_roots = []
    seen = set()
    for root in roots:
        try:
            resolved = root.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        resolved_roots.append(resolved)

    for root in resolved_roots:
        if (root / "state.db").is_file():
            return root
    return resolved_roots[0] if resolved_roots else Path.home().resolve()


def discover_hermes_databases(explicit_path=None):
    """Find Hermes Agent ``state.db`` files (HERMES_HOME, %LOCALAPPDATA%/hermes, ~/.hermes, ~)."""
    if explicit_path:
        roots = [Path(explicit_path).expanduser()]
    else:
        roots = hermes_default_roots()
    seen = set()
    databases = []
    for root in roots:
        try:
            resolved_root = root.resolve()
        except OSError:
            continue
        candidate = resolved_root / "state.db"
        if candidate in seen or not candidate.is_file():
            continue
        seen.add(candidate)
        databases.append(candidate)
    return databases


def hermes_database_has_sessions(connection):
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'sessions'"
    ).fetchone()
    return row is not None


def parse_epoch_timestamp(value):
    """Parse a float/int epoch-seconds column into an aware UTC datetime."""
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def assistant_tool_calls(message):
    """Extract (name, args_text) pairs from OpenAI-style tool_calls entries."""
    calls = []
    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        fn = call.get("function") or {}
        name = call.get("name") or fn.get("name") or "unknown"
        args = call.get("arguments")
        if args is None:
            args = fn.get("arguments")
        if not isinstance(args, str):
            args = json.dumps(args, ensure_ascii=False)
        calls.append((str(name), args))
    return calls


def parse_hermes_session(connection, session_row, skill_names, include_subagents: bool):
    """Normalize one Hermes Agent session (from state.db) to the shared transcript shape."""
    if session_row["parent_session_id"] and not include_subagents:
        return None
    meta = {
        "id": session_row["id"],
        "source": session_row["source"] or "cli",
        "cwd": session_row["cwd"],
        "title": session_row["title"] or session_row["display_name"],
    }
    stats = {
        "user_turns": 0,
        "assistant_turns": 0,
        "tool_calls": 0,
        "repeated_tool_calls": 0,
        "error_outputs": 0,
    }
    entries = TranscriptBuffer()
    seen_calls = {}
    used_tool_names = set()
    skills_used = detect_skill_candidates(session_row["cwd"] or "")
    has_code_edit_hint = False
    first_ts = last_ts = None

    rows = connection.execute(
        """
        SELECT role, content, tool_calls, timestamp
        FROM messages
        WHERE session_id = ?
        ORDER BY timestamp
        """,
        (session_row["id"],),
    ).fetchall()
    for row in rows:
        ts = parse_epoch_timestamp(row["timestamp"])
        if ts is not None:
            first_ts = first_ts or ts
            last_ts = ts
        role = row["role"]
        tool_calls_raw = row["tool_calls"]
        content = row["content"] or ""
        if role == "user" and content.strip():
            if looks_injected(content):
                continue
            stats["user_turns"] += 1
            entries.append(("user", truncate(content, MAX_MSG_CHARS)))
        elif role == "assistant":
            stats["assistant_turns"] += 1
            if content.strip() and not looks_injected(content):
                skills_used |= detect_skill_candidates(content) & set(skill_names)
                entries.append(("assistant", truncate(content, MAX_MSG_CHARS)))
            if tool_calls_raw:
                try:
                    parsed_calls = json.loads(tool_calls_raw)
                except ValueError:
                    parsed_calls = []
                for tool, args_text in assistant_tool_calls({"tool_calls": parsed_calls}):
                    stats["tool_calls"] += 1
                    used_tool_names.add(tool)
                    if tool in CODE_EDIT_HINTS or tool in GENERIC_EDIT_TOOLS:
                        has_code_edit_hint = True
                    call_key = hashlib.sha1((tool + args_text).encode()).hexdigest()
                    seen_calls[call_key] = seen_calls.get(call_key, 0) + 1
                    for name in detect_skill_candidates(args_text) & set(skill_names):
                        skills_used.add(name)
                    if tool == "skill_view":
                        try:
                            payload = json.loads(args_text)
                            name = (payload or {}).get("name")
                            if name in skill_names:
                                skills_used.add(name)
                        except (ValueError, TypeError):
                            pass
                    entries.append((f"tool:{tool}", truncate(args_text, MAX_TOOL_CHARS)))
        elif role == "tool" and content.strip():
            lowered = content[:200].lower()
            if "error" in lowered or "traceback" in lowered:
                stats["error_outputs"] += 1
            entries.append(("tool_output", truncate(content, MAX_TOOL_CHARS)))

    if stats["assistant_turns"] < 1 or stats["tool_calls"] < 1:
        return None

    for tool, count in seen_calls.items():
        if count > 1:
            stats["repeated_tool_calls"] += count - 1

    session_started_at = parse_epoch_timestamp(session_row["started_at"])
    first_seen = first_ts or session_started_at
    latest_seen = (
        last_ts
        or parse_epoch_timestamp(session_row["last_activity_at"])
        or parse_epoch_timestamp(session_row["ended_at"])
        or first_seen
    )

    if first_seen is not None:
        meta["started_at"] = first_seen.isoformat()
    if latest_seen is not None:
        meta["timestamp"] = latest_seen.isoformat()
    else:
        meta["timestamp"] = datetime.now(tz=timezone.utc).isoformat()
    stats["first_ts"] = first_seen.isoformat() if first_seen is not None else None
    stats["last_ts"] = latest_seen.isoformat() if latest_seen is not None else None
    stats["has_code_edits"] = has_code_edit_hint
    stats["skills"] = sorted(skills_used & set(skill_names))
    return meta, stats, entries.finish(), sorted(skills_used & set(skill_names))


def find_hermes_sessions(databases, cutoff):
    """Return Hermes session rows (with their database) newer than cutoff, newest first."""
    records = []
    scanned = 0
    cutoff_epoch = cutoff.timestamp()
    for database in databases:
        connection = None
        try:
            connection = open_readonly_database(database)
            if not hermes_database_has_sessions(connection):
                continue
            columns = sqlite_table_columns(connection, "sessions")
            if "cwd" not in columns:
                continue
            message_columns = sqlite_table_columns(connection, "messages")
            required_message_columns = {"session_id", "role", "content", "tool_calls", "timestamp"}
            if not required_message_columns.issubset(message_columns):
                print(
                    f"warning: skipping Hermes database {database}: incompatible messages schema",
                    file=sys.stderr,
                )
                continue
            rows = connection.execute(
                """
                SELECT id, source, cwd, title, display_name, parent_session_id,
                       started_at, last_activity_at, ended_at
                FROM sessions
                WHERE COALESCE(last_activity_at, ended_at, started_at) >= ?
                ORDER BY COALESCE(last_activity_at, ended_at, started_at) DESC
                """,
                (cutoff_epoch,),
            ).fetchall()
        except sqlite3.Error as exc:
            print(f"warning: could not read Hermes database {database}: {exc}", file=sys.stderr)
            continue
        finally:
            if connection is not None:
                connection.close()
        scanned += len(rows)
        for row in rows:
            records.append((database, row))
    records.sort(
        key=lambda pair: parse_epoch_timestamp(
            pair[1]["last_activity_at"] or pair[1]["ended_at"] or pair[1]["started_at"]
        ) or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    return records, scanned
