#!/usr/bin/env python3
# Adapted from warpdotdev/common-skills skill-doctor (MIT, Copyright (c) 2026 Denver Technologies, Inc.)
"""Render a reflect report.json into one self-contained HTML report.

Output (next to report.json):
  report.html - scorecard, findings, and suggested skill edits in a single
                page with inline CSS. No scripts, no external resources.

Python 3.9+, stdlib only. Every string from report.json is HTML-escaped
(it may contain transcript-derived text); URLs are only ever rendered as text.
"""

import argparse
import html
import json
import math
import re
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path

GRADES = [(0.9, "A"), (0.8, "B"), (0.7, "C"), (0.6, "D"), (0.0, "F")]

METRICS = [
    ("efficiency", "Efficiency"),
    ("code_quality", "Code Quality"),
    ("procedure_compliance", "Procedure Compliance"),
    ("verbosity", "Verbosity"),
    ("skill_coverage", "Skill Coverage"),
]

STATS = [
    ("sessions_analyzed", "sessions analyzed"),
    ("sessions_scanned", "sessions scanned"),
    ("skills_found", "skills found"),
    ("skills_used", "skills used"),
    ("window_days", "window (days)"),
]

# Diffs longer than this many lines are collapsed behind <details>.
DIFF_COLLAPSE_LINES = 25


def as_score(value):
    """A 0-1 float, or None when the value is missing or not a usable number."""
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        return None
    try:
        score = float(value)
    except ValueError:
        return None
    return None if math.isnan(score) else min(1.0, max(0.0, score))


def as_dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def as_list(value) -> list:
    if isinstance(value, list):
        return value
    return [value] if isinstance(value, str) and value else []


def grade_for(score: float) -> str:
    for threshold, letter in GRADES:
        if score >= threshold:
            return letter
    return "F"


def format_generated_at(value) -> str:
    if not value:
        return ""
    raw = str(value)
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    if re.search(r"[+-]\d{2}$", normalized):
        normalized += ":00"
    try:
        generated_at = datetime.fromisoformat(normalized)
    except ValueError:
        return raw
    suffix = ""
    if generated_at.tzinfo is not None:
        generated_at = generated_at.astimezone(timezone.utc)
        suffix = " UTC"
    time = generated_at.strftime("%I:%M %p").lstrip("0")
    return (
        f"{generated_at.strftime('%B')} {generated_at.day}, "
        f"{generated_at.year} at {time}{suffix}"
    )


def open_report(report_path: Path) -> bool:
    try:
        return bool(webbrowser.open(report_path.absolute().as_uri(), new=2))
    except (OSError, webbrowser.Error):
        return False


def esc(v) -> str:
    value = v if v is not None else ""
    return html.escape(str(value))


def render_diff(diff_text) -> str:
    if not isinstance(diff_text, str) or not diff_text.strip():
        return ""
    lines = diff_text.splitlines()
    in_hunk = False
    spans = []
    for line in lines:
        # ---/+++ file headers only exist before the first hunk; afterwards a
        # line starting with "---" is a deleted line that begins with "--".
        if line.startswith("@@"):
            in_hunk = True
            kind = "hunk"
        elif not in_hunk and line.startswith(("--- ", "+++ ", "diff ", "index ")):
            kind = "meta"
        elif line.startswith("+"):
            kind = "add"
        elif line.startswith("-"):
            kind = "del"
        else:
            kind = ""
        spans.append(f'<span class="{kind}">{esc(line)}</span>' if kind else esc(line))
    pre = f'<pre class="diff">{chr(10).join(spans)}</pre>'
    if len(lines) <= DIFF_COLLAPSE_LINES:
        return pre
    return f"<details><summary>Show diff ({len(lines)} lines)</summary>{pre}</details>"


# Restrained palette; light by default, dark via prefers-color-scheme.
PAGE_CSS = """
:root {
  --bg: #fafaf8; --surface: #ffffff; --panel: #f1f0ec;
  --fg: #1c1b1a; --muted: #5f5c57; --line: #dedbd4; --accent: #2f5d8a;
  --add-fg: #1a6b34; --add-bg: #e3f4e8; --del-fg: #a02a2a; --del-bg: #fbe6e6;
  --font: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #151514; --surface: #1d1d1b; --panel: #262624;
    --fg: #ecebe7; --muted: #aaa7a0; --line: #3a3935; --accent: #7fb0e0;
    --add-fg: #7fd69a; --add-bg: #1c3324; --del-fg: #f09090; --del-bg: #3a2020;
    color-scheme: dark;
  }
}
* { box-sizing: border-box; }
body {
  font-family: var(--font); font-size: 15px; line-height: 1.6;
  background: var(--bg); color: var(--fg);
  max-width: 880px; margin: 0 auto; padding: 32px 16px 64px;
  overflow-wrap: anywhere;
}
h1 { font-size: 28px; line-height: 1.2; margin: 0 0 4px; }
h2 { font-size: 18px; margin: 36px 0 10px; }
p { margin: 0; }
code { font-family: var(--mono); font-size: 0.9em; background: var(--panel); padding: 1px 5px; border-radius: 3px; }
li { margin-bottom: 14px; }
.muted { color: var(--muted); font-size: 13px; }
.mode-note { margin-top: 10px; padding: 8px 12px; background: var(--panel);
  border-left: 3px solid var(--accent); font-size: 14px; }
.scorecard { display: flex; align-items: center; gap: 32px; margin-top: 20px; padding: 22px;
  background: var(--surface); border: 1px solid var(--line); border-radius: 8px; }
.grade-col { text-align: center; flex: none; width: 130px; }
.grade { font-size: 80px; font-weight: 700; line-height: 1; color: var(--accent); }
.grade-label { font-size: 13px; color: var(--muted); margin-top: 6px; }
.bars { flex: 1; display: flex; flex-direction: column; gap: 14px; min-width: 0; }
.bar-head { display: flex; justify-content: space-between; gap: 12px; font-size: 14px; margin-bottom: 4px; }
.bar-val { font-variant-numeric: tabular-nums; color: var(--muted); }
.bar-track { height: 8px; background: var(--panel); border-radius: 4px; overflow: hidden; }
.bar-fill { height: 100%; background: var(--accent); }
.stats { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
.stat { flex: 1 1 130px; background: var(--surface); border: 1px solid var(--line);
  border-radius: 8px; padding: 12px 16px; }
.stat .num { font-size: 24px; font-weight: 600; font-variant-numeric: tabular-nums; }
.stat .lbl { font-size: 12px; color: var(--muted); }
pre.diff { margin: 8px 0 0; padding: 10px 12px; background: var(--panel); border: 1px solid var(--line);
  border-radius: 6px; font-family: var(--mono); font-size: 12.5px; line-height: 1.5;
  overflow-x: auto; white-space: pre; overflow-wrap: normal; }
pre.diff .add { color: var(--add-fg); background: var(--add-bg); }
pre.diff .del { color: var(--del-fg); background: var(--del-bg); }
pre.diff .hunk { color: var(--accent); }
pre.diff .meta { color: var(--muted); }
details { margin-top: 8px; }
summary { cursor: pointer; color: var(--accent); font-size: 13px; }
@media (max-width: 560px) {
  .scorecard { flex-direction: column; align-items: stretch; gap: 20px; padding: 18px 16px; }
  .grade-col { width: auto; }
  h1 { font-size: 24px; }
}
"""


