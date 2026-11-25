"""Codex PreToolUse guard (shell): block long inline interpreter scripts.

AGENTS.md "Shell on Windows" says to write any script longer than a few lines with apply_patch and run the file.
/reflect 2026-11-25 found 4 Codex sessions losing calls to inline node/python quoting and backticks.
A JSON permissionDecision "deny" on stdout blocks the call and sends the reason to the model.
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


def command_of(data):
    inp = data.get("tool_input") or {}
    cmd = inp.get("command") if isinstance(inp, dict) else inp
    if isinstance(cmd, list):  # argv form, e.g. ["powershell.exe", "-Command", "..."]
        cmd = " ".join(str(c) for c in cmd)
    return cmd if isinstance(cmd, str) else ""


def main():
    try:
        data = json.load(sys.stdin)
    except (ValueError, OSError):
        return 0
    cmd = command_of(data)
    if cmd.count("\n") + 1 <= MAX_LINES or not any(p.search(cmd) for p in INLINE):
        return 0
    reason = (
        f"Blocked: inline interpreter script over {MAX_LINES} lines. Per AGENTS.md (Shell on Windows), write it to a "
        "scratch file with apply_patch (*** Add File: <path>, every line prefixed +) and run that file "
        "(python -X utf8 C:/.../script.py).")
    # Codex 0.167 treats exit 2 as a hook failure and runs the call anyway; only a JSON deny blocks it.
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
