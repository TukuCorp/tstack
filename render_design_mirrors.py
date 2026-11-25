"""Copy ~/.claude/skills/design to the other four harnesses, swapping only the '## This harness' block."""
import re
import shutil
from pathlib import Path

H = Path.home()
SRC = H / ".claude/skills/design"
PS = ("- The shell is Windows PowerShell 5.1: launch headless models with "
      "`Start-Process -NoNewWindow -RedirectStandardOutput <log> -RedirectStandardError <log>.err`, "
      "never `&&` or `2>&1` on native programs.\n")
WAIT = ("- Local picker sends: you have no persistent monitor, so run `design.py serve <run> --detach` once, "
        "then `design.py wait <run> --after <last seq>` after each turn (exit 3 = wait again).\n")
BLOCKS = {
    "agy": (H / ".gemini/config/skills/design", f"""## This harness

- Harness: **agy** (Antigravity CLI). Skill folder: `DESIGN=~/.gemini/config/skills/design`.
- Default picker: **local** (`design.py serve`). Use `--picker static` over SSH or when no browser opens. `--picker artifact` is not available here; fall back to local and say so.
- Default `--models self,claude,codex`: you make one option, and Claude Code and Codex each make one (`references/fanout.md`).
{WAIT}- Write files with `write_file`. Run Python as `python -X utf8`.
{PS}"""),
    "codex": (H / ".codex/skills/design", f"""## This harness

- Harness: **Codex**. Skill folder: `DESIGN=~/.codex/skills/design`.
- Default picker: **local** (`design.py serve`). Use `--picker static` over SSH or when no browser opens. `--picker artifact` is not available here; fall back to local and say so.
- Default `--models self,claude,agy`: you make one option, and Claude Code and agy each make one (`references/fanout.md`).
{WAIT}- Write files with `apply_patch` (`*** Add File: <path>`, every content line prefixed `+`). Run Python as `python -X utf8`.
{PS}"""),
    "opencode": (H / ".config/opencode/skills/design", f"""## This harness

- Harness: **Opencode**. Skill folder: `DESIGN=~/.config/opencode/skills/design`.
- Default picker: **local** (`design.py serve`). Use `--picker static` over SSH or when no browser opens. `--picker artifact` is not available here; fall back to local and say so.
- Default `--models self,claude,agy`: you make one option, and Claude Code and agy each make one (`references/fanout.md`; add `codex` for a fourth).
{WAIT}- Write files with your write tool. Run Python as `python -X utf8`.
"""),
    "hermes": (H / "AppData/Local/hermes/skills/software-development/design", f"""## This harness

- Harness: **Hermes**. Skill folder: `DESIGN=%LOCALAPPDATA%/hermes/skills/software-development/design`.
- Default picker: **local** (`design.py serve`). Use `--picker static` over SSH or when no browser opens. `--picker artifact` is not available here; fall back to local and say so.
- Default `--models self,claude,agy`: you make one option, and Claude Code and agy each make one (`references/fanout.md`; add `codex` for a fourth).
{WAIT}- Write files with `write_file`. Run Python as `python -X utf8`.
"""),
}
BLOCK = re.compile(r"## This harness\n.*?(?=\n## )", re.S)


def main():
    master = (SRC / "SKILL.md").read_text(encoding="utf-8")
    assert BLOCK.search(master)
    for name, (dest, block) in BLOCKS.items():
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(SRC, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
        (dest / "SKILL.md").write_bytes(BLOCK.sub(block.rstrip("\n") + "\n", master, count=1).encode("utf-8"))
        print(f"{name}: {dest}")


if __name__ == "__main__":
    main()
