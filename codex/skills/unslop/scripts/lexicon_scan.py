"""Scan a draft for phrases from references/ai-tells-lexicon.csv.

Usage: python -X utf8 lexicon_scan.py DRAFT [--lexicon CSV]

Prints one line per hit, sorted by position: line:col, severity, the matched
text, the lexicon subcategory and its suggested fix. High-severity hits are
marked FIX, the rest JUDGE. Exits 1 when any High hit is found, else 0.
Fenced code blocks and inline code are skipped. Quoted text and glossary terms
are not detected: the caller still judges each hit in context.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

DEFAULT_LEXICON = Path(__file__).resolve().parent.parent / "references" / "ai-tells-lexicon.csv"

# Rows that describe a shape rather than a phrase cannot be matched literally.
DESCRIPTIVE_CATEGORIES = {"Sentence structure", "Structure/Formatting"}
DESCRIPTIVE_MARKERS = ("(e.g.", " with no ", " repeats ", " across ", " after ", "removable", "callbacks", " | ")
# The lexicon's own "Use with care" regexes that fire on almost every document.
NOISY_REGEXES = {r"\bwhether\b.*\bor\b", r"\bfrom\b.*\bto\b"}

PLACEHOLDER = re.compile(r"\[[^\]]*\]")
NOTE = re.compile(r"\s*\((?:as |without |vague|abstract|literal)[^)]*\)")
NORMALIZE = str.maketrans({"‑": "-", "‐": "-", "–": "-", "’": "'", "‘": "'"})


def phrase_to_regex(example):
    """Turn a literal or [X]-template example into a regex, or None if unmatchable."""
    text = NOTE.sub("", example.translate(NORMALIZE)).strip().strip('"').strip()
    alternatives = [a.strip() for a in re.split(r"\s+/\s+", text) if a.strip()]
    patterns = []
    for alt in alternatives:
        parts = [p.strip(" ,:.") for p in PLACEHOLDER.split(alt)]
        # Leading and trailing placeholders add nothing to the match.
        while parts and not parts[0]:
            parts.pop(0)
        while parts and not parts[-1]:
            parts.pop()
        if not parts or len("".join(parts)) < 4:
            continue
        patterns.append(r"[^.\n]{1,80}?".join(map(_part_regex, parts)))
    return "|".join(f"(?:{p})" for p in patterns) or None


def _word_regex(word):
    # Light inflection so "embark" also catches "embarked" and "embarks".
    suffix = r"(?:s|es|d|ed|ing)?" if len(word) >= 4 and word.isalpha() else ""
    return re.escape(word) + suffix


def _part_regex(part):
    body = r"\s+".join(map(_word_regex, part.split()))
    lead = r"\b" if re.match(r"\w", part) else ""
    tail = r"\b" if re.search(r"\w$", part) else ""
    return lead + body + tail


def load_lexicon(path):
    entries = []
    with open(path, encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            example = row["Example (literal or template)"].strip()
            severity = row["Severity (High/Medium/Low)"].strip()
            fix = row["Human alternative / fix"].strip()
            if row["Subcategory"] == "Regex":
                if example in NOISY_REGEXES:
                    continue
                # Regex rows carry "use with care" as their fix; their "why" column says what they catch.
                pattern, severity, fix = example, "Medium", row["Why it reads as AI"].strip()
            elif row["Category"] in DESCRIPTIVE_CATEGORIES or any(m in example for m in DESCRIPTIVE_MARKERS):
                continue
            else:
                pattern = phrase_to_regex(example)
                if pattern is None:
                    continue
            entries.append((re.compile(pattern, re.IGNORECASE), severity, row["Subcategory"], fix))
    return entries


def mask_code(text):
    """Blank out fenced blocks and inline code, keeping line and column positions."""
    blank = lambda m: re.sub(r"[^\n]", " ", m.group(0))
    text = re.sub(r"^(```|~~~).*?^\1[^\n]*$", blank, text, flags=re.M | re.S)
    return re.sub(r"`[^`\n]+`", blank, text)


def scan(text, entries):
    text = mask_code(text.translate(NORMALIZE))
    hits = []
    for regex, severity, subcategory, fix in entries:
        for m in regex.finditer(text):
            hits.append((m.start(), m.end(), severity, subcategory, fix, m.group(0)))
    # Keep the longest hit when several cover the same span.
    hits.sort(key=lambda h: (h[0], -(h[1] - h[0])))
    kept, last_end = [], -1
    for hit in hits:
        if hit[1] <= last_end:
            continue
        kept.append(hit)
        last_end = max(last_end, hit[1])
    lines = []
    for start, _end, severity, subcategory, fix, matched in kept:
        line = text.count("\n", 0, start) + 1
        col = start - (text.rfind("\n", 0, start) + 1) + 1
        action = "FIX" if severity == "High" else "JUDGE"
        lines.append(f'{line}:{col} {action} {severity} "{" ".join(matched.split())}" ({subcategory}) fix: {fix}')
    return lines, any(h[2] == "High" for h in kept)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("draft")
    ap.add_argument("--lexicon", default=str(DEFAULT_LEXICON))
    args = ap.parse_args()
    text = Path(args.draft).read_text(encoding="utf-8")
    lines, has_high = scan(text, load_lexicon(args.lexicon))
    print("\n".join(lines) if lines else "no lexicon hits")
    return 1 if has_high else 0


if __name__ == "__main__":
    sys.exit(main())
