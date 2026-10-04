#!/usr/bin/env python3
"""Return the next deterministic research brief path for a topic."""

from __future__ import annotations

import re
import sys
import unicodedata
from datetime import date
from pathlib import Path


STOP_WORDS = {
    "a",
    "an",
    "and",
    "before",
    "for",
    "from",
    "how",
    "in",
    "into",
    "of",
    "on",
    "or",
    "the",
    "to",
    "what",
    "why",
    "with",
}


def slugify_topic(topic: str) -> str:
    normalized = (
        unicodedata.normalize("NFKD", topic).encode("ascii", "ignore").decode("ascii")
    )
    words = re.findall(r"[a-z0-9]+", normalized.lower())
    filtered = [word for word in words if word not in STOP_WORDS]
    chosen = filtered[:4] or words[:4] or ["research-brief"]
    slug = "-".join(chosen)
    return slug[:80].strip("-") or "research-brief"


def next_path(topic: str, base_dir: Path) -> Path:
    research_dir = base_dir / "research"
    research_dir.mkdir(parents=True, exist_ok=True)

    stamp = date.today().isoformat()
    slug = slugify_topic(topic)
    candidate = research_dir / f"{stamp}_{slug}.md"
    counter = 2

    while candidate.exists():
        candidate = research_dir / f"{stamp}_{slug}-{counter}.md"
        counter += 1

    return candidate


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: next_research_path.py <topic>", file=sys.stderr)
        return 1

    topic = " ".join(sys.argv[1:]).strip()
    if not topic:
        print("Topic must not be empty", file=sys.stderr)
        return 1

    print(next_path(topic, Path.cwd()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
