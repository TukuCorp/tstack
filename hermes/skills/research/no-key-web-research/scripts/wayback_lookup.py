"""Discover exact URLs on bot-blocked sites via Wayback CDX, then optionally fetch the newest snapshot.

Run with the Hermes venv python (requests available):
  C:/Users/tukum/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe wayback_lookup.py "<url-pattern>" [limit] [--fetch]

Examples:
  wayback_lookup.py "thuvienphapluat.vn/van-ban/Bao-hiem/Nghi-dinh-158-2025*" 5
  wayback_lookup.py "thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-40-2021*" 3 --fetch

Notes:
- `*` wildcards work in the URL path.
- collapse=urlkey dedupes snapshots; pick statuscode 200.
- requests auto-decompresses gzip, so fetched content is clean text (unlike curl, which needs --compressed).
"""
import sys, re
import requests

CDX = "http://web.archive.org/cdx/search/cdx"


def cdx_lookup(pattern, limit=5):
    params = {
        "url": pattern, "output": "text", "collapse": "urlkey",
        "limit": limit, "fl": "original,timestamp,statuscode",
    }
    r = requests.get(CDX, params=params, timeout=40)
    r.raise_for_status()
    rows = []
    for line in r.text.strip().splitlines():
        parts = line.split()
        if len(parts) >= 3:
            rows.append({"original": parts[0], "timestamp": parts[1], "status": parts[2]})
    return rows


def fetch_snapshot(original, ts):
    return requests.get(f"https://web.archive.org/web/{ts}id_/{original}", timeout=90)


def html_to_text(html):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", html, flags=re.S)
    t = re.sub(r"<[^>]+>", "\n", t)
    return "\n".join(l.strip() for l in t.splitlines() if l.strip())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    pattern = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 5
    rows = cdx_lookup(pattern, limit)
    if not rows:
        print("NO SNAPSHOTS FOUND for:", pattern)
        sys.exit(1)
    for row in rows:
        print(f"{row['status']} {row['timestamp']} {row['original']}")
    if "--fetch" in sys.argv:
        best = rows[0]  # newest after collapse ordering
        r = fetch_snapshot(best["original"], best["timestamp"])
        print(f"\nFetched {best['timestamp']} -> HTTP {r.status_code}, {len(r.text)} chars")
        print(html_to_text(r.text)[:600])
