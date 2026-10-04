#!/usr/bin/env python3
import json, subprocess, sys, re
from datetime import datetime

# On Windows, use the .cmd shim so subprocess can find it
import os, platform
if platform.system() == "Windows":
    gws_cmd = "gws.cmd"
else:
    gws_cmd = "gws"

message_ids = [
    "19f24d9722937b88", "19f24102d7c0c4ed", "19f23231f3bd23d5", "19f2323018a8b420",
    "19f22e9b542e58e5", "19f22e9a529b07cb", "19f22daa31b0c1fa", "19f22da9baf8a579",
    "19f22c3bbd37d7f8", "19f22c3aa04e6c8d", "19f22adf9bfb3b55", "19f22adf30a18b88",
    "19f225c3af5dabf4", "19f2257aab177a82", "19f22578ec812aba", "19f22153da2536e1",
    "19f220b62368e98b", "19f220b56dfa5029", "19f220b401cc5c2a", "19f21da7d2d9a8e2"
]

results = []
for i, mid in enumerate(message_ids):
    params = json.dumps({"userId": "me", "id": mid, "format": "metadata"})
    cmd = [gws_cmd, "gmail", "users", "messages", "get",
           "--params", params, "--format", "json"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if out.returncode == 0:
            msg = json.loads(out.stdout)
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            results.append({
                "id": mid,
                "threadId": msg.get("threadId", ""),
                "from": headers.get("From", ""),
                "subject": headers.get("Subject", ""),
                "date": headers.get("Date", ""),
            })
        else:
            results.append({"id": mid, "error": out.stderr[:200]})
    except Exception as e:
        results.append({"id": mid, "error": str(e)})
    if (i+1) % 5 == 0:
        print(f"Fetched {i+1}/{len(message_ids)}", file=sys.stderr)

good = [r for r in results if "error" not in r]
print(f"Success: {len(good)}", file=sys.stderr)

if not good:
    # Show first 3 errors for debugging
    bad = [r for r in results if "error" in r]
    for e in bad[:3]:
        print(f"  {e['id']}: {e.get('error','')[:200]}", file=sys.stderr)
    sys.exit(1)

months = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
          "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

def parse_email_date(date_str):
    m = re.search(r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})', date_str)
    if m:
        day, mon, year, hour, minute, sec = int(m.group(1)), months[m.group(2)], int(m.group(3)), int(m.group(4)), int(m.group(5)), int(m.group(6))
        return datetime(year, mon, day, hour, minute, sec)
    return datetime.min

good.sort(key=lambda r: parse_email_date(r.get("date", "")), reverse=True)

summary = {
    "total_estimate": 201,
    "retrieved": len(good),
    "messages": good[:15]
}
print(json.dumps(summary, indent=2))
