"""Integration tests for inline-script-guard.py: feed real hook payloads on stdin, check the exit code.

Run: python -X utf8 -m pytest C:/Users/<USER>/.claude/hooks/test_inline_script_guard.py
"""
import json
import subprocess
import sys
from pathlib import Path

GUARD = Path(__file__).with_name("inline-script-guard.py")
BODY = "\n".join(f"x{i} = {i}" for i in range(12))


def run(tool, command):
    payload = {"tool_name": tool, "tool_input": {"command": command}}
    return subprocess.run([sys.executable, "-X", "utf8", str(GUARD)], input=json.dumps(payload),
                          capture_output=True, text=True, timeout=30)


def test_blocks_long_python_heredoc():
    r = run("Bash", f"python -X utf8 - <<'EOF'\n{BODY}\nEOF")
    assert r.returncode == 2 and "scratch file" in r.stderr


def test_blocks_long_python_dash_c():
    r = run("Bash", f'python -X utf8 -c "\n{BODY}\n"')
    assert r.returncode == 2


def test_blocks_long_powershell_herestring_piped_to_python():
    r = run("PowerShell", f"@'\n{BODY}\n'@ | python -X utf8 -")
    assert r.returncode == 2


def test_allows_short_heredoc():
    assert run("Bash", "python - <<'EOF'\nprint(1)\nprint(2)\nEOF").returncode == 0


def test_allows_running_a_script_file():
    assert run("Bash", "python -X utf8 C:/tmp/build.py --flag").returncode == 0


def test_allows_long_heredoc_into_a_file_or_git():
    assert run("Bash", f"cat >> notes.md <<'EOF'\n{BODY}\nEOF").returncode == 0
    assert run("Bash", f"git commit -m \"$(cat <<'EOF'\n{BODY}\nEOF\n)\"").returncode == 0


def test_ignores_other_tools_and_bad_input():
    assert run("Read", f"python -c '\n{BODY}'").returncode == 0
    r = subprocess.run([sys.executable, str(GUARD)], input="not json", capture_output=True, text=True)
    assert r.returncode == 0
