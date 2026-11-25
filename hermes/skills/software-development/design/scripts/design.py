"""/design run helper. Plain Python 3.10+, no dependencies.

    design.py new --slug S --brief "one line" [--root DIR]   create .design/<slug>/ and print its path
    design.py status [RUN]                                  list runs (or one run's options, gates, picks)
    design.py picker RUN [--out FILE]                       build RUN/picker.html from options/*/index.html
    design.py serve RUN [--port N] [--detach] [--no-open]   serve the picker; append each Send to picks.jsonl
                                                            and print it as one JSON line (monitor this process)
    design.py wait RUN [--after N] [--timeout S]            block until a Send with seq > N, print it (exit 3 on timeout)
    design.py stop RUN                                      stop a detached server

RUN is a run folder (.design/<slug>) or just its slug when run from the project root.
"""
import argparse
import html
import json
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "picker.html"
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,47}$")
AXIS = re.compile(r'<meta\s+name=["\']design-axis["\']\s+content=["\']([^"\']*)["\']', re.I)
lock = threading.Lock()


def run_dir(arg):
    p = Path(arg)
    if not p.is_dir() and (Path(".design") / arg).is_dir():
        p = Path(".design") / arg
    if not (p / "brief.md").exists():
        sys.exit(f"design: {arg} is not a run folder (no brief.md)")
    return p.resolve()


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def cmd_new(a):
    if not SLUG.match(a.slug):
        sys.exit("design: slug must be lowercase kebab-case, at most 48 chars")
    run = Path(a.root) / ".design" / a.slug
    if (run / "brief.md").exists():
        sys.exit(f"design: {run} already exists; resume it or pick another slug")
    for sub in ("refs", "options", "briefs", "logs", "shots"):
        (run / sub).mkdir(parents=True, exist_ok=True)
    (run / "brief.md").write_text(
        f"# Brief: {a.brief}\n\nDate: {date.today()}\n\n## Goal and audience\n\n## Surface and size\n\n"
        "## Real content\n\n## Taste rules that apply\n\n## Contract\n- Hierarchy:\n- Density:\n- Controls:\n"
        "- States: empty, loading, error\n- Patterns to reject:\n\n## References\n\n"
        "## Rubric (hidden from generators)\n1.\n", encoding="utf-8", newline="\n")
    print(run.resolve())


def options(run):
    out = []
    for f in sorted((run / "options").glob("*/index.html")):
        text = f.read_text(encoding="utf-8", errors="replace")
        m = AXIS.search(text)
        out.append({"name": f.parent.name, "axis": m.group(1) if m else "", "html": text})
    return out


def cmd_status(a):
    if not a.run:
        for b in sorted(Path(".design").glob("*/brief.md")):
            print(f"{b.parent.name}: {b.read_text(encoding='utf-8').splitlines()[0][9:]}")
        return
    run = run_dir(a.run)
    gates, scores = read_json(run / "gates.json", {}), read_json(run / "scores.json", {})
    for o in options(run):
        g = gates.get(o["name"], {}).get("status", "not run")
        print(f"{o['name']:<24} axis={o['axis'] or '?':<18} gates={g:<8} scored={'yes' if o['name'] in scores else 'no'}")
    picks = (run / "picks.jsonl")
    print(f"picks: {len(picks.read_text(encoding='utf-8').splitlines()) if picks.exists() else 0}")


def build_picker(run, out=None):
    opts = options(run)
    if not opts:
        sys.exit(f"design: no options/*/index.html in {run}")
    gates, scores = read_json(run / "gates.json", {}), read_json(run / "scores.json", {})
    title = (run / "brief.md").read_text(encoding="utf-8").splitlines()[0].removeprefix("# Brief: ")
    data = {"slug": run.name, "title": title,
            "options": [dict(o, gates=gates.get(o["name"]), scores=scores.get(o["name"])) for o in opts]}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("__TITLE__", html.escape(title)).replace("__DATA__", blob)
    out = Path(out) if out else run / "picker.html"
    out.write_text(page, encoding="utf-8", newline="\n")
    return out, len(opts)


def cmd_picker(a):
    out, n = build_picker(run_dir(a.run), a.out)
    print(f"{out} ({n} options)")


