#!/usr/bin/env python3
"""lane_rows.py - source rows from an agentic research lane for `/research --depth exhaustive`.

The lead gives each necro lane one sub-question plus the source-row contract below; the lane writes
its candidate sources between BEGIN_SOURCES / END_SOURCES markers in its output file. This script
validates that block and writes one JSONL file the lead merges with `wide_pass.py --merge`. A lane's
claims are hints, never evidence: the lead re-verifies.

  python -I lane_rows.py --print-contract [--max-searches 12] [--max-rows 60]   # text for the lane brief
  python -I lane_rows.py --parse research/sources/<slug>.rs1.md --out research/sources/<slug>.rs1.jsonl --id rs1

`--parse` also writes `<out>.gaps` (one line per `{"gap": ...}` the lane listed). Exit 0 when at least
one valid row was written, 1 otherwise. The last stdout line is always
`LANE_ROWS_DONE <id> rows=<n> status=<ok|empty>`. Stdlib only.
"""
import argparse
import json
import re
import sys
from pathlib import Path

BUCKETS = ("github", "academia", "industry", "web")
_HTTP_URL = re.compile(r"^https?://[^\s/]+\.[^\s]+$")

CONTRACT = """You are a research worker. Use your web search tool to find sources for your sub-question, and
page fetches only to confirm what a page actually is. Search iteratively: follow leads, refine queries,
and prefer primary sources (official docs, specs, source repositories, original papers, government,
lab or standards-body reports) over commentary. Do not write a report.

Budget: at most {max_searches} web searches. When you reach it, stop searching and hand back what
you have; partial results with honest gaps beat looping.

When you are done, write into your output file a line BEGIN_SOURCES, then one JSON object per line,
then a line END_SOURCES. Put nothing else between the markers. Each source object has these keys:
{{"bucket": "github|academia|industry|web", "url": "...", "title": "...", "query": "the search query that found it", "claim": "one sentence: what this source supports for the brief", "quote": "the exact sentence from the page behind any number or key claim, copied verbatim, or empty"}}
For each part of the sub-question you could not answer from a primary source, add one line
{{"gap": "what is still missing"}}.

Rules: only URLs that appeared in your search results; never construct or guess a URL. Only quote
text you saw on the page; never paraphrase inside "quote". At most {max_rows} source objects. No duplicates.
"""


def parse_sources(text, wid, max_rows, gaps=None):
    """(rows, invalid_count) from a lane file. Rows are ledger-ready dicts.
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print-contract", action="store_true", help="print the source-row contract and exit")
    ap.add_argument("--parse", help="lane output file holding a BEGIN_SOURCES block")
    ap.add_argument("--out", help="JSONL file to write (overwritten)")
    ap.add_argument("--id", help="lane id, e.g. rs1")
    ap.add_argument("--max-rows", type=int, default=60)
    ap.add_argument("--max-searches", type=int, default=12, help="web search budget stated in the contract")
    args = ap.parse_args()

    if args.print_contract:
        print(CONTRACT.format(max_rows=args.max_rows, max_searches=args.max_searches))
        return 0
    if not (args.parse and args.out and args.id):
        ap.error("--parse, --out and --id are required (or use --print-contract)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    gaps = []
    rows, invalid = parse_sources(Path(args.parse).read_text(encoding="utf-8", errors="replace"),
                                  args.id, args.max_rows, gaps)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    Path(str(out) + ".gaps").write_text("".join(g + "\n" for g in gaps), encoding="utf-8")
    status = "ok" if rows else "empty"
    print(json.dumps({"id": args.id, "out": str(out), "rows": len(rows), "invalid": invalid, "gaps": gaps},
                     indent=2))
    print(f"LANE_ROWS_DONE {args.id} rows={len(rows)} status={status}")
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
