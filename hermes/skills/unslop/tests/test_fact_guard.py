"""Golden test for scripts/fact_guard.py: a rewrite that drops and adds facts is caught."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCRIPT = HERE.parent / "scripts" / "fact_guard.py"
FIXTURES = HERE / "fixtures"


def run(before, after):
    return subprocess.run(
        [sys.executable, "-X", "utf8", str(SCRIPT), str(before), str(after)],
        capture_output=True, text=True, encoding="utf-8",
    )


def test_drift_matches_golden_report():
    result = run(FIXTURES / "drift.before.md", FIXTURES / "drift.after.md")
    assert result.stdout == (FIXTURES / "drift.expected.txt").read_text(encoding="utf-8")
    assert result.returncode == 1


def test_faithful_rewrite_passes(tmp_path):
    before = tmp_path / "b.md"
    after = tmp_path / "a.md"
    before.write_text("We shipped 3 fixes on 2026-11-24; see `fix.py` and https://x.org/a.\n", encoding="utf-8")
    after.write_text("On 2026-11-24 we shipped 3 fixes (https://x.org/a, `fix.py`).\n", encoding="utf-8")
    result = run(before, after)
    assert result.returncode == 0
    assert result.stdout == "no fact drift\n"
