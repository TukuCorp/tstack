#!/usr/bin/env python3
"""fact_guard.py - check that a rewrite kept the facts of the original.

Usage: python -X utf8 fact_guard.py <before.md> <after.md>

Compares numbers (with $, %, K/M/B), ISO dates, URLs, `code spans` and footnote markers [^n]
as multisets. Prints each one the rewrite dropped ("missing") or introduced ("added").
Exit 0 when nothing drifted, 1 otherwise. Wording, names and order are free to change.
"""
import re
import sys
from collections import Counter

KINDS = ("number", "url", "code", "footref")
URL = re.compile(r"https?://[^\s)\]>\"']+")
CODE = re.compile(r"`[^`\n]+`")
FOOTREF = re.compile(r"\[\^[^\]\s]+\]")
DATE = re.compile(r"(?<![\w.])\d{4}-\d{2}-\d{2}(?![\w])")
NUMBER = re.compile(r"(?<![\w.])\$?\d[\d,]*(?:\.\d+)?(?:%|[KMB]\b)?")


def facts(text):
    found = {k: Counter() for k in KINDS}
    for kind, pat in (("url", URL), ("code", CODE), ("footref", FOOTREF)):
        for m in pat.findall(text):
            found[kind][m.rstrip(".,;:") if kind == "url" else m] += 1
        text = pat.sub(" ", text)
    for m in DATE.findall(text):
        found["number"][m] += 1
    text = DATE.sub(" ", text)
    for m in NUMBER.findall(text):
        found["number"][m.rstrip(",")] += 1
    return found


def main(before_path, after_path):
    read = lambda p: open(p, encoding="utf-8").read()
    before, after = facts(read(before_path)), facts(read(after_path))
    lines = []
    for label, a, b in (("missing", before, after), ("added", after, before)):
        for kind in KINDS:
            for token in a[kind]:
                if a[kind][token] > b[kind][token]:
                    lines.append(f"{label:<8} {kind:<8} {token}")
    if not lines:
        print("no fact drift")
        return 0
    print("\n".join(lines))
    print(f"{len(lines)} drift(s): restore missing facts, cut added ones unless the source supports them")
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1], sys.argv[2]))
