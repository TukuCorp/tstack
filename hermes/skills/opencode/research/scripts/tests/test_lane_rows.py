"""lane_rows.py: the source-row contract for agentic lanes, and parsing a lane's output file.

Real files and processes only (no mocks): a lane file goes in, a ledger-ready JSONL comes out, and
wide_pass.py --merge folds it into a ledger.
Run from anywhere:  python -m unittest discover -s <skill>/scripts/tests -v
"""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

_SCRIPTS = pathlib.Path(__file__).resolve().parent.parent
_SCRIPT = _SCRIPTS / "lane_rows.py"
_FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"

LANE = """# Lane rs1
Notes above the block are ignored.
BEGIN_SOURCES
{"bucket": "web", "url": "https://www.perplexity.ai/hub/blog/photon", "title": "Photon", "query": "perplexity photon", "claim": "Photon replaced the open-source engine", "quote": "Photon replaced the open-source engine in 2025."}
{"bucket": "web", "url": "https://www.perplexity.ai/hub/blog/photon", "title": "Photon again", "query": "photon", "claim": "dup"}
{"bucket": "industry", "url": "ftp://example.com/x", "title": "bad scheme", "query": "q", "claim": "c"}
{"bucket": "news", "url": "https://example.com/n", "title": "bad bucket", "query": "q", "claim": "c"}
not json at all
{"bucket": "academia", "url": "https://arxiv.org/abs/2101.00001", "title": "Paper", "query": "q2", "claim": "method"}
{"gap": "no primary source for the 2025 adoption figure"}
END_SOURCES
Done.
"""


def run(*args):
    return subprocess.run([sys.executable, "-I", str(_SCRIPT), *args],
                          capture_output=True, text=True, encoding="utf-8", timeout=60)


class LaneRows(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.d = pathlib.Path(self._tmp.name)
        self.lane = self.d / "x.rs1.md"
        self.out = self.d / "x.rs1.jsonl"

    def tearDown(self):
        self._tmp.cleanup()

    def test_print_contract(self):
        p = run("--print-contract", "--max-searches", "10")
        self.assertEqual(p.returncode, 0, p.stderr)
        for needle in ("BEGIN_SOURCES", "at most 10 web searches", '{"gap": "what is still missing"}', '"quote"'):
            self.assertIn(needle, p.stdout)
        self.assertNotIn("{{", p.stdout)
        self.assertNotIn("ermes", p.stdout)

    def test_parse_writes_valid_rows_quotes_and_gaps(self):
        self.lane.write_text(LANE, encoding="utf-8")
        p = run("--parse", str(self.lane), "--out", str(self.out), "--id", "rs1")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        got = [json.loads(l) for l in self.out.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(got[0], {"bucket": "web", "url": "https://www.perplexity.ai/hub/blog/photon",
                                  "title": "Photon", "discovered_via": "rs1: perplexity photon",
                                  "hint": "Photon replaced the open-source engine",
                                  "quote": "Photon replaced the open-source engine in 2025."})
        self.assertEqual([r["url"] for r in got],
                         ["https://www.perplexity.ai/hub/blog/photon", "https://arxiv.org/abs/2101.00001"])
        self.assertNotIn("quote", got[1])
        self.assertIn("LANE_ROWS_DONE rs1 rows=2 status=ok", p.stdout)
        summary = json.loads(p.stdout.split("LANE_ROWS_DONE")[0])
        self.assertEqual((summary["invalid"], summary["gaps"]), (4, ["no primary source for the 2025 adoption figure"]))
        self.assertEqual(pathlib.Path(str(self.out) + ".gaps").read_text(encoding="utf-8"),
                         "no primary source for the 2025 adoption figure\n")

    def test_missing_markers_is_empty_and_exit_1(self):
        self.lane.write_text("I could not find anything useful.\n", encoding="utf-8")
        p = run("--parse", str(self.lane), "--out", str(self.out), "--id", "rs1")
        self.assertEqual(p.returncode, 1, p.stdout + p.stderr)
        self.assertIn("status=empty", p.stdout)
        self.assertEqual(self.out.read_text(encoding="utf-8"), "")

    def test_real_agent_transcript_fixtures(self):
        for fx in sorted(_FIXTURES.glob("transcript-*.txt")):
            with self.subTest(fixture=fx.name):
                expected = json.loads(fx.with_suffix(".expected.json").read_text(encoding="utf-8"))
                p = run("--parse", str(fx), "--out", str(self.out), "--id", "rs1")
                self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
                got = [json.loads(l) for l in self.out.read_text(encoding="utf-8").splitlines()]
                self.assertEqual(got, expected)

    def test_parsed_rows_merge_into_ledger(self):
        self.lane.write_text(LANE, encoding="utf-8")
        run("--parse", str(self.lane), "--out", str(self.out), "--id", "rs1")
        ledger = self.d / "ledger.jsonl"
        ledger.write_text("", encoding="utf-8")
        m = subprocess.run([sys.executable, "-I", str(_SCRIPTS / "wide_pass.py"), "--ledger", str(ledger),
                            "--merge", str(self.out)], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(m.returncode, 0, m.stdout + m.stderr)
        rows = [json.loads(l) for l in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([(r["pass"], r["discovered_via"]) for r in rows],
                         [("agentic", "rs1: perplexity photon"), ("agentic", "rs1: q2")])
        self.assertEqual(rows[0]["quote"], "Photon replaced the open-source engine in 2025.")


if __name__ == "__main__":
    unittest.main()
