"""Golden test for scripts/lexicon_scan.py: real slop in, checked-in report out."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = HERE.parent / "scripts" / "lexicon_scan.py"
FIXTURES = HERE / "fixtures"


def run(path):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), str(path)],
        capture_output=True, text=True, encoding="utf-8",
    )


def test_sample_matches_golden_report():
    result = run(FIXTURES / "sample.md")
    expected = (FIXTURES / "sample.expected.txt").read_text(encoding="utf-8")
    assert result.stdout == expected
    assert result.returncode == 1  # High-severity hits present


def test_clean_text_has_no_hits(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("Revenue grew 12% to $4.1M in Q3. We hired two engineers.\n", encoding="utf-8")
    result = run(clean)
    assert result.returncode == 0
    assert result.stdout == "no lexicon hits\n"
