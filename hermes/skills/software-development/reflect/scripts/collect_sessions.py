#!/usr/bin/env python3
# Adapted from warpdotdev/common-skills skill-doctor (MIT, Copyright (c) 2026 Denver Technologies, Inc.)
"""Collect local Claude Code, Codex, and Hermes sessions and skills for reflection.

Scans Claude Code project history, Codex rollout files, and/or Hermes Agent's
state.db, discovers installed skills (de-duplicated across mirrored copies),
detects which sessions used which skills, and emits:

  <out>/inventory.json        - skills, per-session stats, sampling decisions
  <out>/transcripts/<id>.md   - condensed transcripts for sampled sessions

Everything runs locally; nothing is uploaded. Python 3.9+, stdlib only.
"""

import argparse
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from collections import deque
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_MSG_CHARS = 1500
MAX_TOOL_CHARS = 500
MAX_TRANSCRIPT_ENTRIES = 160
TRANSCRIPT_HEAD = 100
TRANSCRIPT_TAIL = 40

CODE_EDIT_HINTS = ("apply_patch", "*** Begin Patch", "edit_file", "create_file", "str_replace", "write_file")
CLAUDE_CODE_EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit", "Write"}
GENERIC_EDIT_TOOLS = {"edit", "write", "apply_patch", "edit_file", "write_file", "str_replace", "search_replace"}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--harness",
        choices=("auto", "all", "claude", "codex", "hermes"),
        default="auto",
        help="session source (default: auto; scans every locally available source)",
    )
    p.add_argument(
        "--claude-home",
        default=os.environ.get("CLAUDE_CONFIG_DIR", "~/.claude"),
        help="Claude Code config directory (default: CLAUDE_CONFIG_DIR or ~/.claude)",
    )
    p.add_argument("--codex-home", default=os.environ.get("CODEX_HOME", "~/.codex"))
    p.add_argument(
        "--hermes-home",
        default=None,
        help="Hermes Agent home containing state.db "
             "(default: HERMES_HOME, %%LOCALAPPDATA%%/hermes, ~/.hermes, then ~)",
    )
    p.add_argument(
        "--repo",
        action="append",
        default=[],
        help="project to include (repeatable; default: git root of cwd, else cwd)",
    )
    p.add_argument(
        "--all-conversations",
        action="store_true",
        help="score conversations from every project represented in local history",
    )
    p.add_argument("--include-global-skills", action="store_true",
                   help="also discover skills outside the repo (~/.claude/skills, ~/.agents/skills, ~/.codex/skills, ~/.config/opencode/skills, Hermes home/skills)")
    p.add_argument("--days", type=int, default=45, help="only consider sessions modified in the last N days")
    p.add_argument("--max-sessions", type=int, default=12, help="max sessions to sample for scoring")
    p.add_argument("--per-skill", type=int, default=3, help="max sampled sessions per skill")
    p.add_argument("--no-skill", type=int, default=4, help="max sampled sessions that used no skill")
    p.add_argument("--skills-dir", action="append", default=[], help="extra skills directory to scan (repeatable)")
    p.add_argument("--include-subagents", action="store_true", help="include subagent/child sessions")
    p.add_argument("--out", default="./reflect-report")
    return p.parse_args()


def resolve_repo(repo_arg) -> Path:
    if repo_arg:
        return Path(repo_arg).expanduser().resolve()
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=10
        )
        if res.returncode == 0 and res.stdout.strip():
            return Path(res.stdout.strip()).resolve()
    except (subprocess.TimeoutExpired, OSError):
        pass
    return Path.cwd().resolve()


def resolve_repos(repo_args):
    if not repo_args:
        return [resolve_repo(None)]
    repos = []
    seen = set()
    for value in repo_args:
        repo = resolve_repo(value)
        if repo in seen:
            continue
        seen.add(repo)
        repos.append(repo)
    return repos


