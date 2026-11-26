"""Post evidence-anchored comments for /officeaudit comments.

- Google Docs (`kind: "docs"`): uses the Docs API `documents.batchUpdate` `insertComment` request
  by default (`"anchored": true`), which creates real range-anchored (`kix.*`) comments pinned to
  the exact UTF-16 text range in the Docs editor (and triggers `@email` notifications).
  Set `"anchored": false` on a comment to fall back to the unanchored Drive API.
- Drive-hosted `.docx` in Office editing mode (`kind: "docx"`): validates every quote against the
  live `.docx` XML (skipping `<w:del>`, flagging `<w:txbxContent>`, checking `word/comments.xml`
  for existing threads/duplicates), then posts anchored comments via guarded `browse` UI automation
  (`Ctrl+F` -> `Escape` -> `Ctrl+Alt+M` -> assert `.docos-input-textarea` visible before typing).
- Google Sheets, Slides, and other Drive files: uses the Drive API (`drive comments create`).
  Because Drive API comments often show unanchored in the editors, every body must name its target:
  `Sheet!A1` for Sheets, `slide N` for Slides, or page/section for other files.

Spec file (JSON):
  {"fileId": "...", "kind": "sheets|slides|docs|docx|file", "authuser": "optional@email",
   "comments": [{"location": "Inputs!C12", "quote": "exact text", "context": "optional nearby text",
                 "occurrence": 1, "tabId": "optional", "assignee": "optional@email",
                 "anchored": true, "body": "..."}],
   "replies":  [{"commentId": "...", "body": "...", "resolve": false}]}

Usage: python -X utf8 post_comments.py spec.json                  # dry run: validate + plan
       python -X utf8 post_comments.py spec.json --live           # dry run + live .docx XML check
       python -X utf8 post_comments.py spec.json --emit-js out.js # also write guarded browse JS (docx)
       python -X utf8 post_comments.py spec.json --post           # send, skip duplicates, verify
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

MAX_BATCH = 25
GWS_NATIVE = Path(os.environ.get("APPDATA", "")) / "npm/node_modules/@googleworkspace/cli/bin/gws.exe"
VAGUE = re.compile(r"\b(this|that) (cell|sentence|paragraph|slide|number|line|section|row|column)\b", re.I)
SHEET_LOC = re.compile(r"^(?:'[^']+'|[^!\s]+)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?$")
SLIDE_LOC = re.compile(r"^slide \d+$", re.I)
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MENTION_PREFIX = re.compile(r"^(?:@\S+\s+)+")


def validate(spec: dict) -> list[str]:
    errs = []
    kind = spec.get("kind")
    if not spec.get("fileId"):
        errs.append("fileId missing")
    if kind not in {"sheets", "slides", "docs", "docx", "file"}:
        errs.append(f"kind must be sheets|slides|docs|docx|file, got {kind!r}")
    comments = spec.get("comments", [])
    if len(comments) + len(spec.get("replies", [])) > MAX_BATCH:
        errs.append(f"more than {MAX_BATCH} actions; split the batch after asking the user")
    for n, c in enumerate(comments, 1):
        body, loc, quote = c.get("body", ""), c.get("location", ""), c.get("quote", "")
        anchored = c.get("anchored", True)
        tag = f"comment {n}"
        if not body.strip():
            errs.append(f"{tag}: empty body")
            continue
        if kind == "sheets" and not SHEET_LOC.match(loc):
            errs.append(f"{tag}: Sheets location must look like Sheet!C12 or Sheet!A2:D10, got {loc!r}")
        if kind == "slides" and not SLIDE_LOC.match(loc):
            errs.append(f"{tag}: Slides location must look like 'slide 4', got {loc!r}")
        if kind in {"docs", "docx"} and not quote:
            errs.append(f"{tag}: {kind} comments need the exact quoted text")
        if kind in {"sheets", "slides"} and loc and loc.lower() not in body.lower():
            errs.append(f"{tag}: body must name its location {loc!r} (anchors may not show in the editor)")
        if kind == "docs" and not anchored and quote and quote[:40].lower() not in body.lower():
            errs.append(f"{tag}: unanchored Docs comment body must quote its target text")
        if kind == "file" and not (loc and loc.lower() in body.lower()):
            errs.append(f"{tag}: file-level comment must name what it refers to (page, section, timestamp) in the body")
        if VAGUE.search(body) and not (loc and loc.lower() in body.lower()) and not (quote and quote[:40].lower() in body.lower()):
            if not ((kind == "docs" and anchored and quote) or (kind == "docx" and quote)):
                errs.append(f"{tag}: vague reference ('{VAGUE.search(body).group(0)}') without evidence")
    if kind == "docx" and spec.get("replies"):
        errs.append("docx replies are not supported via Drive API; reply directly in the Office editor")
    for n, r in enumerate(spec.get("replies", []), 1):
        if not r.get("commentId") or not r.get("body", "").strip():
            errs.append(f"reply {n}: needs commentId and body")
    return errs


def utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def _iter_doc_tabs(doc: dict):
    def visit(tab_list):
        for t in tab_list:
            yield t["tabProperties"]["tabId"], t["documentTab"]["body"]["content"]
            yield from visit(t.get("childTabs", []))

    if "tabs" in doc:
        yield from visit(doc["tabs"])
    else:
        yield None, doc.get("body", {}).get("content", [])


def _iter_paragraphs(elements: list[dict]):
    for el in elements:
        if "paragraph" in el:
            yield el["paragraph"]
        elif "table" in el:
            for row in el["table"].get("tableRows", []):
                for cell in row.get("tableCells", []):
                    yield from _iter_paragraphs(cell.get("content", []))


def find_quote_ranges(doc: dict, quote: str, context: str | None = None, tab_id: str | None = None) -> list[dict]:
    """Return all exact UTF-16 ranges matching `quote` inside single paragraphs of `doc`.

    Skips runs marked with `suggestedDeletionIds` so deleted suggestions are not matched.
    If `context` is given, keeps only paragraphs whose live text contains `context`.
    """
    matches = []
    for tid, content in _iter_doc_tabs(doc):
        if tab_id is not None and tid != tab_id:
            continue
        for para in _iter_paragraphs(content):
            # Build (live_text, utf16_index_per_char) across contiguous text runs.
            text_parts, idx_map = [], []
            for pe in para.get("elements", []):
                tr = pe.get("textRun")
                if not tr or tr.get("suggestedDeletionIds"):
                    continue
                run = tr.get("content", "")
                pos = pe.get("startIndex")
                if pos is None:
                    continue
                for ch in run:
                    text_parts.append(ch)
                    idx_map.append(pos)
                    pos += utf16_len(ch)
            full = "".join(text_parts)
            if context and context not in full:
                continue
            start = 0
            while True:
                i = full.find(quote, start)
                if i < 0:
                    break
                end_i = i + len(quote)
                s_idx = idx_map[i]
                e_idx = idx_map[end_i - 1] + utf16_len(full[end_i - 1])
                rng = {"startIndex": s_idx, "endIndex": e_idx}
                if tid is not None:
                    rng["tabId"] = tid
                matches.append({"range": rng, "paragraph": full.strip()[:120]})
                start = i + 1
    return matches


def resolve_doc_range(doc: dict, comment: dict) -> dict:
    """Resolve one Docs comment to a single `Range`, raising ValueError if missing or ambiguous."""
    quote = comment["quote"]
    matches = find_quote_ranges(doc, quote, context=comment.get("context"), tab_id=comment.get("tabId"))
    if not matches:
        raise ValueError(f"quote not found in live Doc: {quote!r}")
    occ = comment.get("occurrence")
    if occ is None:
        if len(matches) > 1:
            raise ValueError(
                f"quote {quote!r} matched {len(matches)} places; set 'occurrence' (1..{len(matches)}) or 'context'"
            )
        return matches[0]["range"]
    if not (1 <= occ <= len(matches)):
        raise ValueError(f"occurrence {occ} out of range for {quote!r} ({len(matches)} match(es))")
    return matches[occ - 1]["range"]


def build_insert_comment_request(comment: dict, rng: dict) -> dict:
    req: dict = {"content": comment["body"], "range": rng}
    if comment.get("assignee"):
        req["assigneeEmailAddress"] = comment["assignee"]
    return {"insertComment": req}


def gws_cmd() -> list[str]:
    if GWS_NATIVE.exists():
        return [str(GWS_NATIVE)]
    found = shutil.which("gws")
    if not found:
        raise SystemExit("gws not found")
    return [found]


def gws(*args: str, params: dict, body: dict | None = None) -> dict:
    cmd = gws_cmd() + list(args) + ["--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body, ensure_ascii=False)]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"gws {' '.join(args)} failed: {p.stderr.strip() or p.stdout.strip()}")
    out = p.stdout or ""
    idx = out.find("{")
    return json.loads(out[idx:]) if idx >= 0 else {}


def existing_comments(file_id: str) -> list[dict]:
    out, token = [], None
    while True:
        params = {"fileId": file_id, "pageSize": 100,
                  "fields": "comments(id,anchor,content,resolved),nextPageToken"}
        if token:
            params["pageToken"] = token
        page = gws("drive", "comments", "list", params=params)
        out += page.get("comments", [])
        token = page.get("nextPageToken")
        if not token:
            return out


def _norm_body(text: str) -> str:
    return re.sub(r"\s+", " ", MENTION_PREFIX.sub("", text.strip())).strip().lower()


def inspect_docx(docx_path: Path, comments: list[dict]) -> dict:
    """Inspect a .docx zip for live quote uniqueness, textbox traps, and existing word/comments.xml threads."""
    with zipfile.ZipFile(docx_path) as z:
        doc_xml_raw = z.read("word/document.xml").decode("utf-8", "replace")
        root = ET.fromstring(doc_xml_raw)
        normal_paras, textbox_paras = [], []

        def walk_body(el: ET.Element, in_box: bool) -> None:
            if el.tag == f"{W_NS}del":
                return
            if el.tag == f"{W_NS}txbxContent":
                for ch in el:
                    walk_body(ch, True)
                return
            if el.tag == f"{W_NS}p":
                parts: list[str] = []

                def para_text(node: ET.Element) -> None:
                    if node.tag in {f"{W_NS}del", f"{W_NS}txbxContent"}:
                        if node.tag == f"{W_NS}txbxContent":
                            for ch in node:
                                walk_body(ch, True)
                        return
                    if node.tag == f"{W_NS}t" and node.text:
                        parts.append(node.text)
                    for ch in node:
                        para_text(ch)

                para_text(el)
                txt = "".join(parts)
                if txt.strip():
                    (textbox_paras if in_box else normal_paras).append(txt)
                return
            for ch in el:
                walk_body(ch, in_box)

        body_el = root.find(f"{W_NS}body")
        if body_el is not None:
            walk_body(body_el, False)

        existing: list[dict] = []
        if "word/comments.xml" in z.namelist():
            cx = z.read("word/comments.xml").decode("utf-8", "replace")
            for m in re.finditer(r"<w:comment\b([^>]*)>(.*?)</w:comment>", cx, re.S):
                attrs = dict(re.findall(r'w:(\w+)="([^"]*)"', m.group(1)))
                body = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", m.group(2)))
                cid = attrs.get("id", "")
                span = re.search(
                    rf'<w:commentRangeStart w:id="{re.escape(cid)}"\s*/>(.*?)<w:commentRangeEnd w:id="{re.escape(cid)}"\s*/>',
                    doc_xml_raw,
                    re.S,
                )
                anc = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", span.group(1))) if span else ""
                existing.append({
                    "id": cid,
                    "author": attrs.get("author", ""),
                    "date": attrs.get("date", ""),
                    "anchor": anc,
                    "body": body,
                })

    checks: list[dict] = []
    for c in comments:
        quote = c["quote"]
        occ = c.get("occurrence")
        hits = [p for p in normal_paras if quote in p]
        total = sum(p.count(quote) for p in hits)
        in_box = total == 0 and any(quote in bp for bp in textbox_paras)
        norm_new = _norm_body(c["body"])
        related = []
        exact_dup = False
        for ex in existing:
            norm_ex = _norm_body(ex["body"])
            if norm_ex == norm_new:
                exact_dup = True
                related.append({**ex, "match": "exact_duplicate"})
            elif (
                (len(norm_new) >= 28 and norm_new[:28] in norm_ex)
                or (ex["anchor"] and (quote in ex["anchor"] or ex["anchor"] in quote))
            ):
                related.append({**ex, "match": "existing_thread"})
        status = "ok"
        if in_box:
            status = "textbox_blocked"
        elif total == 0:
            status = "missing"
        elif total > 1 and occ is None:
            status = "ambiguous"
        elif occ is not None and not (1 <= occ <= total):
            status = "occurrence_out_of_range"
        checks.append({
            "quote": quote,
            "occurrence": occ or 1,
            "matches": total,
            "in_textbox": in_box,
            "status": status,
            "exact_duplicate": exact_dup,
            "related_existing": related,
            "snippets": [h.strip()[:140] for h in hits[:3]],
        })
    return {"existing_comments": existing, "checks": checks}


def download_docx(file_id: str, dest: Path) -> dict:
    meta = gws("drive", "files", "get", params={
        "fileId": file_id,
        "fields": "id,name,version,md5Checksum,modifiedTime,mimeType",
    })
    cmd = gws_cmd() + ["drive", "files", "get", "--params", json.dumps({"fileId": file_id, "alt": "media"}), "-o", dest.name]
    p = subprocess.run(cmd, cwd=str(dest.parent), capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"gws drive files get media failed: {p.stderr.strip() or p.stdout.strip()}")
    return meta


def build_docx_browse_script(spec: dict, comments: list[dict]) -> str:
    """Return a guarded Playwright JS body for `browse` (Office-mode .docx anchored comments)."""
    fid = spec["fileId"]
    authuser = spec.get("authuser", "")
    url = f"https://docs.google.com/document/d/{fid}/edit" + (f"?authuser={authuser}" if authuser else "")
    items = [
        {"quote": c["quote"], "occurrence": int(c.get("occurrence") or 1), "body": c["body"]}
        for c in comments
    ]
    payload = json.dumps({"fileId": fid, "url": url, "items": items}, ensure_ascii=False)
    return f"""// Guarded Office-mode .docx anchored-comment poster for `browse` (Helium).
