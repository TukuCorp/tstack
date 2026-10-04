# gws Drive Binary File Download Patterns

Used by CC Pipeline orchestrator and cron jobs that need to read or archive Drive files locally.

## Two download paths

Google Drive stores two fundamentally different file types:

| File type | Download method | Example |
|-----------|----------------|---------|
| **Google-native** (Docs, Sheets, Slides) | `files export` | `.docx`, `.pdf`, `.csv` |
| **Uploaded binary** (.docx, .xlsx, .pptx, PDF) | `files get` with `alt:media` | Word docs, Excel files |

## Uploaded binary files (.docx, .xlsx, .pptx)

These are NOT Google Docs — they were uploaded to Drive as binary files. The `-o` flag on `files get` returns metadata JSON by default, **not** the file content.

**Correct pattern — add `alt: media` to the params:**

```bash
gws drive files get \
  --params '{"fileId": "FILE_ID", "alt": "media"}' \
  -o "output_filename.docx"
```

**Without `alt:media`:** returns metadata only (id, name, mimeType)
**With `alt:media`:** returns `{"bytes": N, "mimeType": "...", "saved_file": "name.docx", "status": "success"}`

**Real example (SHP agreement download):**
```bash
cd C:\Users\tukum\AppData\Local\Temp && \
env -u GOOGLE_WORKSPACE_CLI_TOKEN gws drive files get \
  --params '{"fileId":"1rYZ2LQdvehfOPHl-1NFNDfbpKfLtS_OQ","alt":"media"}' \
  -o "agreement.docx"
# → 37451 bytes, valid Microsoft Word 2007+ file
```

**Verification:**
```bash
file agreement.docx   # Should say "Microsoft Word 2007+"
xxd agreement.docx | head -2  # Should start with "PK" (ZIP header)
```

## Google-native files (Docs, Sheets, Slides)

Must be **exported** — cannot use `alt:media`:

```bash
gws drive files export \
  --params '{"fileId": "DOC_ID", "mimeType": "text/plain"}' \
  -o "output.txt"
```

**Error if you try `alt:media` on a Google Doc:**
```json
{"error": {"code": 403, "message": "Only files with binary content can be downloaded. Use Export with Docs Editors files."}}
```

**Common export MIMEs:**
| Format | MIME |
|--------|------|
| Word | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` |
| PDF | `application/pdf` |
| Plain text | `text/plain` |
| Markdown | `text/markdown` |

## Pitfalls

**Pitfall — `mimeType` in `--params` does NOT trigger export:**
```bash
# WRONG — param is ignored by files.get
gws drive files get --params '{"fileId":"ID","mimeType":"text/plain"}'
# RIGHT
gws drive files export --params '{"fileId":"ID","mimeType":"text/plain"}'
```

**Pitfall — `-o` without `alt:media` on binary files:**
The saved file is metadata JSON, not the actual content. File size will be tiny (~200 bytes).

**Pitfall — MSYS `/tmp` path mismatch:** On Windows git-bash, `-o "/tmp/file.docx"` writes to `C:\tmp\` while bash's `/tmp` is `C:\Users\<user>\AppData\Local\Temp`. Use absolute Windows paths for clarity.

## Extracting comments and tracked changes from .docx

Once downloaded, python-docx + lxml can extract Word comments and tracked changes:

```python
from docx import Document
from lxml import etree

doc = Document("file.docx")
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

# Comments
for rel in doc.part.rels.values():
    if "comments" in rel.reltype.lower():
        root = etree.fromstring(rel.target_part.blob)
        for c in root.findall(".//w:comment", ns):
            w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            author = c.get(w + "author", "?")
            texts = c.findall(".//w:t", ns)
            text = "".join(t.text or "" for t in texts)
            print(f"{author}: {text}")

# Tracked changes
body = doc.element.body
for ins in body.findall(".//w:ins", ns):
    a = ins.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}author", "?")
    t = "".join((t.text or "") for t in ins.findall(".//w:t", ns))
    if t.strip(): print(f"+ {a}: {t}")
for d in body.findall(".//w:del", ns):
    t = "".join((t.text or "") for t in d.findall(".//w:delText", ns))
    if t.strip(): print(f"- {t}")
```

Requires `python-docx` (`pip install python-docx`).