def claude_project_slug(path) -> str:
    """Claude Code's project directory name for a path: every non-alphanumeric becomes '-'.

    C:\\Users\\me\\repo -> C--Users-me-repo, /home/me/repo -> -home-me-repo.
    """
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def claude_file_matches_repos(path: Path, claude_home: Path, repos) -> bool:
    """True when a Claude session file sits in a project directory named for one of the repos.

    Fallback for records that carry no cwd. Subagent files live one level deeper
    (projects/<slug>/<session>/subagents/*.jsonl), so compare the first path part.
    """
    try:
        slug = path.relative_to(claude_home / "projects").parts[0]
    except (ValueError, IndexError):
        return False
    return any(slug == claude_project_slug(repo) for repo in repos)


def iter_skill_files(root: Path, nested: bool):
    """Yield SKILL.md paths under a skills root.

    Flat roots hold <skill>/SKILL.md. Nested roots (Hermes) group skills in
    category directories (<category>/<skill>/SKILL.md, sometimes deeper) and keep
    dot-directories such as .archive and .hub, which are skipped.
    """
    if not nested:
        yield from sorted(root.glob("*/SKILL.md"))
        return

    def walk(directory: Path, depth: int):
        try:
            children = sorted(directory.iterdir())
        except OSError:
            return
        for child in children:
            if child.name.startswith(".") or not child.is_dir():
                continue
            skill_md = child / "SKILL.md"
            if skill_md.is_file():
                yield skill_md
            elif depth < 3:
                yield from walk(child, depth + 1)

    yield from walk(root, 1)


def discover_skills(repos, codex_home: Path, extra_dirs, include_global: bool,
                    hermes_home: Path = None, claude_home: Path = None):
    """Find installed skills. Same name+content in several dirs counts once.

    Each skill records every path it was found at (`paths`) and the source labels
    of those dirs (`sources`). A same-named skill with different content is not
    merged: the first one found wins and the others are listed in `shadowed_paths`.
    """
    if isinstance(repos, Path):
        repos = [repos]
    roots = []  # (source label, directory, nested layout)
    for repo in repos:
        roots.extend((
            ("project", repo / ".agents" / "skills", False),
            ("project", repo / ".claude" / "skills", False),
            ("project", repo / ".codex" / "skills", False),
            ("project", repo / ".opencode" / "skills", False),
        ))
    if include_global:
        home = Path.home()
        roots += [
            ("claude", (claude_home or home / ".claude") / "skills", False),
            ("agents", home / ".agents" / "skills", False),
            ("codex", codex_home / "skills", False),
            ("opencode", home / ".config" / "opencode" / "skills", False),
        ]
        if hermes_home is not None:
            roots.append(("hermes", Path(hermes_home) / "skills", True))
    roots += [("extra", Path(d).expanduser(), False) for d in extra_dirs]

    skills = {}
    digests = {}
    for source, root, nested in roots:
        if not root.is_dir():
            continue
        for skill_md in iter_skill_files(root, nested):
            name = skill_md.parent.name
            try:
                text = skill_md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            # Normalize line endings so a CRLF mirror of the same skill still matches.
            digest = hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()
            existing = skills.get(name)
            if existing is not None:
                if digests[name] != digest:
                    existing.setdefault("shadowed_paths", []).append(str(skill_md))
                    continue
                if str(skill_md) not in existing["paths"]:
                    existing["paths"].append(str(skill_md))
                if source not in existing["sources"]:
                    existing["sources"].append(source)
                continue
            desc = ""
            m = re.search(r"^description:\s*(.+)$", text, re.MULTILINE)
            if m:
                desc = m.group(1).strip().strip("\"'")[:300]
            digests[name] = digest
            skills[name] = {
                "name": name,
                "path": str(skill_md),
                "paths": [str(skill_md)],
                "source": source,
                "sources": [source],
                "description": desc,
                "bytes": skill_md.stat().st_size,
                "modified_at": datetime.fromtimestamp(skill_md.stat().st_mtime, tz=timezone.utc).isoformat(),
            }
    return skills


