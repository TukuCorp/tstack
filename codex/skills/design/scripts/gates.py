"""Gate every option of a /design run: slop lint, layout (overflow on phone + desktop), a11y (axe-core).

    python -X utf8 gates.py <run> [--only NAME] [--skip layout,a11y] [--surface web|slides|doc]

Writes <run>/gates.json ({option: {status, checks: {slop|layout|a11y: {status, detail}}}}) and
<run>/shots/<option>/*.png. Exit 1 if any option fails. Statuses: pass, warn, fail, skipped.
A check that cannot run (no agent-browser, no network for axe) is "skipped", never "pass".
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
AXE = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.2/axe.min.js"
PURPLE = r"(#6366f1|#4f46e5|#8b5cf6|#7c3aed|#a855f7|#9333ea|#c084fc|indigo|violet|purple)"
# (name, regex, level, fix). Count-based rules are in slop() below.
SLOP = [
    ("purple-gradient", re.compile(r"gradient\([^;{}]*" + PURPLE + r"|\b(from|via|to)-(indigo|violet|purple)-\d", re.I),
     "fail", "one brand hue from the contract, flat fill"),
    ("filler-content", re.compile(r"lorem ipsum|\bAcme\b|John Doe|Jane Doe|placeholder\.com|via\.placeholder|picsum\.photos", re.I),
     "fail", "real content from the brief"),
    ("emoji-icons", re.compile(r"<(h[1-6]|button|li)\b[^>]*>\s*[\U0001F300-\U0001FAFF☀-➿]"),
     "fail", "inline SVG icons or plain text"),
    ("glass-panels", re.compile(r"backdrop-filter\s*:\s*blur", re.I), "warn", "solid surfaces; blur only for overlays"),
    ("external-assets", re.compile(r"<(script|link|img)\b[^>]*(src|href)=[\"']https?://(?!fonts\.(googleapis|gstatic)\.com)", re.I),
     "fail", "inline it; options must be self-contained"),
]
BIG_RADIUS = re.compile(r"border-radius\s*:\s*(\d+(?:\.\d+)?)(px|rem)", re.I)
TW_RADIUS = re.compile(r"\brounded-(2xl|3xl)\b")
SHADOW = re.compile(r"box-shadow\s*:\s*([^;}\"]+)", re.I)
DEV_TOGGLE = re.compile(r"data-design-dev")
BOX_PROBE = r"""JSON.stringify([...document.querySelectorAll('.slide,.page')].map((s,i)=>{
  const r=s.getBoundingClientRect(); let bad=0;
  for (const el of s.querySelectorAll('*')) { const e=el.getBoundingClientRect();
    if (e.width && (e.right>r.right+1 || e.bottom>r.bottom+1)) bad++; }
  return bad ? `${s.className} ${i+1}: ${bad} elements overflow` : '';
}).filter(Boolean))"""
AXE_PROBE = """(async()=>{await new Promise((res,rej)=>{const s=document.createElement('script');s.src='%s';
s.onload=res;s.onerror=()=>rej(new Error('axe load failed'));document.head.appendChild(s)});
const r=await axe.run(document,{resultTypes:['violations']});
return JSON.stringify(r.violations.filter(v=>['serious','critical'].includes(v.impact))
  .map(v=>v.id+' ('+v.impact+', '+v.nodes.length+')'))})()""" % AXE


def slop(text):
    hits = []
    for name, rx, level, fix in SLOP:
        if rx.search(text):
            hits.append((level, f"{name} -> {fix}"))
    big = [m for m in BIG_RADIUS.finditer(text)
           if 16 <= float(m.group(1)) * (16 if m.group(2).lower() == "rem" else 1) < 999]
    if len(big) >= 4 or len(TW_RADIUS.findall(text)) >= 3:
        hits.append(("fail", "big-radius-everywhere -> one radius scale applied by role"))
    shadows = {s.strip().lower() for s in SHADOW.findall(text) if s.strip().lower() != "none"}
    if len(shadows) >= 5:
        hits.append(("warn", f"shadow-everything ({len(shadows)} distinct) -> elevation only where layering is real"))
    if not DEV_TOGGLE.search(text):
        hits.append(("warn", "no data-design-dev state toggle (Demo/Empty/One/Many/Long text)"))
    status = "fail" if any(l == "fail" for l, _ in hits) else "warn" if hits else "pass"
    return {"status": status, "detail": "; ".join(h for _, h in hits)}


def ab(session, *args, timeout=90):
    r = subprocess.run(["agent-browser", "--session", session, *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout, shell=(os.name == "nt"))
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout).strip()[:300])
    return r.stdout


def ab_eval(session, js):
    out = ab(session, "--json", "eval", "-b", base64.b64encode(js.encode()).decode())
    return json.loads(json.loads(out)["data"]["result"])


def layout(html_file, out, surface, retried=False):
    if surface != "web":
        session = f"gates-{os.getpid()}-box"
        try:
            ab(session, "set", "viewport", "2000", "1200")
            ab(session, "open", html_file.resolve().as_uri())
            ab(session, "wait", "400")
            ab(session, "screenshot", str(out / "box.png"), "--full")
            bad = ab_eval(session, BOX_PROBE)
        except Exception as e:  # noqa: BLE001 - report, never pass silently
            return {"status": "skipped", "detail": f"agent-browser: {e}"}
        finally:
            subprocess.run(["agent-browser", "--session", session, "close"], capture_output=True, shell=(os.name == "nt"))
        return {"status": "fail" if bad else "pass", "detail": "; ".join(bad[:6])}
    r = subprocess.run([sys.executable, "-X", "utf8", str(HERE / "shot.py"), str(html_file), "--out", str(out),
                        "--presets", "phone,desktop"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    lines = [ln for ln in r.stdout.splitlines() if "->" in ln]
    if (r.returncode not in (0, 1) or not lines) and not retried:  # daemon cold-start timeout: retry once
        return layout(html_file, out, surface, retried=True)
    if r.returncode not in (0, 1) or not lines:
        return {"status": "skipped", "detail": (r.stderr or r.stdout).strip()[-300:]}
    bad = [ln.split(" -> ")[0] for ln in lines if not ln.split(" -> ")[0].endswith(": OK")]
    return {"status": "fail" if bad else "pass", "detail": "; ".join(bad)}


def a11y(html_file):
    # One retry: the first eval after a cold browser start sometimes drops the connection (eval run 2026-11-25).
    res = _a11y(html_file)
    return _a11y(html_file) if res["status"] == "skipped" else res


def _a11y(html_file):
    session = f"gates-{os.getpid()}-axe"
    try:
        ab(session, "open", html_file.resolve().as_uri())
        ab(session, "wait", "300")
        bad = ab_eval(session, AXE_PROBE)
    except Exception as e:  # noqa: BLE001
        return {"status": "skipped", "detail": f"axe: {e}"}
    finally:
        subprocess.run(["agent-browser", "--session", session, "close"], capture_output=True, shell=(os.name == "nt"))
    return {"status": "fail" if bad else "pass", "detail": "; ".join(bad[:8])}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("run")
    ap.add_argument("--only")
    ap.add_argument("--skip", default="", help="comma list of layout,a11y")
    ap.add_argument("--surface", choices=["web", "slides", "doc"], default="web")
    a = ap.parse_args(argv)
    run = Path(a.run)
    if not (run / "options").is_dir():
        sys.exit(f"gates: {run} has no options/ folder")
    skip = {s.strip() for s in a.skip.split(",") if s.strip()}
    gates_file = run / "gates.json"
    try:
        results = json.loads(gates_file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        results = {}
    files = sorted((run / "options").glob("*/index.html"))
    if a.only:
        files = [f for f in files if f.parent.name == a.only]
    if not files:
        sys.exit("gates: no options to check")
    failed = False
    for f in files:
        name, out = f.parent.name, run / "shots" / f.parent.name
        out.mkdir(parents=True, exist_ok=True)
        checks = {"slop": slop(f.read_text(encoding="utf-8", errors="replace"))}
        checks["layout"] = {"status": "skipped", "detail": "--skip"} if "layout" in skip else layout(f, out, a.surface)
        checks["a11y"] = {"status": "skipped", "detail": "--skip"} if "a11y" in skip else a11y(f)
        st = [c["status"] for c in checks.values()]
        status = "fail" if "fail" in st else "warn" if ("warn" in st or "skipped" in st) else "pass"
        failed |= status == "fail"
        results[name] = {"status": status, "checks": checks}
        print(f"{name}: {status}  " + "  ".join(f"{k}={v['status']}" + (f" ({v['detail']})" if v["detail"] else "")
                                               for k, v in checks.items()))
    gates_file.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
