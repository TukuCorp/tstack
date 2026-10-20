"""wide_pass.py run as a process: --merge of Hermes worker rows (no network) and the live
Perplexity fallback (real call; skipped only when neither PERPLEXITY_API_KEY nor a Hermes
install is present).

Run from anywhere:  python -m unittest discover -s <skill>/scripts/tests -v
"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

_SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "wide_pass.py"


def run(args, env=None):
    p = subprocess.run([sys.executable, "-I", str(_SCRIPT), *args], capture_output=True,
                       text=True, encoding="utf-8", env=env, timeout=600)
    if p.returncode != 0:
        raise AssertionError(p.stdout + p.stderr)
    return json.loads(p.stdout)


def rows(path):
    return [json.loads(line) for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines()
            if line.strip()]


def hermes_present():
    candidates = [os.environ.get("HERMES_AGENT_DIR", ""),
                  os.path.join(os.environ.get("LOCALAPPDATA", ""), "hermes", "hermes-agent"),
                  os.path.expanduser("~/.hermes/hermes-agent")]
    return any(c and os.path.isdir(c) for c in candidates)


class Merge(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        d = pathlib.Path(self._tmp.name)
        self.ledger = d / "ledger.jsonl"
        self.ledger.write_text(json.dumps({
            "id": "we-004", "bucket": "web", "url": "https://example.com/already", "title": "x",
            "tier": 4, "status": "candidate", "pass": "wide"}) + "\n", encoding="utf-8")
        self.worker = d / "w.hermes-1.jsonl"
        worker_rows = [
            {"bucket": "web", "url": "https://www.example.com/already/?utm_source=a", "title": "dup",
             "discovered_via": "hermes-1: q1", "hint": "h"},
            {"bucket": "web", "url": "https://example.com/new", "title": "New page",
             "discovered_via": "hermes-1: q2", "hint": "supports the latency claim"},
            {"bucket": "academia", "url": "https://arxiv.org/abs/2101.00001v2", "title": "Paper",
             "discovered_via": "hermes-1: q3", "hint": "original method"},
            {"bucket": "blogs", "url": "https://example.com/bad-bucket", "title": "b",
             "discovered_via": "hermes-1: q4", "hint": ""},
            {"bucket": "web", "url": "not a url", "title": "bad", "discovered_via": "hermes-1: q5"},
        ]
        self.worker.write_text("\n".join(json.dumps(r) for r in worker_rows) + "\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def test_merge_dedupes_validates_and_continues_ids(self):
        summary = run(["--ledger", str(self.ledger), "--merge", str(self.worker)])
        self.assertEqual(summary["merged"], {str(self.worker): {"added": 2, "duplicate": 1, "invalid": 2}})
        added = rows(self.ledger)[1:]
        self.assertEqual([r["id"] for r in added], ["we-005", "ac-001"])
        for r in added:
            self.assertEqual((r["status"], r["pass"]), ("candidate", "agentic"))
        self.assertEqual(added[0]["hint"], "supports the latency claim")
        self.assertEqual(added[0]["discovered_via"], "hermes-1: q2")
        self.assertEqual(added[0]["tier"], 4)
        self.assertEqual(added[1]["tier"], 3)

    def test_merge_twice_adds_nothing(self):
        run(["--ledger", str(self.ledger), "--merge", str(self.worker)])
        summary = run(["--ledger", str(self.ledger), "--merge", str(self.worker)])
        self.assertEqual(summary["merged"][str(self.worker)]["added"], 0)


@unittest.skipUnless(os.environ.get("PERPLEXITY_API_KEY") or hermes_present(),
                     "needs PERPLEXITY_API_KEY or a Hermes install")
class PerplexityFallback(unittest.TestCase):
    def test_web_bucket_filled_by_perplexity_when_firecrawl_unavailable(self):
        env = {k: v for k, v in os.environ.items() if k != "FIRECRAWL_API_KEY"}
        with tempfile.TemporaryDirectory() as d:
            ledger = pathlib.Path(d) / "l.jsonl"
            summary = run(["--ledger", str(ledger), "--web-target", "5",
                           "--web-query", "Perplexity Photon retrieval engine"], env=env)
            self.assertEqual(summary["firecrawl"], "unavailable: no key")
            self.assertTrue(summary["perplexity"].startswith("ok"), summary)
            self.assertGreaterEqual(summary["by_bucket"].get("web", 0), 1, summary)
            got = rows(ledger)
            self.assertTrue(all(r["discovered_via"].startswith("perplexity search=") for r in got))
            self.assertTrue(any("perplexity.ai" in r["url"] for r in got), got)


if __name__ == "__main__":
    unittest.main()
