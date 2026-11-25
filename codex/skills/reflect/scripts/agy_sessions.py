"""Read agy (Antigravity CLI) conversations for collect_sessions.py.

agy keeps one SQLite file per conversation in ~/.gemini/antigravity-cli/conversations/<id>.db.
Each row of `steps` holds a protobuf `step_payload` (no .proto is shipped), decoded here from the
wire format. Field numbers were read off agy 1.5.16 on 2026-11-25:
  payload.1 = step type; payload.5.1.1 = epoch seconds
  type 14  user input:   19.2 text, 19.12.12 workspace file:// URI
  type 15  model turn:   20.1 reply text, 20.3 thinking, 20.7 tool calls (1 id, 2 name, 3 JSON args)
  type 132 tool result:  longest text leaf
  type 101 notification: 114.1 text
history.jsonl maps conversationId -> workspace as a fallback for the working directory.
"""

import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

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

USER, MODEL, TOOL_RESULT, NOTICE = 14, 15, 132, 101
EDIT_TOOLS = {"write_file", "edit_file"}
OSC_PREFIX = re.compile(r"^(?:\x1b?\]\d+;[^\x07\x1b]*?(?=[A-Z/]|$))+")  # herdr's terminal colour reply


def default_agy_home():
    return Path.home() / ".gemini" / "antigravity-cli"


def _varint(b, i):
    result = shift = 0
    while True:
        c = b[i]
        i += 1
        result |= (c & 0x7F) << shift
        shift += 7
        if c < 0x80:
            return result, i


def decode_message(b):
    """Wire-decode one protobuf message to [(field, wiretype, value)], or None if b is not one."""
    out, i = [], 0
    try:
        while i < len(b):
            key, i = _varint(b, i)
            field, wt = key >> 3, key & 7
            if field == 0:
                return None
            if wt == 0:
                v, i = _varint(b, i)
            elif wt == 1:
                v, i = b[i:i + 8], i + 8
            elif wt == 5:
                v, i = b[i:i + 4], i + 4
            elif wt == 2:
                n, i = _varint(b, i)
                v, i = b[i:i + n], i + n
            else:
                return None
            if i > len(b):
                return None
            out.append((field, wt, v))
        return out
    except IndexError:
        return None


def _text(b):
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    printable = sum(ch.isprintable() or ch in "\n\r\t" for ch in t)
    return t if t and printable >= 0.95 * len(t) else None


def get(b, *path):
    """Values at a field path (bytes for length-delimited, int for varints); repeated fields fan out."""
    level = [b]
    for depth, field in enumerate(path):
        nxt = []
        for blob in level:
            msg = decode_message(blob) if isinstance(blob, (bytes, bytearray)) else None
            for f, wt, v in msg or []:
                if f == field and (wt == 2 or depth == len(path) - 1):
                    nxt.append(v)
        level = nxt
    return level


def get_text(b, *path):
    for v in get(b, *path):
        if isinstance(v, (bytes, bytearray)):
            t = _text(v)
            if t:
                return t
    return ""


def longest_text(b, depth=0, skip=(5,)):
    """Longest readable string anywhere in the payload, ignoring metadata field 5 at the top."""
    best = ""
    msg = decode_message(b) if depth < 8 else None
    if msg is None:
        return _text(b) or ""
    for f, wt, v in msg:
        if wt != 2 or (depth == 0 and f in skip):
            continue
        cand = longest_text(v, depth + 1)
        if len(cand) > len(best):
            best = cand
    return best


