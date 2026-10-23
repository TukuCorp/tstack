"""Claim 7: Personal Wiki section in each harness's global rules + Hermes personal-wiki skill."""
import re
import sys
from pathlib import Path

home = Path.home()
fail = []
for rel in [".claude/CLAUDE.md", ".config/opencode/AGENTS.md", ".codex/AGENTS.md", ".omp/agent/AGENTS.md"]:
    p = home / rel
    t = p.read_text(encoding="utf-8") if p.is_file() else ""
    m = re.search(r"(?ms)^## Personal Wiki\s*$(.*?)(?=^## |\Z)", t)
    if not m or "~/wiki/index.md" not in m.group(1):
        fail.append(f"{rel}: no '## Personal Wiki' section mentioning ~/wiki/index.md")
    else:
        print(f"ok: {rel}")
s = home / "AppData/Local/hermes/skills/personal-wiki/SKILL.md"
if not s.is_file() or not re.search(r"(?m)^name:\s*personal-wiki\s*$", s.read_text(encoding="utf-8")):
    fail.append("hermes personal-wiki SKILL.md missing or lacks name: personal-wiki")
else:
    print("ok: hermes personal-wiki skill")
if fail:
    print("\n".join(fail)); sys.exit(1)
print("personal wiki rules present in all harnesses")
