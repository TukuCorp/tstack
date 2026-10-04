# gws CLI JSON Params Quoting on Windows/MSYS

The `gws drive files list --params` command requires a JSON string with **literal double quotes** inside the `q` field (around datetime values). MSYS/git-bash consistently mangles nested double quotes, causing `Invalid --params JSON` errors.

## Auth Triage: gws vs Hermes google_api.py

This user has two Google accounts:
- **Work** (<EMAIL>) → use `gws` CLI with `env -u GOOGLE_WORKSPACE_CLI_TOKEN`
- **Personal** (<EMAIL>) → use `google_api.py` (Hermes token)

**Rule:** For work queries (project names, CPI, VIDA, Allotrope), always use `gws` directly. The Hermes `google_token.json` may be expired or absent. Check with:

```bash
# Check if gws auth is valid
env -u GOOGLE_WORKSPACE_CLI_TOKEN gws drive files list --params '{"pageSize": 1}' --format json

# Check Hermes token
test -f ~/.hermes/google_token.json && echo "exists" || echo "missing"
```

If the query is work-related and gws responds, use gws. Fall back to google_api.py only for personal queries.

## The Problem

```bash
# ❌ Fails — MSYS bash strips/mangles the inner quotes
gws drive files list --params '{\"pageSize\": 20, \"q\": \"modifiedTime >= \\\"2026-07-01T00:00:00\\\"\"}' --format json
# Error: Invalid --params JSON: expected `,` or `}` at line 1 column 73

# ❌ Also fails — printf doesn't help
printf '{\"q\": \"modifiedTime >= \\\"...\\\"\"}' | gws ...

# ❌ Also fails — python inline subprocess can't find gws (PATH not inherited)
python -c \"import subprocess; subprocess.run(['gws', ...])\"
# FileNotFoundError: [WinError 2] The system cannot find the file specified
```

## Quick-fix: `'\''` escape for simple queries (no temp file needed)

When the `q` value contains **single-quoted** literals (like `modifiedTime > '2026-06-20'`), bash single quotes surrounding `--params` are terminated by the inner single quotes. The general shell trick—end the quote, insert an escaped literal quote, resume the quote—works in git-bash:

```bash
# ✅ Works for simple queries — '\'' embeds a literal single quote inside a single-quoted string
gws drive files list --params '{"q": "fullText contains '\''lupa'\'' and modifiedTime > '\''2026-06-20T14:00:00Z'\''", "orderBy": "modifiedTime desc", "pageSize": 10}'
```

This avoids writing a temp file for one-off searches. Use it when the query has single-quoted string literals inside the `q` field. For query strings with only double-quoted values (e.g. `name contains \"report\"`), no escape is needed.

### The `'\''` pattern explained

The `--params` value is wrapped in outer single quotes so the shell doesn't expand `$` or `{` inside JSON. A literal single quote inside that string would close the outer quotes prematurely. The fix:

| What you type | What the shell sees |
|---|---|
| `'...\''...'` | `...'...` (one string with an embedded `'`) |

Breakdown: `'...'` (quoted segment) → `\'` (escaped literal single quote — the backslash before it exits the quote context) → `'...'` (resume quoting).

Always test with `echo` first if unsure:
```bash
echo '{"q": "modifiedTime > '\''2026-06-20'\''"}'
# → {"q": "modifiedTime > '2026-06-20'"}
```

## The Fix: Write JSON to a File

