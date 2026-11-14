"""Global agent rule files stay short and calm: current models over-apply shouted or old-model rules."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_FILES = ["claude/CLAUDE.md", "opencode/AGENTS.md", "codex/AGENTS.md"]
MAX_LINES = 100
# Shouting markers and habits written for older models (see the 2026-11-12 activeContext section).
SHOUTING = re.compile(r"\b(IMPORTANT|MUST|NEVER|ALWAYS|CRITICAL|EXTREMELY)\b")
OLD_MODEL_HABITS = re.compile(r"no laziness|don't be lazy|think harder|ultrathink", re.IGNORECASE)


class RuleFileTests(unittest.TestCase):
    def test_rule_files_within_line_budget(self):
        for rel in RULE_FILES:
            count = len((ROOT / rel).read_text(encoding="utf-8").splitlines())
            self.assertLessEqual(count, MAX_LINES, f"{rel}: {count} lines; move detail into skills")

    def test_rule_files_have_no_shouting_or_old_model_habits(self):
        hits = []
        for rel in RULE_FILES:
            for n, line in enumerate((ROOT / rel).read_text(encoding="utf-8").splitlines(), 1):
                if SHOUTING.search(line) or OLD_MODEL_HABITS.search(line):
                    hits.append(f"{rel}:{n}: {line.strip()[:80]}")
        self.assertEqual(hits, [], "state rules plainly; enforce must-nevers with hooks instead")


if __name__ == "__main__":
    unittest.main()
