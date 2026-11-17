"""PreToolUse guard (Bash, PowerShell): block long inline interpreter scripts.

CLAUDE.md "Shell on Windows" says to write any script longer than a few lines to a scratch file and run it.
/reflect (2026-11-08..18) found the rule ignored in 11+ sessions, with heredoc and -c scripts breaking on quotes.
Exit 2 sends the reason back to the model and the call does not run.
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
        return 0
    if data.get("tool_name") not in ("Bash", "PowerShell"):
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    if cmd.count("\n") + 1 <= MAX_LINES or not any(p.search(cmd) for p in INLINE):
        return 0
    sys.stderr.write(
        f"Blocked: inline interpreter script over {MAX_LINES} lines. Per CLAUDE.md (Shell on Windows), write it to a "
        "scratch file with the Write tool and run that file (python -X utf8 C:/.../script.py).\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
