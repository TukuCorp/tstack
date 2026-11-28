#!/usr/bin/env python3
"""hermes_worker.py - one Hermes Agent research worker for `/research --depth exhaustive`.

Runs `hermes -z <brief + output contract> -t web` once, so the worker searches agentically with
whatever web backend Hermes is configured with (Perplexity through the Nous Portal gateway when its
web backend is `nous`). Its candidate sources come back between BEGIN_SOURCES / END_SOURCES markers
as JSON lines; this script validates them and writes one JSONL file the lead merges with
`wide_pass.py --merge`. The worker's claims are hints, never evidence: the lead re-verifies.

Stdlib only. Typically launched by the lead as an hc child in its own Herdr tab:
  python -I hermes_worker.py --brief research/sources/<slug>.hermes-1.brief.md \
      --out research/sources/<slug>.hermes-1.jsonl --id hermes-1   # hc's exit note reports it; --notify <hc address> for a non-parent

Exit 0 when at least one valid row was written, 1 otherwise. The last stdout line is always
`HERMES_WORKER_DONE <id> rows=<n> status=<ok|empty|failed>`.
"""
import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

BUCKETS = ("github", "academia", "industry", "web")
_HTTP_URL = re.compile(r"^https?://[^\s/]+\.[^\s]+$")

CONTRACT = """

---
You are a research worker. Use web_search to find sources for the brief above, and web_extract
only to confirm what a page actually is. Search iteratively: follow leads, refine queries, and
prefer primary sources (official docs, specs, source repositories, original papers, government,
lab or standards-body reports) over commentary. Do not write a report.

Budget: at most {max_searches} web_search calls. When you reach it, stop searching and hand back what
you have; partial results with honest gaps beat looping.

When you are done, print a line BEGIN_SOURCES, then one JSON object per line, then a line
END_SOURCES. Print nothing else between the markers. Each source object has these keys:
{{"bucket": "github|academia|industry|web", "url": "...", "title": "...", "query": "the search query that found it", "claim": "one sentence: what this source supports for the brief", "quote": "the exact sentence from the page behind any number or key claim, copied verbatim, or empty"}}
For each part of the brief you could not answer from a primary source, add one line
{{"gap": "what is still missing"}}.

Rules: only URLs that appeared in your search results; never construct or guess a URL. Only quote
text you saw on the page; never paraphrase inside "quote". At most {max_rows} source objects. No duplicates.
"""


def parse_sources(text, wid, max_rows, gaps=None):
    """(rows, invalid_count) from a worker transcript. Rows are ledger-ready dicts.
    `{"gap": ...}` lines are appended to `gaps` (a list) when given, and never count as invalid."""
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == "BEGIN_SOURCES")
        end = next(i for i, ln in enumerate(lines) if i > start and ln.strip() == "END_SOURCES")
    except StopIteration:
        return [], 0
    rows, seen, invalid = [], set(), 0
    gaps = [] if gaps is None else gaps
    for ln in lines[start + 1:end]:
        ln = ln.strip()
        if not ln:
            continue
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError:
            invalid += 1
            continue
        if isinstance(obj, dict) and set(obj) == {"gap"}:
            if str(obj["gap"]).strip():
                gaps.append(str(obj["gap"]).strip()[:300])
            continue
        url = str(obj.get("url", "")).strip() if isinstance(obj, dict) else ""
        if not isinstance(obj, dict) or obj.get("bucket") not in BUCKETS or not _HTTP_URL.match(url):
            invalid += 1
            continue
        key = re.sub(r"^https?://(www\.)?", "", url.lower()).rstrip("/")
        if key in seen:
            invalid += 1
            continue
        seen.add(key)
        row = {"bucket": obj["bucket"], "url": url, "title": str(obj.get("title", ""))[:200],
               "discovered_via": f"{wid}: {str(obj.get('query', ''))[:160]}",
               "hint": str(obj.get("claim", ""))[:300]}
        if str(obj.get("quote", "")).strip():
            row["quote"] = str(obj["quote"]).strip()[:500]
        rows.append(row)
        if len(rows) >= max_rows:
            break
    return rows, invalid


def hermes_command(arg):
    if arg:
        return shlex.split(arg)
    exe = shutil.which("hermes")
    if not exe:
        raise SystemExit("hermes_worker: `hermes` not found on PATH (pass --hermes)")
    return [exe]


def notify(pane, message):
    try:
        subprocess.run(["hc", "send", pane, message], capture_output=True, timeout=90)
    except Exception as e:  # noqa: BLE001
        print(f"hermes_worker: notify failed: {e}", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brief", required=True, help="markdown brief written by the lead")
    ap.add_argument("--out", required=True, help="JSONL file this worker writes (overwritten)")
    ap.add_argument("--id", required=True, help="worker id, e.g. hermes-1")
    ap.add_argument("--notify", help="hc terminal address or name to `hc send` the done line to")
    ap.add_argument("--hermes", help="hermes command (default: `hermes` on PATH)")
    ap.add_argument("--toolsets", default="web")
    ap.add_argument("--max-rows", type=int, default=60)
    ap.add_argument("--max-searches", type=int, default=12, help="web_search budget given to the worker")
    ap.add_argument("--timeout", type=int, default=1800, help="seconds")
    ap.add_argument("--print-prompt", action="store_true", help="print the full prompt and exit")
    args = ap.parse_args()

    prompt = Path(args.brief).read_text(encoding="utf-8") + CONTRACT.format(
        max_rows=args.max_rows, max_searches=args.max_searches)
    if args.print_prompt:
        print(prompt)
        return 0
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = hermes_command(args.hermes) + ["-z", prompt, "-t", args.toolsets]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=args.timeout)
        transcript, code, err = p.stdout, p.returncode, p.stderr
    except subprocess.TimeoutExpired as e:
        transcript, code, err = (e.stdout or "") if isinstance(e.stdout, str) else "", None, "timeout"
    Path(str(out) + ".log").write_text(
        f"$ exit={code}\n--- stdout ---\n{transcript}\n--- stderr ---\n{err or ''}\n", encoding="utf-8")

    gaps = []
    rows, invalid = parse_sources(transcript, args.id, args.max_rows, gaps)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    Path(str(out) + ".gaps").write_text("".join(g + "\n" for g in gaps), encoding="utf-8")
    status = "failed" if code != 0 else ("ok" if rows else "empty")
    print(json.dumps({"id": args.id, "out": str(out), "rows": len(rows), "invalid": invalid,
                      "gaps": gaps, "hermes_exit": code, "log": str(out) + ".log"}, indent=2))
    done = f"HERMES_WORKER_DONE {args.id} rows={len(rows)} status={status}"
    print(done)
    if args.notify:
        notify(args.notify, f"{done}: candidate rows in {out}; merge with wide_pass.py --merge {out}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
