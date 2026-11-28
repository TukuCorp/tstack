"""Tests for design.py and gates.py. Run: python -X utf8 -m pytest -q scripts/test_design.py

The gates e2e test drives a real browser through agent-browser and needs the network for axe-core;
it skips (with the reason) when agent-browser is not installed.
"""
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import design  # noqa: E402
import gates  # noqa: E402

CLEAN = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Invoices</title>
<meta name="design-axis" content="density: dense table">
<style>body{margin:0;font:15px/1.5 system-ui;color:#1c1c1a;background:#fff}main{padding:16px;max-width:960px;margin:auto}
table{width:100%;border-collapse:collapse}td,th{padding:6px 8px;border-bottom:1px solid #ddd;text-align:left}
.dev{position:fixed;right:8px;bottom:8px;font-size:12px}</style></head>
<body><main><h1>Invoices due this week</h1><table><thead><tr><th>Client</th><th>Amount</th></tr></thead>
<tbody><tr><td>Northwind Solar</td><td>$12,400</td></tr><tr><td>Bac Ninh Wind</td><td>$8,150</td></tr></tbody></table>
</main><div class="dev" data-design-dev><label>State <select><option>Demo</option><option>Empty</option></select></label></div>
</body></html>"""

SLOPPY = """<!doctype html><html><head><style>
.hero{background:linear-gradient(135deg,#6366f1,#8b5cf6)}
.a{border-radius:24px}.b{border-radius:20px}.c{border-radius:1.5rem}.d{border-radius:16px}
</style></head><body><div class="hero rounded-2xl"><h1>Welcome to Acme</h1>
<button>🚀 Get started</button><p>Lorem ipsum dolor sit amet</p></div></body></html>"""


def make_run(tmp_path, opts):
    design.main(["new", "--slug", "invoices", "--brief", "Invoices due page", "--root", str(tmp_path)])
    run = tmp_path / ".design" / "invoices"
    for name, html in opts.items():
        (run / "options" / name).mkdir(parents=True)
        (run / "options" / name / "index.html").write_text(html, encoding="utf-8")
    return run


def test_slop_lint_flags_ai_defaults_and_passes_clean_html():
    bad = gates.slop(SLOPPY)
    assert bad["status"] == "fail"
    for name in ("purple-gradient", "filler-content", "emoji-icons", "big-radius-everywhere"):
        assert name in bad["detail"], name
    assert gates.slop(CLEAN) == {"status": "pass", "detail": ""}


def test_slop_lint_ignores_pill_radius_and_google_fonts():
    html = CLEAN.replace("<style>", '<link href="https://fonts.googleapis.com/css2?family=Inter" rel="stylesheet"><style>'
                         ".p{border-radius:9999px}.q{border-radius:999px}.r{border-radius:50%}")
    assert gates.slop(html)["status"] == "pass"


# One snippet per "vibecoded" tell catalogued by slopstrap.mikelacher.com (read 2026-11-28).
VIBECODED = {
    "gradient-text": ".h{background:linear-gradient(90deg,#fff,#0ea5e9);-webkit-background-clip:text;background-clip:text}",
    "accent-left-border": ".a{border-left:4px solid #0ea5e9}.b{border-left:4px solid #10b981}.c{border-left: 4px solid #f59e0b}",
    "serif-accent-word": "</style><h1>Build the <em class=\"serif\">future</em> of work</h1><style>",
    "font-trio": "@import url(https://fonts.googleapis.com/css2?family=Inter&family=Instrument+Serif&family=JetBrains+Mono);",
    "ambient-orbs": ".orb{position:absolute;filter:blur(80px);background:#0ea5e9}",
    "grid-bg": ".bg{background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),"
               "linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px)}",
    "conic-beam": ".beam{background:conic-gradient(from 0deg,#0ea5e9,#10b981);animation:spin 4s linear infinite}"
                  "@keyframes spin{to{transform:rotate(360deg)}}",
    "logo-marquee": ".logos{animation:m 30s linear infinite}@keyframes m{from{transform:translateX(0)}to{transform:translateX(-50%)}}",
    "pulse-dot": ".dot{animation:pulse 2s infinite}@keyframes pulse{50%{opacity:.4}}",
    "count-up": "</style><script>new IntersectionObserver(e=>countUp(e)).observe(stat)</script><style>",
    "fake-terminal": ".r{background:#ff5f56}.y{background:#ffbd2e}.g{background:#27c93f}",
    "hype-badge": "</style><span class=\"badge\">AI-POWERED</span><span>All Systems Operational</span><style>",
}


@pytest.mark.parametrize("name", sorted(VIBECODED))
def test_slop_lint_flags_vibecoded_tells(name):
    result = gates.slop(CLEAN.replace("<style>", "<style>" + VIBECODED[name]))
    assert name in result["detail"], result
    assert result["status"] == ("fail" if name == "conic-beam" else "warn")


def test_picker_embeds_every_option_and_escapes_script_end(tmp_path):
    run = make_run(tmp_path, {"dense-table": CLEAN, "editorial": CLEAN.replace("</body>", "<script>1</script></body>")})
    (run / "gates.json").write_text(json.dumps({"dense-table": {"status": "pass", "checks": {}}}), encoding="utf-8")
    out, n = design.build_picker(run)
    page = out.read_text(encoding="utf-8")
    assert n == 2
    blob = page.split('<script type="application/json" id="data">')[1].split("</script>")[0]
    data = json.loads(blob.replace("<\\/", "</"))
    assert [o["name"] for o in data["options"]] == ["dense-table", "editorial"]
    assert data["options"][0]["axis"] == "density: dense table"
    assert data["options"][0]["gates"]["status"] == "pass"
    assert "__DATA__" not in page and "__TITLE__" not in page


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_serve_records_send_and_wait_returns_it(tmp_path):
    run = make_run(tmp_path, {"dense-table": CLEAN})
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-X", "utf8", str(HERE / "design.py"), "serve", str(run), "--port", str(port),
                            "--no-open"], stdout=subprocess.PIPE, text=True, encoding="utf-8")
    try:
        assert json.loads(srv.stdout.readline())["type"] == "ready"
        page = urllib.request.urlopen(f"http://127.0.0.1:{port}/?v=dense-table", timeout=10).read().decode()
        assert "dense-table" in page
        req = urllib.request.Request(f"http://127.0.0.1:{port}/send", method="POST",
                                     data=json.dumps({"line": "mash dense-table", "base": "dense-table"}).encode(),
                                     headers={"Content-Type": "application/json"})
        assert json.loads(urllib.request.urlopen(req, timeout=10).read())["seq"] == 1
        event = json.loads(srv.stdout.readline())
        assert event["type"] == "send" and event["base"] == "dense-table"
        w = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "design.py"), "wait", str(run), "--after", "0",
                            "--timeout", "5"], capture_output=True, text=True, encoding="utf-8")
        assert w.returncode == 0 and json.loads(w.stdout)["seq"] == 1
        w = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "design.py"), "wait", str(run), "--after", "1",
                            "--timeout", "1"], capture_output=True, text=True, encoding="utf-8")
        assert w.returncode == 3
    finally:
        srv.terminate()
        srv.wait(10)


def test_new_refuses_existing_run_and_bad_slug(tmp_path):
    make_run(tmp_path, {})
    with pytest.raises(SystemExit):
        design.main(["new", "--slug", "invoices", "--brief", "again", "--root", str(tmp_path)])
    with pytest.raises(SystemExit):
        design.main(["new", "--slug", "Bad Slug", "--brief", "x", "--root", str(tmp_path)])


@pytest.mark.skipif(not shutil.which("agent-browser"), reason="agent-browser not installed")
def test_gates_e2e_clean_passes_sloppy_fails(tmp_path):
    run = make_run(tmp_path, {"clean": CLEAN, "sloppy": SLOPPY})
    t = time.time()
    code = gates.main([str(run)])
    res = json.loads((run / "gates.json").read_text(encoding="utf-8"))
    assert code == 1
    assert res["sloppy"]["status"] == "fail"
    assert res["clean"]["checks"]["slop"]["status"] == "pass"
    assert res["clean"]["checks"]["layout"]["status"] == "pass", res["clean"]["checks"]["layout"]
    assert res["clean"]["checks"]["a11y"]["status"] in ("pass", "skipped"), res["clean"]["checks"]["a11y"]
    assert res["sloppy"]["checks"]["a11y"]["status"] in ("fail", "skipped")
    assert (run / "shots" / "clean" / "phone.png").exists()
    assert time.time() - t < 240