Use `execute_code` (Python) or `write_file` to write the exact JSON to a temp file with single quotes around the string values (no backslash escaping needed at the Python level for the inner double quotes — Python's `json.dump` handles it):

```python
from hermes_tools import terminal
import json

params = {
    "pageSize": 20,
    "orderBy": "modifiedTime desc",
    "q": 'modifiedTime >= "2026-07-01T00:00:00" and modifiedTime < "2026-07-02T00:00:00"'
}
with open("C:/Users/tukum/AppData/Local/hermes/tmp/drive_query.json", "w") as f:
    json.dump(params, f)

# Then reference it via shell
r = terminal('gws drive files list --params "$(cat /c/Users/tukum/AppData/Local/hermes/tmp/drive_query.json)" --format json 2>&1', timeout=30)
```

Key points:
- `write_file` also works to create the JSON file (just ensure the containing literal `"` around datetime values)
- Always reference the file via `$(cat /c/.../file.json)` in the `--params` argument
- The `/c/...` (MSYS-style) path works for the `cat` command even though it's inside a bash terminal call
- `timeout=30` is safe — Drive queries rarely take more than a few seconds

## Why Python subprocess Fails (and the `gws.cmd` workaround)

`gws` at `/c/Users/tukum/AppData/Roaming/npm/gws` is a Node.js executable (no `.exe` extension). It's added to the MSYS/bash PATH but Python's `subprocess` inherits the **Windows** PATH, not the bash/MSYS PATH. So `subprocess.run(['gws', ...])` throws `FileNotFoundError` even though `which gws` works in terminal.

Always call `gws` from `terminal()` (bash context), not from `execute_code()` (Python context).

**Unless you use `gws.cmd`:** The npm install also creates `gws.cmd` in the same directory — a native Windows batch file that re-invokes node properly. This CAN be called from `execute_code()` (Python subprocess) because Windows `.cmd` files are valid Win32 executables via `CreateProcess`:

```python
import subprocess, json

gws_path = r"C:\Users\tukum\AppData\Roaming\npm\gws.cmd"
# ✅ Works from Python subprocess
result = subprocess.run(
    [gws_path, "drive", "files", "list", "--params", json.dumps({...})],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
```

This is useful for complex multi-query workflows where shell quoting becomes unmanageable. The trade-off: you lose the `$HOME` and PATH context from bash — use absolute paths or `os.path.expanduser('~')`.

## Also: Batch Gmail Metadata Fetch

When fetching metadata from multiple Gmail messages (e.g., for a daily brief), use a bash for-loop from `terminal()` rather than calling gws per message from Python:

```bash
for id in ID1 ID2 ID3; do
  gws gmail users messages get \
    --params "{\"userId\": \"me\", \"id\": \"$id\", \"format\": \"metadata\"}" \
    --format json 2>/dev/null | \
    python -c "import sys,json; d=json.load(sys.stdin); h={x['name']:x['value'] for x in d.get('payload',{}).get('headers',[])}; print(json.dumps({'id':d['id'],'from':h.get('From',''),'subject':h.get('Subject',''),'date':h.get('Date','')}))"
done
```

Note: `gws gmail get` accepts inline params with escaped quotes via bash — the quoting issue is specific to `drive files list` with complex `q` strings.

## Also: Gmail Message Body Extraction (full-text)

When you need the email body text (not just metadata headers), fetch with `format: "full"` and decode the base64 body. Messages with attachments or multipart content store the plaintext in `payload.parts[]`:

```python
import base64, json

def get_message_body(gws_raw_json: dict) -> str:
    """Extract plaintext body from a gws 'messages get' response."""
    def _extract(part):
        if part.get("mimeType") == "text/plain":
            bdata = part.get("body", {}).get("data", "")
            if bdata:
                return base64.urlsafe_b64decode(bdata).decode("utf-8", errors="replace")
        for sub in part.get("parts", []):
            result = _extract(sub)
            if result:
                return result
        return ""

    payload = gws_raw_json.get("payload", {})
    body = _extract(payload)
    if not body:
        bdata = payload.get("body", {}).get("data", "")
        if bdata:
            body = base64.urlsafe_b64decode(bdata).decode("utf-8", errors="replace")
    return body or ""

# Usage:
# result = gws_call("gmail", "users", "messages", "get", "--params",
#     json.dumps({"userId": "me", "id": msg_id, "format": "full"}))
# body = get_message_body(json.loads(result))
```
