"""Screenshot a page on phone, phone-landscape and desktop, and flag layout that falls off-screen.

    python -X utf8 shot.py <url-or-html-file> [--out DIR] [--presets phone,phone-landscape,desktop] [--full]

Uses agent-browser real device emulation (mobile UA, device-width viewport), not a narrow desktop
window: a narrow window reflows, a phone zooms out, so off-screen controls only show up here.
Per preset it saves <out>/<preset>.png and prints one line: OK, or the problems found
(horizontal overflow, visible controls outside the screen). Exit 1 if any preset has problems.
Look at the PNGs too: the report catches overflow, not ugliness.
For a claude.ai artifact, pass the local source file with --artifact (the live URL needs a login,
and the source lacks the doctype/viewport skeleton the publisher adds).
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PRESETS = {  # name -> (screen width in CSS px, agent-browser `set` commands)
    "phone": (393, [["device", "iPhone 15"]]),
    "phone-landscape": (852, [["device", "iPhone 15"], ["viewport", "852", "393", "3"]]),
    "android": (412, [["device", "Pixel 9"]]),
    "desktop": (1440, [["viewport", "1440", "900"]]),
}
DEFAULT = "phone,phone-landscape,desktop"
SKELETON = '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n'

# __W__ is the preset's screen width. A phone widens innerWidth to fit overflowing content,
# so measuring against innerWidth alone would hide the bug.
PROBE = r"""JSON.stringify((() => {
  const vw = Math.min(innerWidth, __W__);
  const sw = document.documentElement.scrollWidth;
  const sel = 'a[href],button,input,select,textarea,[role=button],[role=tab],[onclick]';
  const off = [];
  for (const el of document.querySelectorAll(sel)) {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    if (cs.display === 'none' || cs.visibility === 'hidden' || r.width === 0 || r.height === 0) continue;
    if (r.right > vw + 1 || r.left < -1 || r.bottom < 0) {
      const label = (el.innerText || el.value || el.getAttribute('aria-label') || el.tagName).trim().slice(0, 30);
      off.push(`${el.tagName.toLowerCase()} "${label}" (${Math.round(r.left)}..${Math.round(r.right)}px)`);
    }
  }
  return {vw, sw, off};
})())"""


def ab(session, *args):
    r = subprocess.run(["agent-browser", "--session", session, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60, shell=(os.name == "nt"))
    if r.returncode != 0:
        raise RuntimeError(f"agent-browser {' '.join(args)}: {(r.stderr or r.stdout).strip()}")
    return r.stdout


def to_url(target):
    p = Path(target)
    return p.resolve().as_uri() if p.exists() else target


def shoot(url, preset, out, full):
    session = f"shot-{os.getpid()}-{preset}"
    try:
        width, cmds = PRESETS[preset]
        for cmd in cmds:
            ab(session, "set", *cmd)
        ab(session, "open", url)
        ab(session, "wait", "500")
        png = out / f"{preset}.png"
        ab(session, "screenshot", str(png), *(["--full"] if full else []))
        probe = base64.b64encode(PROBE.replace("__W__", str(width)).encode()).decode()  # -b: no shell quoting
        res = json.loads(json.loads(ab(session, "--json", "eval", "-b", probe))["data"]["result"])
    finally:
        subprocess.run(["agent-browser", "--session", session, "close"], capture_output=True,
                       shell=(os.name == "nt"))
    problems = []
    if res["sw"] > res["vw"] + 1:
        problems.append(f"horizontal overflow {res['sw']}px > {res['vw']}px screen")
    if res["off"]:
        problems.append("off-screen: " + "; ".join(res["off"][:8]))
    return res["vw"], png, problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("target", help="URL or local HTML file")
    ap.add_argument("--out", help="output folder (default: a new temp folder)")
    ap.add_argument("--presets", default=DEFAULT, help=f"comma list from {', '.join(PRESETS)}")
    ap.add_argument("--full", action="store_true", help="full-page screenshots")
    ap.add_argument("--artifact", action="store_true",
                    help="local artifact source: wrap it in the publisher's doctype + viewport skeleton")
    a = ap.parse_args(argv)
    out = Path(a.out) if a.out else Path(tempfile.mkdtemp(prefix="shot-"))
    out.mkdir(parents=True, exist_ok=True)
    wrapped = None
    if a.artifact:  # next to the source, so relative assets still resolve; removed below
        src = Path(a.target)
        wrapped = src.with_name(f".shot-{os.getpid()}.html")
        wrapped.write_text(SKELETON + src.read_text(encoding="utf-8"), encoding="utf-8")
    url, failed = to_url(str(wrapped or a.target)), False
    try:
        for preset in a.presets.split(","):
            vw, png, problems = shoot(url, preset.strip(), out, a.full)
            failed |= bool(problems)
            print(f"{preset} ({vw}px): {'; '.join(problems) if problems else 'OK'} -> {png}")
    finally:
        if wrapped:
            wrapped.unlink(missing_ok=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