def render_scorecard(scores) -> str:
    overall = as_score(scores.get("overall"))
    grade = grade_for(overall) if overall is not None else "&ndash;"
    label = f"overall {overall:.2f}" if overall is not None else "overall n/a"
    bars = []
    for key, name in METRICS:
        val = as_score(scores.get(key))
        shown = f"{val:.2f} ({grade_for(val)})" if val is not None else "n/a"
        width = round(val * 100) if val is not None else 0
        bars.append(
            f'<div class="bar-row"><div class="bar-head"><span>{esc(name)}</span>'
            f'<span class="bar-val">{shown}</span></div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{width}%"></div></div></div>'
        )
    return (
        '<div class="scorecard">'
        f'<div class="grade-col"><div class="grade">{grade}</div>'
        f'<div class="grade-label">{label}</div></div>'
        f'<div class="bars">{"".join(bars)}</div></div>'
    )


def render_suggestion(s) -> str:
    s = as_dict(s)
    if not s:
        return ""
    evidence = (
        f'<div class="muted">Evidence: {esc(s["evidence"])}</div>' if s.get("evidence") else ""
    )
    path = f'<div class="muted">Proposed file: <code>{esc(s["proposed_path"])}</code></div>' if s.get("proposed_path") else ""
    return (
        f'<li><b><code>{esc(s.get("skill"))}</code></b> &mdash; {esc(s.get("change"))}'
        f'{evidence}{path}{render_diff(s.get("diff"))}</li>'
    )


def render_page(r) -> str:
    r = as_dict(r)
    scores = as_dict(r.get("scores"))
    stats = as_dict(r.get("stats"))
    title = r.get("title") or "Agent Skill Report"
    generated_at = format_generated_at(r.get("generated_at"))

    meta = " &middot; ".join(
        part for part in [
            f"Generated {esc(generated_at)}" if generated_at else "",
            f"harness: {esc(r['harness'])}" if r.get("harness") else "",
            esc(r["handle"]) if r.get("handle") else "",
        ] if part
    )
    mode_note = f'<p class="mode-note">{esc(r["mode_note"])}</p>' if r.get("mode_note") else ""
    stat_cells = "".join(
        f'<div class="stat"><div class="num">{esc(stats[key]) if stats.get(key) is not None else "&ndash;"}</div>'
        f'<div class="lbl">{esc(label)}</div></div>'
        for key, label in STATS
    )
    findings = "".join(f"<li>{esc(f)}</li>" for f in as_list(r.get("top_findings")))
    suggestions = "".join(render_suggestion(s) for s in as_list(r.get("suggestions"))) \
        or "<li>No skill change cleared the bar for this window.</li>"

    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{esc(title)}</title>
<style>{PAGE_CSS}</style></head><body>
<header><h1>{esc(title)}</h1>
<p class="muted">{meta}</p>{mode_note}</header>
<main>
{render_scorecard(scores)}
<div class="stats">{stat_cells}</div>
<h2>Findings</h2><ul>{findings}</ul>
<h2>Suggested skill changes</h2><ol>{suggestions}</ol>
</main>
</body></html>"""


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report_path",
        nargs="?",
        default="./report.json",
        help="Path to the report.json file",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="Open the generated report in the default browser",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    report_path = Path(args.report_path).expanduser()
    if not report_path.exists():
        print(f"error: {report_path} not found", file=sys.stderr)
        sys.exit(1)
    try:
        r = json.loads(report_path.read_text(encoding="utf-8"))
    except ValueError as e:
        print(f"error: {report_path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    out_path = report_path.parent / "report.html"
    out_path.write_text(render_page(r), encoding="utf-8")
    print(f"report: {out_path.absolute().as_uri()}")
    if args.open_browser:
        if open_report(out_path):
            print("        opened in the default browser")
        else:
            print(
                "warning: could not open the report in the default browser",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