def find_codex_session_files(codex_home: Path, cutoff: datetime):
    files = []
    for sub in ("sessions", "archived_sessions"):
        root = codex_home / sub
        if not root.is_dir():
            continue
        for f in root.rglob("rollout-*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            except OSError:
                continue
            if mtime >= cutoff:
                files.append((mtime, f))
    files.sort(key=lambda t: t[0], reverse=True)
    return files


def find_claude_session_files(claude_home: Path, cutoff: datetime, include_subagents: bool):
    """Find recent Claude Code parent sessions and, optionally, sidechains."""
    projects = claude_home / "projects"
    if not projects.is_dir():
        return []

    candidates = list(projects.glob("*/*.jsonl"))
    if include_subagents:
        candidates.extend(projects.glob("*/*/subagents/*.jsonl"))

    files = []
    for path in candidates:
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        except OSError:
            continue
        if mtime >= cutoff:
            files.append((mtime, path))
    files.sort(key=lambda item: item[0], reverse=True)
    return files


def truncate(text: str, limit: int) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f" …[truncated {len(text) - limit} chars]"


def extract_text(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                t = block.get("text") or block.get("content") or ""
                if isinstance(t, str) and t:
                    parts.append(t)
            elif isinstance(block, str):
                parts.append(block)
    return "\n".join(parts)


def iter_jsonl_records(path: Path):
    """Yield every valid JSON object without loading the whole file."""
    stream = path.open("r", encoding="utf-8", errors="replace")

    def records():
        with stream:
            for line in stream:
                try:
                    yield json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue

    return records()


class TranscriptBuffer:
    """Keep complete short transcripts and a bounded head/tail for long ones."""

    def __init__(self):
        self._entries = []
        self._tail = None
        self._total = 0

    def append(self, entry):
        self._total += 1
        if self._tail is None:
            self._entries.append(entry)
            if len(self._entries) > MAX_TRANSCRIPT_ENTRIES:
                self._tail = deque(self._entries[-TRANSCRIPT_TAIL:], maxlen=TRANSCRIPT_TAIL)
                self._entries = self._entries[:TRANSCRIPT_HEAD]
        else:
            self._tail.append(entry)

    def finish(self):
        if self._tail is None:
            return self._entries
        omitted = self._total - TRANSCRIPT_HEAD - TRANSCRIPT_TAIL
        return self._entries + [
            ("note", f"[... {omitted} entries omitted ...]")
        ] + list(self._tail)


def detect_skill_candidates(text: str):
    """Extract possible installed-skill names from one tool argument payload."""
    normalized = text.replace("\\", "/")
    candidates = set(re.findall(r"(?:^|/)skills/+([^/]+)/+", normalized))
    candidates.update(re.findall(
        r'"(?:skill|name|bundled_skill_id)"\s*:\s*"([^"]+)"',
        normalized,
    ))
    return candidates


def parse_claude_session(path: Path, skill_names, include_subagents: bool):
    """Normalize one Claude Code JSONL session to the shared transcript shape."""
    try:
        records = iter_jsonl_records(path)
    except OSError:
        return None

    meta = {}
    stats = {
        "user_turns": 0,
        "assistant_turns": 0,
        "tool_calls": 0,
        "repeated_tool_calls": 0,
        "error_outputs": 0,
    }
    entries = TranscriptBuffer()
    seen_calls = {}
    seen_assistant_messages = set()
    used_tool_names = set()
    skills_used = set()
    has_code_edit_hint = False
    first_ts = last_ts = None
    is_sidechain = False

    for obj in records:
        ts = obj.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts

        if obj.get("isSidechain"):
            is_sidechain = True
            if not include_subagents:
                return None

        if not meta and obj.get("sessionId"):
            session_id = obj.get("sessionId")
            agent_id = obj.get("agentId")
            meta = {
                "id": f"{session_id}-{agent_id}" if agent_id else session_id,
                "cwd": obj.get("cwd"),
                "started_at": ts,
                "originator": "claude-code",
                "thread_source": "subagent" if obj.get("isSidechain") else None,
                "cli_version": obj.get("version"),
                "entrypoint": obj.get("entrypoint"),
            }
        elif meta:
            meta["cwd"] = meta.get("cwd") or obj.get("cwd")
            meta["started_at"] = meta.get("started_at") or ts
            meta["cli_version"] = meta.get("cli_version") or obj.get("version")
            meta["entrypoint"] = meta.get("entrypoint") or obj.get("entrypoint")
            agent_id = obj.get("agentId")
            if agent_id and not meta["id"].endswith(f"-{agent_id}"):
                meta["id"] = f"{obj.get('sessionId') or meta['id']}-{agent_id}"

        record_type = obj.get("type")
        message = obj.get("message")
        if record_type not in ("user", "assistant") or not isinstance(message, dict):
            continue

        role = message.get("role") or record_type
        content = message.get("content")
        blocks = content if isinstance(content, list) else [{"type": "text", "text": content}]
        has_user_text = False

        if role == "assistant":
            message_id = message.get("id") or obj.get("uuid")
            if message_id and message_id not in seen_assistant_messages:
                seen_assistant_messages.add(message_id)
                stats["assistant_turns"] += 1

        for block in blocks:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                text = block.get("text")
                if not isinstance(text, str) or not text or looks_injected(text):
                    continue
                if role == "user":
                    has_user_text = True
                    entries.append(("user", truncate(text, MAX_MSG_CHARS)))
                elif role == "assistant":
                    entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
            elif block_type == "tool_use":
                stats["tool_calls"] += 1
                name = str(block.get("name") or "unknown")
                args = block.get("input") or {}
                args_text = args if isinstance(args, str) else json.dumps(args, ensure_ascii=False)
                key = hashlib.sha1((name + args_text).encode()).hexdigest()
                seen_calls[key] = seen_calls.get(key, 0) + 1
                if seen_calls[key] > 1:
                    stats["repeated_tool_calls"] += 1
                used_tool_names.add(name)
                skills_used.update(detect_skill_candidates(args_text))
                has_code_edit_hint = has_code_edit_hint or any(
                    hint in args_text for hint in CODE_EDIT_HINTS
                )
                if name == "Skill" and isinstance(args, dict):
                    skill_name = args.get("skill")
                    if skill_name:
                        skills_used.add(skill_name)
                entries.append((f"tool:{name}", truncate(args_text, MAX_TOOL_CHARS)))
            elif block_type == "tool_result":
                result = extract_text(block.get("content"))
                low = result[:2000].lower()
                if block.get("is_error") or "error" in low or "failed" in low or "traceback" in low:
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(result, MAX_TOOL_CHARS)))

        if role == "user" and has_user_text:
            stats["user_turns"] += 1

    if not meta:
        meta = {
            "id": path.stem,
            "cwd": None,
            "started_at": first_ts,
            "originator": "claude-code",
            "thread_source": "subagent" if is_sidechain else None,
        }
    elif is_sidechain:
        meta["thread_source"] = "subagent"

    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = (
        bool(used_tool_names & CLAUDE_CODE_EDIT_TOOLS)
        or has_code_edit_hint
    )
    return meta, stats, entries.finish(), sorted(skills_used)


