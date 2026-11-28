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

    def test_contract_sets_search_budget_quotes_and_gaps(self):
        # The worker stops at its search budget and hands back partial rows, verbatim quotes and gaps.
        transcript = ("Budget reached.\nBEGIN_SOURCES\n"
                      '{"bucket": "web", "url": "https://example.com/p", "title": "P", "query": "q", '
                      '"claim": "latency fell", "quote": "Median latency fell from 410 ms to 180 ms."}\n'
                      '{"gap": "no primary source for the 2025 adoption figure"}\n'
                      "END_SOURCES\n")
        fake = self.fake_hermes(transcript)
        p = subprocess.run(
            [sys.executable, "-I", str(_SCRIPT), "--brief", str(self.brief), "--out", str(self.out),
             "--id", "hermes-1", "--hermes", fake, "--max-searches", "9", "--print-prompt"],
            capture_output=True, text=True, encoding="utf-8", timeout=120)
        self.assertIn("at most 9 web searches", p.stdout)
        p = self.run_worker(fake)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        got = [json.loads(l) for l in self.out.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(got[0]["quote"], "Median latency fell from 410 ms to 180 ms.")
        summary = json.loads(p.stdout.split("HERMES_WORKER_DONE")[0])
        self.assertEqual((summary["invalid"], summary["gaps"]),
                         (0, ["no primary source for the 2025 adoption figure"]))
        self.assertEqual(pathlib.Path(str(self.out) + ".gaps").read_text(encoding="utf-8"),
                         "no primary source for the 2025 adoption figure\n")

    def test_print_contract_needs_no_brief(self):
        # A necro lane brief embeds the same source-row contract the Hermes worker gets.
        p = subprocess.run([sys.executable, "-I", str(_SCRIPT), "--print-contract", "--max-searches", "10"],
                           capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("BEGIN_SOURCES", p.stdout)
        self.assertIn("at most 10 web searches", p.stdout)
        self.assertNotIn("{{", p.stdout)

    def test_parse_lane_file_then_merge_into_ledger(self):
        # A necro lane writes the BEGIN_SOURCES block into its output file; --parse validates it
        # without running Hermes, and wide_pass --merge takes the rows like any worker's.
        lane = self.d / "rs-lane1.md"
        lane.write_text("# Lane 1\nNotes above the block are ignored.\n" + TRANSCRIPT.split("Searching")[0]
                        + "BEGIN_SOURCES\n"
                        '{"bucket": "industry", "url": "https://example.com/report", "title": "R", "query": "q", '
                        '"claim": "capacity 3 GW", "quote": "Installed capacity reached 3 GW in 2025."}\n'
                        '{"gap": "no 2026 figure"}\nEND_SOURCES\n', encoding="utf-8")
        p = subprocess.run([sys.executable, "-I", str(_SCRIPT), "--parse", str(lane), "--out", str(self.out),
                            "--id", "lane1"], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertIn("HERMES_WORKER_DONE lane1 rows=1 status=ok", p.stdout)
        self.assertEqual(pathlib.Path(str(self.out) + ".gaps").read_text(encoding="utf-8"), "no 2026 figure\n")
        ledger = self.d / "ledger.jsonl"
        ledger.write_text("", encoding="utf-8")
        m = subprocess.run([sys.executable, "-I", str(_SCRIPT.parent / "wide_pass.py"), "--ledger", str(ledger),
                            "--merge", str(self.out)], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(m.returncode, 0, m.stdout + m.stderr)
        rows = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([(r["pass"], r["quote"], r["discovered_via"]) for r in rows],
                         [("agentic", "Installed capacity reached 3 GW in 2025.", "lane1: q")])

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
