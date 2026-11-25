"""Repo-authored files keep their committed line endings.

On 2026-11-23 a `sed -i 's/$/\\r/'` turned README.md from LF to CRLF and the 178-line churn was pushed
(2da6c5c, undone in e92ab58). Mirror folders are skipped: sync.py copies those byte-for-byte from live files.
"""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sync  # noqa: E402

MIRRORS = tuple(d + "/" for d in sync.TOOL_DIRS)


def eol_changes(root):
    """Tracked, non-mirror files whose working-tree EOL style differs from the index."""
    out = subprocess.run(["git", "ls-files", "--eol", "-z"], cwd=root, capture_output=True, check=True).stdout
    bad = []
    for rec in out.decode("utf-8").split("\0"):
        if "\t" not in rec:
            continue
        info, path = rec.split("\t", 1)
        idx, work = info.split()[:2]
        if path.startswith(MIRRORS) or work == "w/" or "-text" in (idx, work) or "none" in idx + work:
            continue
        if idx[2:] != work[2:]:
            bad.append(f"{path}: {idx} -> {work}")
    return bad


class LineEndingTests(unittest.TestCase):
    def test_authored_files_keep_committed_line_endings(self):
        self.assertEqual(eol_changes(ROOT), [], "line endings changed; restore the original EOL before committing")


if __name__ == "__main__":
    unittest.main()