def looks_injected(text: str) -> bool:
    head = text.lstrip()[:80]
    return head.startswith("<") and any(
        tag in head
        for tag in (
            "environment_context", "user_instructions", "ENVIRONMENT", "system-reminder",
            "permissions", "collaboration_mode", "recommended_plugins", "turn_context",
            "user_info",
        )
    )


def parse_codex_session(path: Path, skill_names, include_subagents: bool):
    """Returns (meta, stats, entries) or None if the session should be skipped."""
    try:
        records = iter_jsonl_records(path)
    except OSError:
        return None

    meta = {}
    stats = {"user_turns": 0, "assistant_turns": 0, "tool_calls": 0, "repeated_tool_calls": 0, "error_outputs": 0}
    entries = TranscriptBuffer()
    seen_calls = {}
    skills_used = set()
    message_turns = {"user": 0, "assistant": 0}
    has_code_edits = False
    first_ts = last_ts = None

    for obj in records:
        ltype = obj.get("type")
        payload = obj.get("payload") or {}
        if not isinstance(payload, dict):
            continue
        ts = obj.get("timestamp")
        if ts:
            first_ts = first_ts or ts
            last_ts = ts

        if ltype == "session_meta":
            meta = {
                "id": payload.get("id") or payload.get("session_id") or path.stem,
                "cwd": payload.get("cwd"),
                "started_at": payload.get("timestamp"),
                "originator": payload.get("originator"),
                "thread_source": payload.get("thread_source"),
                "cli_version": payload.get("cli_version"),
            }
            source = payload.get("source")
            is_subagent = payload.get("thread_source") == "subagent" or (
                isinstance(source, dict) and "subagent" in source
            )
            if is_subagent and not include_subagents:
                return None

        elif ltype == "event_msg":
            ptype = payload.get("type")
            if ptype == "user_message":
                stats["user_turns"] += 1
            elif ptype == "agent_message":
                stats["assistant_turns"] += 1

        elif ltype == "response_item":
            ptype = payload.get("type")
            if ptype == "message":
                role = payload.get("role")
                text = extract_text(payload.get("content"))
                if not text:
                    continue
                if role == "user":
                    if looks_injected(text):
                        continue
                    message_turns["user"] += 1
                    entries.append(("user", truncate(text, MAX_MSG_CHARS)))
                elif role == "assistant":
                    message_turns["assistant"] += 1
                    entries.append(("assistant", truncate(text, MAX_MSG_CHARS)))
            elif ptype in ("function_call", "custom_tool_call", "local_shell_call"):
                stats["tool_calls"] += 1
                name = payload.get("name") or ptype
                args = payload.get("arguments") or payload.get("input") or ""
                if not isinstance(args, str):
                    args = json.dumps(args)
                key = hashlib.sha1((name + args).encode()).hexdigest()
                seen_calls[key] = seen_calls.get(key, 0) + 1
                if seen_calls[key] > 1:
                    stats["repeated_tool_calls"] += 1
                skills_used.update(detect_skill_candidates(args))
                has_code_edits = has_code_edits or any(
                    hint in args for hint in CODE_EDIT_HINTS
                )
                entries.append((f"tool:{name}", truncate(args, MAX_TOOL_CHARS)))
            elif ptype in ("function_call_output", "custom_tool_call_output"):
                out = payload.get("output") or ""
                if not isinstance(out, str):
                    out = json.dumps(out)
                low = out[:2000].lower()
                if "error" in low or "failed" in low or "traceback" in low:
                    stats["error_outputs"] += 1
                entries.append(("output", truncate(out, MAX_TOOL_CHARS)))

    if not meta:
        meta = {"id": path.stem, "cwd": None, "started_at": first_ts}

    # Newer rollouts have no user_message/agent_message events; count the messages themselves.
    stats["user_turns"] = stats["user_turns"] or message_turns["user"]
    stats["assistant_turns"] = stats["assistant_turns"] or message_turns["assistant"]

    stats["first_ts"] = first_ts
    stats["last_ts"] = last_ts
    stats["has_code_edits"] = has_code_edits
    return meta, stats, entries.finish(), sorted(skills_used)


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


