#!/usr/bin/env bash
# Fetch HoldForBatch messages metadata for categorization
MSG_IDS=$(gws gmail users messages list --params '{"userId": "me", "q": "label:HoldForBatch", "maxResults": 100}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
ids = [m['id'] for m in data.get('messages', [])]
print('\n'.join(ids))
")

echo "Total messages: $(echo "$MSG_IDS" | wc -l)"
echo "---"

for mid in $MSG_IDS; do
  echo "MSGID:$mid"
  gws gmail users messages get --params "{\"userId\": \"me\", \"id\": \"$mid\", \"format\": \"metadata\"}" 2>/dev/null | python3 -c "
import sys, json, base64
msg = json.load(sys.stdin)
headers = {h['name']: h['value'] for h in msg['payload']['headers']}
print('  From: ' + headers.get('From','?'))
print('  Subject: ' + headers.get('Subject','?'))
print('  Date: ' + headers.get('Date','?'))
"
done
