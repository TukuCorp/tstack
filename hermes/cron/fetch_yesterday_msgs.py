"""Fetch metadata for yesterday's emails (excluding HoldForBatch labels)."""
import subprocess, json, sys, time

# Get all message IDs from yesterday
r1 = subprocess.run(
    ['gws', 'gmail', 'users', 'messages', 'list', '--params',
     json.dumps({"userId": "me", "q": "after:2026/07/15 before:2026/07/17 -label:HoldForBatch", "maxResults": 200})],
    capture_output=True, text=True, timeout=30
)
data = json.loads(r1.stdout)
msg_ids = [m['id'] for m in data.get('messages', [])]
print(f"Total messages from yesterday (excl HoldForBatch): {len(msg_ids)}", flush=True)

# Fetch metadata for each
for i, mid in enumerate(msg_ids, 1):
    r2 = subprocess.run(
        ['gws', 'gmail', 'users', 'messages', 'get', '--params',
         json.dumps({"userId": "me", "id": mid, "format": "metadata"})],
        capture_output=True, text=True, timeout=15
    )
    try:
        msg = json.loads(r2.stdout)
        h = {x['name']: x['value'] for x in msg['payload']['headers']}
        f = h.get('From', '?')
        s = h.get('Subject', '?')
        d = h.get('Date', '?')
        labels = msg.get('labelIds', [])
        print(f"{i}. ID:{mid} | From: {f} | Subject: {s} | Date: {d} | Labels: {labels}", flush=True)
    except Exception as e:
        print(f"{i}. ID:{mid} — ERROR: {e}", flush=True)
