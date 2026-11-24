"""End-to-end tests for scripts/shot.py with a real agent-browser (nothing mocked).

Run: python -X utf8 tests/test_shot.py   (from the skill directory; needs agent-browser on PATH)
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SHOT = Path(__file__).resolve().parent.parent / "scripts" / "shot.py"

# The 2026-11 deck bug: a 900px-wide row pushes the language toggle off a phone screen,
# while a narrow desktop window still shows it.
BAD = ('<!doctype html><meta name="viewport" content="width=device-width">'
       '<body style="margin:0"><div style="width:900px">'
       '<button style="margin-left:700px">EN|VI</button></div>'
       '<button style="display:none">hidden</button></body>')
GOOD = ('<!doctype html><meta name="viewport" content="width=device-width">'
        '<body style="margin:0"><button>EN|VI</button><p>Fits on every screen.</p></body>')


def run(target, out):
    return subprocess.run([sys.executable, "-X", "utf8", str(SHOT), str(target), "--out", str(out)],
                          capture_output=True, text=True, timeout=180)


@unittest.skipUnless(shutil.which("agent-browser"), "agent-browser not installed")
class ShotTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def page(self, name, html):
        p = self.tmp / name
        p.write_text(html, encoding="utf-8")
        return p

    def test_offscreen_toggle_on_phone_fails(self):
        r = run(self.page("bad.html", BAD), self.tmp / "out")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        phone = next(line for line in r.stdout.splitlines() if line.startswith("phone "))
        self.assertIn("EN|VI", phone)
        self.assertIn("overflow", phone)
        desktop = next(line for line in r.stdout.splitlines() if line.startswith("desktop "))
        self.assertIn("OK", desktop)
        self.assertNotIn("hidden", r.stdout)  # display:none controls are not reported

    def test_artifact_source_gets_publisher_skeleton(self):
        # Artifact sources have no viewport meta (the publisher adds it), so a phone lays them out
        # at 980px. --artifact wraps the file first and removes the wrapper afterwards.
        src = self.page("art.html", '<style>p{font-size:18px}</style><button>EN|VI</button><p>Fits.</p>')
        self.assertEqual(run(src, self.tmp / "raw").returncode, 1)
        r = subprocess.run([sys.executable, "-X", "utf8", str(SHOT), str(src), "--artifact",
                            "--out", str(self.tmp / "wrapped")], capture_output=True, text=True, timeout=180)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in self.tmp.glob("*.html")), ["art.html"])

    def test_fitting_page_passes_with_screenshots(self):
        out = self.tmp / "out"
        r = run(self.page("good.html", GOOD), out)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        pngs = sorted(p.name for p in out.glob("*.png"))
        self.assertEqual(pngs, ["desktop.png", "phone-landscape.png", "phone.png"])
        self.assertTrue(all((out / n).stat().st_size > 1000 for n in pngs))


if __name__ == "__main__":
    unittest.main()
