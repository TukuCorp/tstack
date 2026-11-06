# Adapted from warpdotdev/common-skills skill-doctor (MIT, Copyright (c) 2026 Denver Technologies, Inc.)
"""Shared transcript helpers for collect_sessions.py and hermes_sessions.py."""

import json
import re
from collections import deque
from pathlib import Path

MAX_MSG_CHARS = 1500
MAX_TOOL_CHARS = 500
MAX_TRANSCRIPT_ENTRIES = 160
TRANSCRIPT_HEAD = 100
TRANSCRIPT_TAIL = 40

CODE_EDIT_HINTS = ("apply_patch", "*** Begin Patch", "edit_file", "create_file", "str_replace", "write_file")
CLAUDE_CODE_EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit", "Write"}
GENERIC_EDIT_TOOLS = {"edit", "write", "apply_patch", "edit_file", "write_file", "str_replace", "search_replace"}


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


