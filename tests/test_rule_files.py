"""Global agent rule files stay short and calm: current models over-apply shouted or old-model rules."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE_FILES = ["claude/CLAUDE.md", "opencode/AGENTS.md", "codex/AGENTS.md", "agy/GEMINI.md"]
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

    def test_rule_files_size_work_in_agent_units(self):
        missing = [rel for rel in RULE_FILES if "## Estimates" not in (ROOT / rel).read_text(encoding="utf-8")]
        self.assertEqual(missing, [], "each rule file needs the agent-unit Estimates section")

    def test_agy_rules_contain_codex(self):
        # agy (~/.gemini/GEMINI.md) carries every Codex section verbatim plus the Claude Code
        # workflow sections (2026-11-24); a Codex rule edit must be copied into agy too.
        agy = (ROOT / "agy/GEMINI.md").read_text(encoding="utf-8")
        # Self-paths and file-writing tools differ by design: each harness names its own.
        codex = (ROOT / "codex/AGENTS.md").read_text(encoding="utf-8").replace(
            "/.codex/skills/", "/.gemini/config/skills/").replace(
            "`apply_patch` (`*** Add File: <path>`, every content line prefixed `+`)", "`write_file`")
        sections = [sec.strip() for sec in re.split(r"(?m)^(?=## )", codex) if sec.strip()]
        missing = [sec.splitlines()[0] for sec in sections if sec not in agy]
        self.assertEqual(missing, [], "agy/GEMINI.md lost or changed these Codex sections")
        for heading in ("## Initialization", "## Debugging Rules", "## Task Management", "## Subagents"):
            self.assertIn(heading, agy)


if __name__ == "__main__":
    unittest.main()
