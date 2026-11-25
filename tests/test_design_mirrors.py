"""/design exists in all five harnesses with the full studio; copies differ only in their '## This harness' block (2026-11-25)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "claude/skills/design"
MIRRORS = {
    "agy": (ROOT / "agy/skills/design", "~/.gemini/config/skills/design"),
    "codex": (ROOT / "codex/skills/design", "~/.codex/skills/design"),
    "opencode": (ROOT / "opencode/skills/design", "~/.config/opencode/skills/design"),
    "hermes": (ROOT / "hermes/skills/software-development/design", "hermes/skills/software-development/design"),
}
BLOCK = re.compile(r"## This harness\n.*?(?=\n## )", re.S)


def tree(d):
    return {p.relative_to(d).as_posix(): p.read_bytes() for p in d.rglob("*")
            if p.is_file() and "__pycache__" not in p.parts}


class DesignMirrorTests(unittest.TestCase):
    def test_every_mirror_has_the_same_files_and_bytes(self):
        master = tree(MASTER)
        master.pop("SKILL.md")
        for name, (d, _) in MIRRORS.items():
            got = tree(d)
            got.pop("SKILL.md", None)
            self.assertEqual(sorted(got), sorted(master), f"{name}: file list differs")
            changed = [k for k in master if got[k] != master[k]]
            self.assertEqual(changed, [], f"{name}: shared files differ; re-render the mirrors")

    def test_skill_md_differs_only_in_this_harness_block(self):
        text = (MASTER / "SKILL.md").read_text(encoding="utf-8")
        self.assertIsNotNone(BLOCK.search(text))
        body = BLOCK.sub("", text)
        for name, (d, own) in MIRRORS.items():
            mirror = (d / "SKILL.md").read_text(encoding="utf-8")
            self.assertEqual(BLOCK.sub("", mirror), body, f"{name}: SKILL.md changed outside 'This harness'")
            block = BLOCK.search(mirror).group(0)
            self.assertIn(own, block, f"{name}: block must name its own skill folder")
            self.assertNotIn("Artifact tool", block, f"{name}: artifacts are Claude Code only")


if __name__ == "__main__":
    unittest.main()
