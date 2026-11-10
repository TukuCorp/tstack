# Force UTF-8 stdio on this Windows machine. Loaded even under `python -I`, which
# ignores PYTHONUTF8, so printing non-ASCII text no longer crashes on cp1252.
# Added 2026-11-11 by /reflect. Does not change open()'s default encoding.
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        if _stream is not None and (_stream.encoding or "").lower() not in ("utf-8", "utf8"):
            _stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    except (AttributeError, ValueError):
        pass
