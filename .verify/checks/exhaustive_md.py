"""Assert each research copy's references/exhaustive.md has the Step 3 agentic-pass section
and exactly 2 lines starting with '- Perplexity search (fast preset)'."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PARENTS = [
    "claude/skills/research",
    "codex/skills/research",
    "opencode/skills/research",
    "shared/agents-skills/research",
    "hermes/skills/opencode/research",
]
failures = []
for parent in PARENTS:
    path = ROOT / parent / "references" / "exhaustive.md"
    if not path.is_file():
        failures.append(f"{path}: missing")
        continue
    lines = path.read_text(encoding="utf-8").splitlines()
    if not any(l.startswith("### Step 3 - optional agentic pass") for l in lines):
        failures.append(f"{path}: no '### Step 3 - optional agentic pass' heading")
    n = sum(1 for l in lines if l.startswith("- Perplexity search (fast preset)"))
    if n != 2:
        failures.append(f"{path}: expected 2 '- Perplexity search (fast preset)' lines, found {n}")
    else:
        print(f"ok {parent}")
assert not failures, "exhaustive.md check failed:\n" + "\n".join(failures)
print("all 5 exhaustive.md files pass")
