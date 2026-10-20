"""End-to-end tests for scripts/verify_run.py against real throwaway git repos.

Run: python -I tests/test_verify_run.py   (from the skill directory)
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RUNNER = Path(__file__).resolve().parent.parent / "scripts" / "verify_run.py"

BUGGY = "def add(a, b):\n    return a - b\n"
FIXED = "def add(a, b):\n    return a + b\n"
TEST = (
    "import sys, os\n"
    "sys.path.insert(0, os.getcwd())\n"
    "from calc import add\n"
    "assert add(2, 3) == 5, 'add is wrong'\n"
    "print('ok')\n"
)
OLD_TEST = (
    "import sys, os\n"
    "sys.path.insert(0, os.getcwd())\n"
    "from calc import add\n"
    "assert add(0, 0) == 0\n"
    "assert add(2, 3) == 5\n"
)


def git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True,
                          text=True, encoding="utf-8").stdout


def make_repo(tmp):
    repo = Path(tmp) / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "core.autocrlf", "false")
    (repo / "calc.py").write_text(BUGGY, encoding="utf-8")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "-m", "base")
    return repo


def commit_all(repo, msg):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


def write_checks(repo, claims):
    path = repo / ".verify" / "task.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps({"task": "t", "claims": claims}), encoding="utf-8")
    return path


def run(repo, checks, *extra):
    p = subprocess.run([sys.executable, "-I", str(RUNNER), str(checks), *extra], cwd=repo,
                       capture_output=True, text=True, encoding="utf-8")
    return p.returncode, p.stdout + p.stderr


FIX_CLAIM = {"id": "fix", "claim": "add is fixed", "run": "python tests/test_calc.py",
             "fails_on_base": True, "base_fail_pattern": "add is wrong"}
TRUE_CLAIM = {"id": "true", "claim": "python runs", "run": "python -c \"print(1)\""}


class VerifyRunTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = make_repo(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def add_fix_and_test(self, fix=True):
        if fix:
            (self.repo / "calc.py").write_text(FIXED, encoding="utf-8")
        (self.repo / "tests").mkdir(exist_ok=True)
        (self.repo / "tests" / "test_calc.py").write_text(TEST, encoding="utf-8")

    def report(self, out):
        m = re.search(r"^REPORT: (.+)$", out, re.M)
        self.assertIsNotNone(m, out)
        return (self.repo / m.group(1).strip()).read_text(encoding="utf-8")

    def test_real_fix_committed_is_verified(self):
        self.add_fix_and_test()
        commit_all(self.repo, "fix")
        code, out = run(self.repo, write_checks(self.repo, [FIX_CLAIM]), "--independence", "subagent")
        self.assertEqual(code, 0, out)
        self.assertIn("VERDICT: verified", out)
        head = git(self.repo, "rev-parse", "HEAD").strip()
        rep = self.report(out)
        self.assertIn(f"head_sha: {head}", rep)
        self.assertIn("independence: subagent", rep)
        self.assertIn("reports/", (self.repo / ".git" / "info" / "exclude").read_text(encoding="utf-8"))
        self.assertEqual(git(self.repo, "status", "--porcelain", "--untracked-files=no"), "")

    def test_test_passing_on_base_is_not_reproduced(self):
        self.add_fix_and_test(fix=False)
        (self.repo / "calc.py").write_text(FIXED, encoding="utf-8")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "--amend", "-m", "base already fixed")
        (self.repo / "README.md").write_text("x", encoding="utf-8")
        commit_all(self.repo, "noop")
        code, out = run(self.repo, write_checks(self.repo, [FIX_CLAIM, TRUE_CLAIM]))
        self.assertEqual(code, 1, out)
        self.assertIn("VERDICT: partial", out)
        self.assertIn("passed on base", out)

    def test_base_failure_for_wrong_reason_is_not_reproduced(self):
        self.add_fix_and_test()
        commit_all(self.repo, "fix")
        claim = dict(FIX_CLAIM, base_fail_pattern="this text never appears")
        code, out = run(self.repo, write_checks(self.repo, [claim]))
        self.assertEqual(code, 2, out)
        self.assertIn("VERDICT: refuted", out)

    def test_failing_check_on_head_is_contradicted(self):
        self.add_fix_and_test(fix=False)
        commit_all(self.repo, "claimed fix, no code change")
        code, out = run(self.repo, write_checks(self.repo, [FIX_CLAIM, TRUE_CLAIM]))
        self.assertEqual(code, 2, out)
        self.assertIn("VERDICT: refuted", out)
        self.assertIn("contradicted", out)

    def test_weakened_existing_test_caps_at_partial(self):
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "test_old.py").write_text(OLD_TEST, encoding="utf-8")
        commit_all(self.repo, "add old test")
        (self.repo / "tests" / "test_old.py").write_text(
            OLD_TEST.replace("assert add(2, 3) == 5\n", ""), encoding="utf-8")
        commit_all(self.repo, "make it pass")
        claim = {"id": "old", "claim": "old test passes", "run": "python tests/test_old.py"}
        code, out = run(self.repo, write_checks(self.repo, [claim]))
        self.assertEqual(code, 1, out)
        self.assertIn("VERDICT: partial", out)
        self.assertIn("tests/test_old.py", out)

    def test_uncommitted_fix_uses_head_as_base(self):
        self.add_fix_and_test()
        code, out = run(self.repo, write_checks(self.repo, [FIX_CLAIM]))
        self.assertEqual(code, 0, out)
        rep = self.report(out)
        self.assertRegex(rep, r"patch_id: [0-9a-f]{40}")
        self.assertIn(f"base: {git(self.repo, 'rev-parse', 'HEAD').strip()}", rep)

    def test_claim_without_check_and_timeout_are_not_reproduced(self):
        claims = [
            {"id": "nocheck", "claim": "the UI looks right", "run": None},
            {"id": "slow", "claim": "slow thing", "run": "python -c \"import time; time.sleep(5)\"",
             "timeout": 1},
        ]
        code, out = run(self.repo, write_checks(self.repo, claims))
        self.assertEqual(code, 2, out)
        self.assertIn("no check", out)
        self.assertIn("timed out", out)

    def test_same_commit_gives_same_verdict(self):
        self.add_fix_and_test()
        commit_all(self.repo, "fix")
        checks = write_checks(self.repo, [FIX_CLAIM, TRUE_CLAIM])
        first = run(self.repo, checks)
        second = run(self.repo, checks)
        self.assertEqual(first[0], second[0])
        self.assertEqual(re.findall(r"^(?:VERDICT|- ).*", first[1], re.M),
                         re.findall(r"^(?:VERDICT|- ).*", second[1], re.M))

    def test_invalid_checks_file_exits_3(self):
        code, out = run(self.repo, write_checks(self.repo, [{"id": "x", "claim": "y", "run": "z",
                                                              "fails_on_base": True}]))
        self.assertEqual(code, 3, out)
        self.assertIn("base_fail_pattern", out)


if __name__ == "__main__":
    unittest.main()