def next_seq(picks):
    if not picks.exists():
        return 1
    lines = [ln for ln in picks.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return (json.loads(lines[-1]).get("seq", len(lines)) + 1) if lines else 1


def make_handler(run):
    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):  # stdout carries only Send lines (the monitor reads it)
            pass

        def do_GET(self):
            if self.path.split("?")[0] not in ("/", "/picker.html"):
                self.send_error(404)
                return
            build_picker(run)  # rebuilt per load, so a refresh shows new options
            body = (run / "picker.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path != "/send":
                self.send_error(404)
                return
            try:
                pick = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            except ValueError:
                self.send_error(400)
                return
            with lock:
                picks = run / "picks.jsonl"
                event = {"type": "send", "seq": next_seq(picks), "at": time.strftime("%Y-%m-%dT%H:%M:%S"), **pick}
                with picks.open("a", encoding="utf-8", newline="\n") as f:
                    f.write(json.dumps(event, ensure_ascii=False) + "\n")
            print(json.dumps(event, ensure_ascii=False), flush=True)
            body = json.dumps({"ok": True, "seq": event["seq"]}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
    return H


def cmd_serve(a):
    run = run_dir(a.run)
    if a.detach:
        args = [sys.executable, "-X", "utf8", str(Path(__file__).resolve()), "serve", str(run), "--no-open"]
        if a.port:
            args += ["--port", str(a.port)]
        flags = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        (run / "logs").mkdir(exist_ok=True)
        (run / "server.json").unlink(missing_ok=True)  # so the poll below sees only the new server
        log = open(run / "logs" / "serve.log", "a", encoding="utf-8")
        subprocess.Popen(args, stdout=log, stderr=log, stdin=subprocess.DEVNULL, creationflags=flags,
                         start_new_session=(os.name != "nt"))
        for _ in range(50):
            info = read_json(run / "server.json", None)
            if info:
                print(info["url"])
                return
            time.sleep(0.1)
        sys.exit("design: detached server did not start; see logs/serve.log")
    srv = ThreadingHTTPServer(("127.0.0.1", a.port or 0), make_handler(run))
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    (run / "server.json").write_text(json.dumps({"url": url, "pid": os.getpid()}), encoding="utf-8")
    print(json.dumps({"type": "ready", "url": url}), flush=True)
    if not a.no_open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    finally:
        (run / "server.json").unlink(missing_ok=True)


def cmd_wait(a):
    run = run_dir(a.run)
    picks, end = run / "picks.jsonl", time.time() + a.timeout
    while time.time() < end:
        if picks.exists():
            for ln in picks.read_text(encoding="utf-8").splitlines():
                if ln.strip() and json.loads(ln).get("seq", 0) > a.after:
                    print(ln)
                    return 0
        time.sleep(0.5)
    return 3


def cmd_stop(a):
    run = run_dir(a.run)
    info = read_json(run / "server.json", None)
    if not info:
        print("no server running")
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(info["pid"]), "/F"], capture_output=True)
    else:
        os.kill(info["pid"], 15)
    (run / "server.json").unlink(missing_ok=True)
    print(f"stopped {info['url']}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("--slug", required=True); p.add_argument("--brief", required=True)
    p.add_argument("--root", default=".")
    p = sub.add_parser("status"); p.add_argument("run", nargs="?")
    p = sub.add_parser("picker"); p.add_argument("run"); p.add_argument("--out")
    p = sub.add_parser("serve"); p.add_argument("run"); p.add_argument("--port", type=int)
    p.add_argument("--detach", action="store_true"); p.add_argument("--no-open", action="store_true")
    p = sub.add_parser("wait"); p.add_argument("run"); p.add_argument("--after", type=int, default=0)
    p.add_argument("--timeout", type=float, default=480)
    p = sub.add_parser("stop"); p.add_argument("run")
    a = ap.parse_args(argv)
    return {"new": cmd_new, "status": cmd_status, "picker": cmd_picker, "serve": cmd_serve,
            "wait": cmd_wait, "stop": cmd_stop}[a.cmd](a) or 0


if __name__ == "__main__":
    sys.exit(main())
