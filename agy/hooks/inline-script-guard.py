"""agy PreToolUse guard (run_command): block long inline interpreter scripts.

GEMINI.md "Shell on Windows" says to write any script longer than a few lines with write_file and run the file.
/reflect 2026-11-25 found agy inlining multi-line python -c scripts; Claude Code and Codex have the same guard.
agy contract: JSON on stdin (toolCall.args.CommandLine); stdout {"decision": "deny", "reason": ...} blocks the call.
"""
import json
import re
import sys

MAX_LINES = 8  # "a few lines": short one-off snippets stay allowed
INTERP = r"\b(?:python3?|py|node)(?:\.exe)?\b"
INLINE = [
    re.compile(INTERP + r"[^\n|;&]*<<-?\s*['\"]?\w+"),        # python - <<'EOF'
    re.compile(INTERP + r"[^\n|;&]*\s-[ce]\s"),               # python -c "...", node -e "..."
    re.compile(r"['\"]@\s*\|\s*(?:&\s*)?" + INTERP),           # @' ... '@ | python -
]


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        data = {}
    call = data.get("toolCall") or {}
    cmd = (call.get("args") or {}).get("CommandLine") or ""
    if not isinstance(cmd, str) or cmd.count("\n") + 1 <= MAX_LINES or not any(p.search(cmd) for p in INLINE):
        return 0  # no output = no decision; agy reads "{}" as deny
    print(json.dumps({"decision": "deny", "reason": (
        f"Blocked: inline interpreter script over {MAX_LINES} lines. Per GEMINI.md (Shell on Windows), write it to a "
        "scratch file with write_file and run that file (python -X utf8 C:/.../script.py).")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
