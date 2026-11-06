"""Every tracked code file stays at or under 1000 lines (agents split big files early)."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_LINES = 1000
# Known debt, split pending: the live Hermes job has globals-heavy run state and 7 failing tests
# (switch_model / new_phase_commits not implemented yet). Remove once it is split.
EXEMPT = {"hermes/scripts/cc-nightly.py"}
CODE_SUFFIXES = {".py", ".ps1", ".psm1", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh"}


class FileLengthTests(unittest.TestCase):
    def test_code_files_at_most_1000_lines(self):
        tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                                 text=True, encoding="utf-8", check=True).stdout.splitlines()
        too_long = []
        for rel in tracked:
            path = ROOT / rel
            if rel not in EXEMPT and path.suffix.lower() in CODE_SUFFIXES and path.is_file():
                count = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
                if count > MAX_LINES:
                    too_long.append(f"{rel}: {count}")
        self.assertEqual(too_long, [], f"split these files below {MAX_LINES} lines")


if __name__ == "__main__":
    unittest.main()
