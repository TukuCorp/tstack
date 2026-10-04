# Gmail & Drive Operations from Cron Jobs (via gws CLI)

When a cron-triggered Hermes agent needs to interact with Gmail or Drive,
it typically uses the `gws` CLI (not the `google_api.py` wrapper, whose
token may be expired). The `gws` CLI uses its own encrypted credential
store at `~/.config/gws/` and authenticates as the work account
(e.g. `<EMAIL>`).

## Env-var guard

Always strip the `GOOGLE_WORKSPACE_CLI_TOKEN` env var that Hermes injects,
or gws will use the wrong credentials:

```bash
env -u GOOGLE_WORKSPACE_CLI_TOKEN gws <command>
```

## Gmail: List messages by label

```bash
# By label ID (found via `gmail users labels list`)
gws gmail users messages list \
  --params '{"userId":"me","labelIds":["Label_4922299671175567648"],"maxResults":50}'

# By label name (Gmail search syntax)
gws gmail users messages list \
  --params '{"userId":"me","q":"label:HoldForBatch","maxResults":50}'
```

The `resultSizeEstimate` field gives the total count (may exceed `maxResults`).

## Gmail: Get message details

```python
import subprocess, json
gws = r"C:\Users\tukum\AppData\Roaming\npm\gws.cmd"
result = subprocess.run(
    [gws, "gmail", "users", "messages", "get", "--params",
     json.dumps({"userId": "me", "id": mid, "format": "full"})],
    capture_output=True, text=True,
    env={k:v for k,v in os.environ.items() if k != "GOOGLE_WORKSPACE_CLI_TOKEN"}
)
md = json.loads(result.stdout)
headers = {h["name"]: h["value"] for h in md.get("payload", {}).get("headers", [])}
snippet = md.get("snippet", "")
```

Format options: `full` (headers + body + snippet), `metadata` (headers only + labelIds), `minimal` (id + threadId + labelIds), `raw` (base64url-encoded RFC2822).

## Gmail: Trash messages

```bash
gws gmail users messages trash \
  --params '{"userId":"me","id":"MESSAGE_ID"}'
```

Batch trash by looping — the API has no batch endpoint for this. Rate-limit
to ~5 requests per second.

## Gmail: Create a draft

1. Build an RFC2822 message string
2. Base64url-encode it (no padding)
3. POST via `drafts create --json`

```python
import base64, subprocess, json

msg = f"""From: Tung Ho <<EMAIL>>
To: Recipient Name <email@example.com>
Subject: Your subject line
Content-Type: text/plain; charset=utf-8

Dear Recipient,

Body text here.

Best,
Tung"""

msg_b64 = base64.urlsafe_b64encode(msg.encode("utf-8")).decode("utf-8")

result = subprocess.run(
    [gws, "gmail", "users", "drafts", "create", "--params",
     json.dumps({"userId": "me"}),
     "--json", json.dumps({"message": {"raw": msg_b64}})],
    capture_output=True, text=True, env=env
)
# Response: {"id": "r-12345...", "message": {...}}
```

The draft lands in the Gmail Drafts folder, unsent. The `From:` address
must match an authenticated account on the gws profile.

## Gmail: Multi-step batch classify + trash pattern

Used by the HoldForBatch cleanup cron job:

1. Fetch all messages with `q="label:HoldForBatch"`
2. For each, get sender + subject (from headers)
3. Classify using string matching — the patterns to look for:

| Pattern | Classification | Action |
|---------|---------------|--------|
| `firecrawl` in sender | Automated alert | Trash |
| `<EMAIL>` + `CI` in subject | GitHub CI notice | Trash |
| `comments-noreply` in sender | Google Docs/Slides comment notification | Trash |
| `pwc.com` + `cbam` in subject | External marketing | Trash |
| `voiz.academy`, `esgbook.com`, `alliedoffsets`, `contactus@` in sender | Marketing blast | Trash |
| Team members (`tah`, `hal`, `lem`, `mds`, `jrh`, `mmr`, `httt`, `ceb`, etc.) | Real work | Keep |
| Partners/clients (`@ceba.org`, `@cpiglobal.org`, etc.) | Real work | Keep |

4. Keep all `Keep` items; `Trash` via `messages trash`
5. Report: "HoldForBatch cleanup: X trashed, Y kept"

## Drive: List files with search

```bash
gws drive files list \
  --params '{"q":"name contains '\''LUPA'\''","orderBy":"modifiedTime desc","pageSize":20,"fields":"files(id,name,modifiedTime,owners,mimeType,webViewLink)"}'
```

Common field selections for efficiency:
- `files(id,name,modifiedTime)` — minimal listing
- `files(id,name,modifiedTime,owners,webViewLink,mimeType)` — full metadata
- `files(id,name,modifiedTime,owners,webViewLink,mimeType,parents)` — with parent folder

## Drive: Download binary files (.docx, .pptx, .xlsx)

Native Google file types (Docs, Sheets, Slides) need `files export`. Binary
uploaded files (.docx, .pptx, .xlsx, .pdf) need `files get` with `alt:media`:

```bash
gws drive files get \
  --params '{"fileId":"FILE_ID","alt":"media"}' \
  -o "output.docx"
```

The response confirms with `bytes`, `mimeType`, `saved_file`. The file is
written to disk at the `-o` path.

**Pitfall — missing `alt:media`:** Without `alt:media`, `files get` returns
only metadata (ID, name, mimeType) regardless of `-o`. The file is not
downloaded.

## Drive: Read Google Doc content (Docs API)

For Google Docs (not .docx uploads), use the Docs API:

```bash
gws docs documents get \
  --params '{"documentId":"DOC_ID","fields":"body.content"}'
```

The response contains structured JSON with paragraphs → elements → textRun.
Extract plain text with:

```python
text_parts = []
for item in content.get("body", {}).get("content", []):
    para = item.get("paragraph")
    if para:
        for elem in para.get("elements", []):
            run = elem.get("textRun")
            if run:
                text_parts.append(run.get("content", ""))
full_text = "".join(text_parts)
```

## Drive: Export Google Doc as plain text

```bash
gws drive files get \
  --params '{"fileId":"DOC_ID","mimeType":"text/plain"}' \
  -o "output.txt"
```

For Google Docs, use `mimeType` to export. For binary files, use `alt:media`.

## Auth health check

```bash
# Check token validity, scopes, and authenticated user
gws auth status

# Expected (healthy):
#   token_valid: true
#   has_refresh_token: true
#   user: <EMAIL>
#   scope_count: 12 (includes drive, gmail.modify, sheets, docs)

# Export credentials for programmatic use
gws auth export
# Returns {client_id, client_secret, refresh_token, type}
```

## gws subprocess from Python (execute_code / cron agent)

```python
import subprocess, json, os

gws = r"C:\Users\tukum\AppData\Roaming\npm\gws.cmd"
env = os.environ.copy()
env.pop("GOOGLE_WORKSPACE_CLI_TOKEN", None)

result = subprocess.run(
    [gws, "drive", "files", "list", "--params",
     json.dumps({"q": "name contains 'test'", "pageSize": 10})],
    capture_output=True, text=True, env=env, timeout=15
)
data = json.loads(result.stdout)
```

Note: `shell=True` or `gws.cmd` — both work. The `.cmd` extension is needed
for direct `CreateProcess` resolution in subprocess on Windows; `shell=True`
resolves via PATH.