def step_time(payload):
    secs = get(payload, 5, 1, 1)
    if secs and isinstance(secs[0], int):
        try:
            return datetime.fromtimestamp(secs[0], tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    return None


def clean_user_text(text):
    return OSC_PREFIX.sub("", text).strip()


def uri_to_path(uri):
    if not uri.startswith("file:"):
        return uri or None
    path = unquote(urlparse(uri).path)
    return path[1:] if re.match(r"^/[A-Za-z]:", path) else path


def load_history_workspaces(home):
    """conversationId -> workspace from history.jsonl (agy's prompt log)."""
    out = {}
    path = Path(home) / "history.jsonl"
    try:
        with path.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if rec.get("conversationId") and rec.get("workspace"):
                    out[rec["conversationId"]] = rec["workspace"]
    except OSError:
        pass
    return out


def find_agy_sessions(home, cutoff):
    """Conversation databases modified since cutoff, newest first; returns (paths, scanned)."""
    folder = Path(home) / "conversations"
    if not folder.is_dir():
        return [], 0
    cutoff_epoch = cutoff.timestamp()
    dbs = [p for p in folder.glob("*.db") if p.stat().st_mtime >= cutoff_epoch]
    dbs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return dbs, len(dbs)


def parse_agy_session(db_path, skill_names, workspaces):
    """Normalize one agy conversation to (meta, stats, entries, skills_used), or None if empty."""
    try:
        con = sqlite3.connect(f"{Path(db_path).as_uri()}?mode=ro", uri=True, timeout=2)
        rows = con.execute("SELECT step_type, step_payload FROM steps ORDER BY idx").fetchall()
        con.close()
    except sqlite3.Error as exc:
        print(f"warning: could not read agy conversation {db_path}: {exc}", file=sys.stderr)
        return None
    cid = Path(db_path).stem
    skill_set = set(skill_names)
    stats = {"user_turns": 0, "assistant_turns": 0, "tool_calls": 0, "repeated_tool_calls": 0, "error_outputs": 0}
    entries = TranscriptBuffer()
    seen_calls, skills_used = {}, set()
    cwd, has_edit, first_ts, last_ts = None, False, None, None

    for step_type, payload in rows:
        payload = payload or b""
        ts = step_time(payload)
        if ts is not None:
            first_ts = first_ts or ts
            last_ts = ts
        if step_type == USER:
            text = clean_user_text(get_text(payload, 19, 2))
            cwd = cwd or uri_to_path(get_text(payload, 19, 12, 12))
            if text and not looks_injected(text):
                stats["user_turns"] += 1
                skills_used |= detect_skill_candidates(text) & skill_set
                entries.append(("user", truncate(text, MAX_MSG_CHARS)))
        elif step_type == MODEL:
            stats["assistant_turns"] += 1
            reply = get_text(payload, 20, 1)
            if reply:
                skills_used |= detect_skill_candidates(reply) & skill_set
                entries.append(("assistant", truncate(reply, MAX_MSG_CHARS)))
            for call in get(payload, 20, 7):
                name = get_text(call, 2) or "unknown"
                args = get_text(call, 3)
                stats["tool_calls"] += 1
                if name in EDIT_TOOLS or name in GENERIC_EDIT_TOOLS or name in CODE_EDIT_HINTS:
                    has_edit = True
                key = hashlib.sha1((name + args).encode()).hexdigest()
                seen_calls[key] = seen_calls.get(key, 0) + 1
                skills_used |= detect_skill_candidates(args) & skill_set
                entries.append((f"tool:{name}", truncate(args, MAX_TOOL_CHARS)))
        elif step_type in (TOOL_RESULT, NOTICE):
            text = get_text(payload, 114, 1) if step_type == NOTICE else longest_text(payload)
            if text:
                low = text[:300].lower()
                if "error" in low or "traceback" in low or "denied" in low:
                    stats["error_outputs"] += 1
                entries.append(("tool_output", truncate(text, MAX_TOOL_CHARS)))

    if stats["assistant_turns"] < 1 or stats["tool_calls"] < 1:
        return None
    stats["repeated_tool_calls"] = sum(n - 1 for n in seen_calls.values() if n > 1)
    if last_ts is None:
        last_ts = datetime.fromtimestamp(Path(db_path).stat().st_mtime, tz=timezone.utc)
    first_ts = first_ts or last_ts
    meta = {"id": cid, "source": "agy", "cwd": cwd or workspaces.get(cid),
            "started_at": first_ts.isoformat(), "timestamp": last_ts.isoformat()}
    stats.update(first_ts=first_ts.isoformat(), last_ts=last_ts.isoformat(), has_code_edits=has_edit,
                 skills=sorted(skills_used))
    return meta, stats, entries.finish(), sorted(skills_used)