def safe_filename(value) -> str:
    """Make a session id safe as a Windows filename."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", str(value))


def render_transcript(meta, stats, skills_used, entries) -> str:
    lines = [
        f"# Session {meta.get('id')}",
        f"- cwd: {meta.get('cwd')}",
        f"- started: {meta.get('started_at') or stats.get('first_ts')}",
        f"- skills detected: {', '.join(skills_used) or '(none)'}",
        f"- stats: {stats['user_turns']} user turns, {stats['assistant_turns']} assistant turns, "
        f"{stats['tool_calls']} tool calls ({stats['repeated_tool_calls']} repeated), "
        f"{stats['error_outputs']} error-ish outputs, code edits: {stats['has_code_edits']}",
        "",
        "## Condensed transcript",
        "",
    ]
    shown = entries
    if len(entries) > MAX_TRANSCRIPT_ENTRIES:
        omitted = len(entries) - TRANSCRIPT_HEAD - TRANSCRIPT_TAIL
        shown = entries[:TRANSCRIPT_HEAD] + [("note", f"[... {omitted} entries omitted ...]")] + entries[-TRANSCRIPT_TAIL:]
    for role, text in shown:
        lines.append(f"[{role}] {text}")
        lines.append("")
    return "\n".join(lines)


def session_matches_repo(cwd, repo: Path) -> bool:
    """True when a session's recorded cwd belongs to this repo.

    Two ways to match:
    1. cwd is inside the repo root (same-machine sessions).
    2. cwd's trailing directory name equals the repo's name (git/Codex
       worktrees like ~/.codex/worktrees/<id>/<repo-name>, and sessions
       imported from another machine where the checkout path differs).
    Basename matching can over-match if two different projects share a
    directory name; acceptable for a report, and prefix matching alone
    misses every worktree session.
    """
    if not cwd:
        return False
    p = Path(cwd)
    try:
        if p.resolve().is_relative_to(repo):
            return True
    except OSError:
        pass  # cwd from another machine may not exist locally
    return p.name == repo.name or repo.name in p.parts


def session_matches_repos(cwd, repos) -> bool:
    return any(session_matches_repo(cwd, repo) for repo in repos)


def infer_session_repos(sessions):
    repos = []
    seen = set()
    for session in sessions:
        cwd = session["meta"].get("cwd")
        if not cwd:
            continue
        path = Path(cwd).expanduser()
        if not path.is_dir():
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (subprocess.TimeoutExpired, OSError):
            continue
        if result.returncode != 0 or not result.stdout.strip():
            continue
        repo = Path(result.stdout.strip()).resolve()
        if repo in seen:
            continue
        seen.add(repo)
        repos.append(repo)
    return repos


def detect_skills_from_entries(entries, skill_names):
    tool_text = "\n".join(
        text
        for role, text in entries
        if role == "skill" or role.startswith("tool:")
    ).replace("\\", "/")
    detected = set()
    for name in skill_names:
        markers = (
            f"skills/{name}/",
            f"{name}/SKILL.md",
            f'"skill": "{name}"',
            f'"name": "{name}"',
            f'"bundled_skill_id": "{name}"',
        )
        if any(marker in tool_text for marker in markers):
            detected.add(name)
    return detected


def main():
    # Piped output on Windows defaults to a legacy codepage; print UTF-8 and never crash on a non-ASCII path.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    if args.all_conversations and args.repo:
        print(
            "error: --all-conversations cannot be combined with --repo",
            file=sys.stderr,
        )
        sys.exit(2)
    claude_home = Path(args.claude_home).expanduser()
    codex_home = Path(args.codex_home).expanduser()
    hermes_home = resolve_hermes_home(args.hermes_home)
    out_dir = Path(args.out).expanduser()
    transcripts_dir = out_dir / "transcripts"
    transcripts_dir.mkdir(parents=True, exist_ok=True)

    repos = [] if args.all_conversations else resolve_repos(args.repo)
    skills = discover_skills(
        repos,
        codex_home,
        args.skills_dir,
        args.include_global_skills,
        hermes_home=hermes_home,
        claude_home=claude_home,
    )
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    sessions = []
    in_scope_count = 0
    scanned_count = 0
    sources = {}

    requested_claude = args.harness in ("auto", "all", "claude")
    if requested_claude and (claude_home / "projects").is_dir():
        claude_files = find_claude_session_files(
            claude_home,
            cutoff,
            args.include_subagents,
        )
        sources["claude"] = {
            "home": str(claude_home),
            "records_in_window": len(claude_files),
        }
        scanned_count += len(claude_files)
        for mtime, path in claude_files:
            parsed = parse_claude_session(path, skills.keys(), args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            if not args.all_conversations and not (
                session_matches_repos(meta.get("cwd"), repos)
                or claude_file_matches_repos(path, claude_home, repos)
            ):
                continue
            in_scope_count += 1
            if stats["assistant_turns"] < 1 or stats["tool_calls"] < 1:
                continue
            sessions.append({
                "harness": "claude",
                "meta": meta,
                "stats": stats,
                "skills_used": skills_used,
                "file": str(path),
                "modified_at": mtime.isoformat(),
                "_entries": entries,
            })
    elif args.harness == "claude":
        print(
            f"error: Claude Code project history not found at {claude_home / 'projects'}",
            file=sys.stderr,
        )
        sys.exit(1)

    requested_codex = args.harness in ("auto", "all", "codex")
    if requested_codex and codex_home.is_dir():
        codex_files = find_codex_session_files(codex_home, cutoff)
        sources["codex"] = {"home": str(codex_home), "records_in_window": len(codex_files)}
        scanned_count += len(codex_files)
        for mtime, path in codex_files:
            parsed = parse_codex_session(path, skills.keys(), args.include_subagents)
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            if not args.all_conversations and not session_matches_repos(
                meta.get("cwd"),
                repos,
            ):
                continue
            in_scope_count += 1
            if stats["assistant_turns"] < 1 or stats["tool_calls"] < 1:
                continue
            sessions.append({
                "harness": "codex",
                "meta": meta,
                "stats": stats,
                "skills_used": skills_used,
                "file": str(path),
                "modified_at": mtime.isoformat(),
                "_entries": entries,
            })
    elif args.harness == "codex":
        print(f"error: Codex home not found at {codex_home}", file=sys.stderr)
        sys.exit(1)

    requested_hermes = args.harness in ("auto", "all", "hermes")
    hermes_databases = discover_hermes_databases(args.hermes_home) if requested_hermes else []
    if hermes_databases:
        hermes_records, hermes_scanned = find_hermes_sessions(hermes_databases, cutoff)
        sources["hermes"] = {
            "home": str(hermes_databases[0].parent),
            "records_in_window": len(hermes_records),
        }
        scanned_count += hermes_scanned
        for database, row in hermes_records:
            connection = open_readonly_database(database)
            try:
                parsed = parse_hermes_session(connection, row, skills.keys(), args.include_subagents)
            finally:
                connection.close()
            if parsed is None:
                continue
            meta, stats, entries, skills_used = parsed
            if not args.all_conversations and not session_matches_repos(
                meta.get("cwd"),
                repos,
            ):
                continue
            in_scope_count += 1
            if stats["assistant_turns"] < 1 or stats["tool_calls"] < 1:
                continue
            sessions.append({
                "harness": "hermes",
                "meta": meta,
                "stats": stats,
                "skills_used": skills_used,
                "file": str(database),
                "modified_at": meta["timestamp"],
                "_entries": entries,
            })
    elif args.harness == "hermes":
        print(
            f"error: Hermes state.db not found (looked in {args.hermes_home or 'HERMES_HOME, %LOCALAPPDATA%/hermes, ~/.hermes, ~'})",
            file=sys.stderr,
        )
        sys.exit(1)

    if not sources:
        print(
            "error: no supported session source found (Claude Code, Codex, or Hermes)",
            file=sys.stderr,
        )
        sys.exit(1)
    if args.all_conversations:
        repos = infer_session_repos(sessions)
        skills = discover_skills(
            repos,
            codex_home,
            args.skills_dir,
            args.include_global_skills,
            hermes_home=hermes_home,
            claude_home=claude_home,
        )
    installed_skill_names = set(skills)
    for session in sessions:
        detected = detect_skills_from_entries(
            session["_entries"],
            installed_skill_names,
        )
        session["skills_used"] = sorted(
            (set(session["skills_used"]) | detected) & installed_skill_names
        )

    sessions.sort(key=lambda session: session["modified_at"], reverse=True)
    for session in sessions:
        session["_key"] = f"{session['harness']}:{session['meta']['id']}"

    # Sample: newest-first, up to per-skill sessions per skill, then no-skill sessions.
    sampled_keys = set()
    per_skill_count = {name: 0 for name in skills}
    for s in sessions:
        if len(sampled_keys) >= args.max_sessions:
            break
        for name in s["skills_used"]:
            if per_skill_count.get(name, 0) < args.per_skill:
                per_skill_count[name] = per_skill_count.get(name, 0) + 1
                sampled_keys.add(s["_key"])
                break
    no_skill_taken = 0
    for s in sessions:
        if len(sampled_keys) >= args.max_sessions or no_skill_taken >= args.no_skill:
            break
        if not s["skills_used"] and s["_key"] not in sampled_keys:
            sampled_keys.add(s["_key"])
            no_skill_taken += 1

    for s in sessions:
        sid = s["meta"]["id"]
        s["sampled"] = s["_key"] in sampled_keys
        if s["sampled"]:
            tpath = transcripts_dir / f"{s['harness']}-{safe_filename(sid)}.md"
            tpath.write_text(
                render_transcript(s["meta"], s["stats"], s["skills_used"], s["_entries"]),
                encoding="utf-8",
            )
            s["transcript_path"] = str(tpath)
        del s["_entries"]
        del s["_key"]

    skill_usage = {name: 0 for name in skills}
    for s in sessions:
        for name in s["skills_used"]:
            skill_usage[name] += 1

    if args.all_conversations:
        conversation_scope = "all"
        scope_name = "all-conversations"
    elif len(repos) == 1:
        conversation_scope = "projects"
        scope_name = repos[0].name
    else:
        conversation_scope = "projects"
        scope_name = "multiple-projects"

    inventory = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "harness": next(iter(sources)) if len(sources) == 1 else "mixed",
        "sources": sources,
        "claude_home": str(claude_home) if "claude" in sources else None,
        "codex_home": str(codex_home) if "codex" in sources else None,
        "hermes_home": str(hermes_home) if "hermes" in sources else None,
        "conversation_scope": conversation_scope,
        "repo": str(repos[0]) if len(repos) == 1 else None,
        "repos": [str(repo) for repo in repos],
        "repo_name": scope_name,
        "repo_names": [repo.name for repo in repos],
        "window_days": args.days,
        "skills": sorted(skills.values(), key=lambda x: x["name"]),
        "skill_usage": skill_usage,
        "stats": {
            "session_files_in_window": scanned_count,
            "session_records_in_window": scanned_count,
            "sessions_in_repo": in_scope_count,
            "sessions_in_scope": in_scope_count,
            "sessions_considered": len(sessions),
            "sessions_sampled": len(sampled_keys),
            "skills_found": len(skills),
            "skills_used": sum(1 for v in skill_usage.values() if v > 0),
        },
        "sessions": sessions,
    }
    (out_dir / "inventory.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    st = inventory["stats"]
    print(
        "scope:             "
        + (
            "all conversations"
            if args.all_conversations
            else ", ".join(str(repo) for repo in repos)
        )
    )
    print(f"sources:           {', '.join(sources)}")
    print(f"skills found:      {st['skills_found']} ({st['skills_used']} used in window)")
    print(f"sessions in window: {st['session_records_in_window']} records, {st['sessions_in_scope']} in scope, {st['sessions_considered']} scoreable")
    print(f"sessions sampled:  {st['sessions_sampled']} -> {transcripts_dir}")
    print(f"inventory:         {out_dir / 'inventory.json'}")


if __name__ == "__main__":
    main()
