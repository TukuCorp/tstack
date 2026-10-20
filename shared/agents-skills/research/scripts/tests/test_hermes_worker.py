"""hermes_worker.py against a stand-in `hermes` that prints a fixed transcript (the subprocess
boundary is the only thing replaced; parsing, validation, files and exit codes are real).

Run from anywhere:  python -m unittest discover -s <skill>/scripts/tests -v
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "hermes_worker.py"
_FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"

TRANSCRIPT = """Searching for sources...
I found several relevant pages.
BEGIN_SOURCES
{"bucket": "web", "url": "https://www.perplexity.ai/hub/blog/photon", "title": "Photon", "query": "perplexity photon", "claim": "Photon replaced the open-source engine"}
{"bucket": "web", "url": "https://www.perplexity.ai/hub/blog/photon", "title": "Photon again", "query": "photon", "claim": "dup"}
{"bucket": "industry", "url": "ftp://example.com/x", "title": "bad scheme", "query": "q", "claim": "c"}
{"bucket": "news", "url": "https://example.com/n", "title": "bad bucket", "query": "q", "claim": "c"}
not json at all
{"bucket": "academia", "url": "https://arxiv.org/abs/2101.00001", "title": "Paper", "query": "q2", "claim": "method"}
END_SOURCES
Done.
"""


class HermesWorker(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = pathlib.Path(self._tmp.name)
        self.brief = self.d / "brief.md"
        self.brief.write_text("Find primary sources on Perplexity Photon.", encoding="utf-8")
        self.out = self.d / "x.hermes-1.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def fake_hermes(self, transcript, code=0):
        t = self.d / "transcript.txt"
        t.write_text(transcript, encoding="utf-8")
        fake = self.d / "fake_hermes.py"
        fake.write_text(
            "import sys, pathlib\n"
            "assert sys.argv[1] == '-z' and 'BEGIN_SOURCES' in sys.argv[2], sys.argv\n"
            f"sys.stdout.write(pathlib.Path(r'{t}').read_text(encoding='utf-8'))\n"
            f"sys.exit({code})\n", encoding="utf-8")
        return f'"{pathlib.Path(sys.executable).as_posix()}" "{fake.as_posix()}"'

    def run_worker(self, hermes):
        return subprocess.run(
            [sys.executable, "-I", str(_SCRIPT), "--brief", str(self.brief), "--out", str(self.out),
             "--id", "hermes-1", "--hermes", hermes],
            capture_output=True, text=True, encoding="utf-8", timeout=120)

    def test_valid_rows_written_and_invalid_counted(self):
        p = self.run_worker(self.fake_hermes(TRANSCRIPT))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        got = [json.loads(l) for l in self.out.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([r["url"] for r in got],
                         ["https://www.perplexity.ai/hub/blog/photon", "https://arxiv.org/abs/2101.00001"])
        self.assertEqual(got[0], {"bucket": "web", "url": "https://www.perplexity.ai/hub/blog/photon",
                                  "title": "Photon", "discovered_via": "hermes-1: perplexity photon",
                                  "hint": "Photon replaced the open-source engine"})
        self.assertIn("HERMES_WORKER_DONE hermes-1 rows=2 status=ok", p.stdout)
        summary = json.loads(p.stdout.split("HERMES_WORKER_DONE")[0])
        self.assertEqual(summary["invalid"], 4)
        self.assertTrue(pathlib.Path(str(self.out) + ".log").read_text(encoding="utf-8").count("BEGIN_SOURCES"))

    def test_missing_markers_is_empty_and_exit_1(self):
        p = self.run_worker(self.fake_hermes("I could not find anything useful.\n"))
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("status=empty", p.stdout)
        self.assertEqual(self.out.read_text(encoding="utf-8"), "")

    def test_hermes_failure_is_reported(self):
        p = self.run_worker(self.fake_hermes("boom\n", code=3))
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("status=failed", p.stdout)

    def test_real_hermes_transcript_fixtures(self):
        for fx in sorted(_FIXTURES.glob("hermes-transcript-*.txt")):
            with self.subTest(fixture=fx.name):
                expected = json.loads(fx.with_suffix(".expected.json").read_text(encoding="utf-8"))
                p = self.run_worker(self.fake_hermes(fx.read_text(encoding="utf-8")))
                got = [json.loads(l) for l in self.out.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
