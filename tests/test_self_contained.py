"""Each harness loads and runs only its own files: no rule or skill points into another harness's folders.

Skills whose job is to drive or study another agent may name it; they are listed in ORCHESTRATORS.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# mirror dir -> pattern for its own home (allowed); everything else in FOREIGN is a borrow.
HARNESSES = {
    "claude": ["claude/CLAUDE.md", "claude/skills", "claude/agents"],
    "codex": ["codex/AGENTS.md", "codex/skills", "codex/agents"],
    "opencode": ["opencode/AGENTS.md", "opencode/skills", "opencode/agents"],
    "agy": ["agy/GEMINI.md", "agy/skills", "agy/skills.json"],
    "hermes": ["hermes/skills"],
}
FOREIGN = {
    "claude": re.compile(r"\.claude[/\\](skills|agents|CLAUDE\.md|commands|hooks)"),
    "codex": re.compile(r"\.codex[/\\](skills|AGENTS\.md|agents)"),
    "opencode": re.compile(r"\.config[/\\]opencode[/\\](skills|AGENTS\.md|agents)"),
    "agy": re.compile(r"\.gemini[/\\](config|GEMINI\.md)"),
    "hermes": re.compile(r"hermes[/\\](skills|hermes-agent|SOUL\.md)|\.hermes[/\\]"),
    "pool": re.compile(r"(~|tukum)[/\\]\.agents[/\\]skills"),
}
# Skills that orchestrate or analyze other agents by design (directory names under */skills/).
ORCHESTRATORS = {"necro", "coop", "reflect", "herdr", "grill-with-ui", "dloop", "swarm",
                 ".archive", ".hub", "autonomous-ai-agents"}
TEXT = {".md", ".py", ".sh", ".ps1", ".json", ".toml", ".yaml", ".yml", ".js", ".ts", ".txt"}


def files(rel):
    p = ROOT / rel
    if p.is_file():
        yield p
    elif p.is_dir():
        for f in p.rglob("*"):
            if f.is_file() and f.suffix in TEXT and "__pycache__" not in f.parts:
                yield f


class SelfContained(unittest.TestCase):
    def test_no_harness_points_into_another(self):
        hits = []
        for owner, rels in HARNESSES.items():
            for rel in rels:
                for f in files(rel):
                    if ORCHESTRATORS & set(f.relative_to(ROOT).parts):
                        continue
                    for n, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                        for target, pat in FOREIGN.items():
                            if target != owner and pat.search(line):
                                hits.append(f"{f.relative_to(ROOT)}:{n} -> {target}: {line.strip()[:90]}")
        self.assertEqual(hits, [], "point at this harness's own copy instead:\n" + "\n".join(hits[:40]))

    def test_agy_loads_no_extra_skill_dirs(self):
        text = (ROOT / "agy/skills.json").read_text(encoding="utf-8")
        self.assertNotIn('"path"', text, "agy/skills.json must not add another harness's skill dir")


if __name__ == "__main__":
    unittest.main()