// Safety rule: NEVER types until `.docos-input-textarea:visible` is confirmed open and focused.
const CFG = {payload};
await page.goto(CFG.url, {{ waitUntil: 'commit', timeout: 30000 }});
await page.waitForFunction(() => {{
  const share = document.querySelector('[aria-label*="Share"]');
  return !!share && share.getAttribute('aria-disabled') !== 'true';
}}, null, {{ timeout: 45000 }});
await page.waitForTimeout(2000);

const posted = [], failed = [];
for (const item of CFG.items) {{
  await page.keyboard.press('Escape');
  await page.waitForTimeout(300);
  await page.mouse.click(400, 300);
  await page.waitForTimeout(300);
  await page.keyboard.press('Control+f');
  const findInput = page.locator('input[aria-label="Find in document"], .docs-findinput-input').first();
  await findInput.waitFor({{ state: 'visible', timeout: 5000 }});
  await findInput.fill(item.quote);
  await page.waitForTimeout(1500);
  const countText = await page.evaluate(() => {{
    const inp = document.querySelector('input[aria-label="Find in document"], .docs-findinput-input');
    let el = inp;
    for (let i = 0; i < 6 && el && el.parentElement; i++) {{
      el = el.parentElement;
      const t = (el.innerText || '').trim();
      const hit = t.match(/\\d+\\s+of\\s+\\d+/i);
      if (hit) return hit[0];
    }}
    return '';
  }});
  const m = countText.match(/(\\d+)\\s+of\\s+(\\d+)/i);
  const cur = m ? parseInt(m[1], 10) : 0;
  const total = m ? parseInt(m[2], 10) : 0;
  if (!total || item.occurrence > total) {{
    failed.push({{ quote: item.quote, status: 'not_found', countText }});
    await page.keyboard.press('Escape');
    continue;
  }}
  const steps = (item.occurrence - cur + total) % total;
  for (let k = 0; k < steps; k++) {{
    await page.keyboard.press('Enter');
    await page.waitForTimeout(350);
  }}
  await page.keyboard.press('Escape');
  await page.waitForTimeout(600);
  await page.keyboard.press('Control+Alt+m');
  const box = page.locator('.docos-input-textarea >> visible=true').first();
  const opened = await box.waitFor({{ state: 'visible', timeout: 4000 }}).then(() => true).catch(() => false);
  if (!opened) {{
    failed.push({{ quote: item.quote, status: 'composer_not_focused' }});
    continue;
  }}
  await box.fill(item.body);
  await page.waitForTimeout(400);
  const postBtn = page.getByRole('button', {{ name: /^Comment$/i }}).locator('visible=true').first();
  if (await postBtn.isVisible().catch(() => false)) {{
    await postBtn.click();
  }} else {{
    await page.keyboard.press('Control+Enter');
  }}
  const probe = item.body.replace(/^(@\\S+\\s+)+/, '').slice(0, 24);
  const card = page.locator('.docos-anchoreddocoview').filter({{ hasText: probe }}).first();
  const ok = await card.waitFor({{ state: 'visible', timeout: 8000 }}).then(() => true).catch(() => false);
  if (ok) {{
    posted.push({{ quote: item.quote, occurrence: item.occurrence, probe }});
  }} else {{
    failed.push({{ quote: item.quote, status: 'card_not_verified', probe }});
  }}
  await page.waitForTimeout(800);
}}
await page.waitForTimeout(4000);
return {{ fileId: CFG.fileId, posted, failed, verified: failed.length === 0 }};
"""


def plan(spec: dict) -> list[str]:
    lines = [f"file {spec['fileId']} ({spec['kind']})"]
    for c in spec.get("comments", []):
        if spec["kind"] == "docx":
            mode = "docx-ui"
        elif spec["kind"] == "docs" and c.get("anchored", True):
            mode = "anchored"
        else:
            mode = "drive"
        lines.append(f"  + [{mode}:{c.get('location') or c.get('quote', '')[:30]}] {c['body']}")
    for r in spec.get("replies", []):
        lines.append(f"  > reply {r['commentId']}{' + resolve' if r.get('resolve') else ''}: {r['body']}")
    return lines


def post_docx(spec: dict, emit_js: Path | None = None) -> dict:
    fid = spec["fileId"]
    with tempfile.TemporaryDirectory() as td:
        local = Path(td) / "live.docx"
        meta = download_docx(fid, local)
        info = inspect_docx(local, spec.get("comments", []))
    bad = [ch for ch in info["checks"] if ch["status"] != "ok"]
    if bad:
        raise ValueError("live .docx pre-flight failed: " + json.dumps(bad, ensure_ascii=False))
    to_post, skipped = [], []
    for c, ch in zip(spec.get("comments", []), info["checks"]):
        if ch["exact_duplicate"]:
            skipped.append(c["body"][:60])
        else:
            to_post.append(c)
    if not to_post:
        return {"created": 0, "anchored": 0, "skipped_duplicates": skipped, "verified": True, "meta": meta}
    js = build_docx_browse_script(spec, to_post)
    if emit_js:
        emit_js.write_text(js, encoding="utf-8")
    browse_bin = shutil.which("browse")
    if not browse_bin:
        raise RuntimeError("browse CLI not found; use --emit-js and run the generated script via browse MCP")
    with tempfile.TemporaryDirectory() as td:
        jsp = Path(td) / "post_docx.js"
        jsp.write_text(js, encoding="utf-8")
        p = subprocess.run([browse_bin, "execute", "--rm", "--file", str(jsp)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=240)
        if p.returncode != 0:
            raise RuntimeError(f"browse execute failed: {p.stderr.strip() or p.stdout.strip()}")
        out = p.stdout or ""
        idx = out.find("{")
        res = json.loads(out[idx:]) if idx >= 0 else {"raw": out}
    return {
        "created": len(res.get("posted", [])),
        "anchored": len(res.get("posted", [])),
        "failed": res.get("failed", []),
        "skipped_duplicates": skipped,
        "verified": bool(res.get("verified")),
        "meta": meta,
    }


def post(spec: dict, emit_js: Path | None = None) -> dict:
    if spec["kind"] == "docx":
        return post_docx(spec, emit_js=emit_js)
    fid, kind = spec["fileId"], spec["kind"]
    before = {c["content"].strip() for c in existing_comments(fid) if not c.get("resolved")}
    created, skipped, replied = [], [], []
    doc_requests = []
    live_doc = None
    if kind == "docs" and any(c.get("anchored", True) for c in spec.get("comments", [])):
        live_doc = gws("docs", "documents", "get", params={"documentId": fid, "includeTabsContent": True})
    for c in spec.get("comments", []):
        if c["body"].strip() in before:
            skipped.append(c["body"][:60])
            continue
        if kind == "docs" and c.get("anchored", True):
            rng = resolve_doc_range(live_doc, c)
            doc_requests.append(build_insert_comment_request(c, rng))
        else:
            body: dict = {"content": c["body"]}
            if c.get("quote"):
                body["quotedFileContent"] = {"mimeType": "text/plain", "value": c["quote"]}
            res = gws("drive", "comments", "create", params={"fileId": fid, "fields": "id"}, body=body)
            created.append(res["id"])
    if doc_requests:
        batch_body: dict = {"requests": doc_requests}
        if live_doc and live_doc.get("revisionId"):
            batch_body["writeControl"] = {"requiredRevisionId": live_doc["revisionId"]}
        res = gws("docs", "documents", "batchUpdate", params={"documentId": fid}, body=batch_body)
        for rep in res.get("replies", []):
            cid = rep.get("insertComment", {}).get("commentThread", {}).get("commentId")
            if cid:
                created.append(cid)
    for r in spec.get("replies", []):
        body = {"content": r["body"]}
        if r.get("resolve"):
            body["action"] = "resolve"
        res = gws("drive", "replies", "create",
                  params={"fileId": fid, "commentId": r["commentId"], "fields": "id"}, body=body)
        replied.append(res["id"])
    after = {c["id"]: c for c in existing_comments(fid)}
    missing = [i for i in created if i not in after]
    anchored_count = sum(1 for i in created if (after.get(i, {}).get("anchor") or "").startswith("kix."))
    return {"created": len(created), "anchored": anchored_count, "replied": len(replied),
            "skipped_duplicates": skipped, "verified": not missing, "missing_after_post": missing}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("spec", type=Path)
    ap.add_argument("--post", action="store_true", help="send (default is a dry run)")
    ap.add_argument("--live", action="store_true", help="for kind=docx dry run, inspect live .docx XML & comments.xml")
    ap.add_argument("--emit-js", type=Path, default=None, help="write guarded browse JS script for kind=docx")
    a = ap.parse_args(argv)
    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    errs = validate(spec)
    if errs:
        print("REJECTED:\n" + "\n".join(f"- {e}" for e in errs))
        return 2
    print("\n".join(plan(spec)))
    if not a.post:
        if spec["kind"] == "docx" and a.live:
            with tempfile.TemporaryDirectory() as td:
                local = Path(td) / "live.docx"
                meta = download_docx(spec["fileId"], local)
                info = inspect_docx(local, spec.get("comments", []))
            print(f"\nLIVE .DOCX CHECK: {meta.get('name')} (v{meta.get('version')}, modified {meta.get('modifiedTime')})")
            print(f"Existing word/comments.xml count: {len(info['existing_comments'])}")
            bad = 0
            for n, ch in enumerate(info["checks"], 1):
                if ch["status"] != "ok":
                    bad += 1
                print(f"  #{n} [{ch['status']}] matches={ch['matches']} occ={ch['occurrence']} quote={ch['quote']!r}")
                for sn in ch["snippets"][:2]:
                    print(f"      live: {sn}")
                for rel in ch["related_existing"]:
                    print(
                        f"      WARN {rel['match']} (word id={rel['id']}, {rel['author']} {rel['date']}, "
                        f"anc={rel['anchor']!r}): {rel['body'][:110]}"
                    )
            if a.emit_js:
                a.emit_js.write_text(build_docx_browse_script(spec, spec.get("comments", [])), encoding="utf-8")
                print(f"Wrote guarded browse JS: {a.emit_js}")
            print("dry run: nothing sent (add --post or run the emitted JS via browse MCP after the user approves)")
            return 2 if bad else 0
        if spec["kind"] == "docx" and a.emit_js:
            a.emit_js.write_text(build_docx_browse_script(spec, spec.get("comments", [])), encoding="utf-8")
            print(f"Wrote guarded browse JS: {a.emit_js}")
        print("dry run: nothing sent (add --post after the user approves)")
        return 0
    print(json.dumps(post(spec, emit_js=a.emit_js), indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
