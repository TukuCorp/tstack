"""/codebase reads an existing Floorplan map in all five harnesses; the step is byte-identical everywhere (2026-11-27)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPIES = {
    "claude": ROOT / "claude/skills/codebase/SKILL.md",
    "agy": ROOT / "agy/skills/codebase/SKILL.md",
    "codex": ROOT / "codex/skills/codebase/SKILL.md",
    "opencode": ROOT / "opencode/skills/codebase/SKILL.md",
    "hermes": ROOT / "hermes/skills/engineering/codebase/SKILL.md",
}
STEP = re.compile(r"\*\*Floorplan map\.\*\*.*?(?=\nThen spawn a sub-agent)", re.S)


def step(name):
    text = COPIES[name].read_text(encoding="utf-8").replace("\r\n", "\n")
    m = STEP.search(text)
    return m.group(0) if m else None


class CodebaseFloorplanTests(unittest.TestCase):
    def test_every_copy_has_the_same_floorplan_step(self):
        master = step("claude")
        self.assertIsNotNone(master, "claude: Floorplan step missing")
        for name in COPIES:
            self.assertEqual(step(name), master, f"{name}: Floorplan step missing or drifted")

    def test_step_reads_only_and_names_no_harness(self):
        master = step("claude") or ""
        for cmd in ("plugin install", "npm install", "build.mjs", "scan.mjs"):
            self.assertNotIn(cmd, master, "the step must only read an existing map")
        for tool in ("Claude", "Codex", "Opencode", "Hermes", "agy"):
            self.assertNotIn(tool, master, f"step names {tool}; mirrors must stay harness-neutral")


if __name__ == "__main__":
    unittest.main()
