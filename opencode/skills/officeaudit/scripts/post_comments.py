"""Post evidence-anchored comments for /officeaudit comments.

- Google Docs (`kind: "docs"`): uses the Docs API `documents.batchUpdate` `insertComment` request
  by default (`"anchored": true`), which creates real range-anchored (`kix.*`) comments pinned to
  the exact UTF-16 text range in the Docs editor (and triggers `@email` notifications).
  Set `"anchored": false` on a comment to fall back to the unanchored Drive API.
- Google Sheets, Slides, and other Drive files: uses the Drive API (`drive comments create`).
  Because Drive API comments often show unanchored in the editors, every body must name its target:
  `Sheet!A1` for Sheets, `slide N` for Slides, or page/section for other files.

Spec file (JSON):
  {"fileId": "...", "kind": "sheets|slides|docs|file",
   "comments": [{"location": "Inputs!C12", "quote": "exact text", "context": "optional nearby text",
                 "occurrence": 1, "tabId": "optional", "assignee": "optional@email",
                 "anchored": true, "body": "..."}],
   "replies":  [{"commentId": "...", "body": "...", "resolve": false}]}

Usage: python -X utf8 post_comments.py spec.json            # dry run: validate and print the plan
       python -X utf8 post_comments.py spec.json --post     # send, skip duplicates, verify
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

MAX_BATCH = 25
GWS_NATIVE = Path(os.environ.get("APPDATA", "")) / "npm/node_modules/@googleworkspace/cli/bin/gws.exe"
VAGUE = re.compile(r"\b(this|that) (cell|sentence|paragraph|slide|number|line|section|row|column)\b", re.I)
SHEET_LOC = re.compile(r"^(?:'[^']+'|[^!\s]+)!\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?$")
SLIDE_LOC = re.compile(r"^slide \d+$", re.I)


def validate(spec: dict) -> list[str]:
    errs = []
    kind = spec.get("kind")
    if not spec.get("fileId"):
        errs.append("fileId missing")
    if kind not in {"sheets", "slides", "docs", "file"}:
        errs.append(f"kind must be sheets|slides|docs|file, got {kind!r}")
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
        if kind == "docs" and not quote:
            errs.append(f"{tag}: Docs comments need the exact quoted text")
        if kind in {"sheets", "slides"} and loc and loc.lower() not in body.lower():
            errs.append(f"{tag}: body must name its location {loc!r} (anchors may not show in the editor)")
        if kind == "docs" and not anchored and quote and quote[:40].lower() not in body.lower():
            errs.append(f"{tag}: unanchored Docs comment body must quote its target text")
        if kind == "file" and not (loc and loc.lower() in body.lower()):
            errs.append(f"{tag}: file-level comment must name what it refers to (page, section, timestamp) in the body")
        if VAGUE.search(body) and not (loc and loc.lower() in body.lower()) and not (quote and quote[:40].lower() in body.lower()):
            if not (kind == "docs" and anchored and quote):
                errs.append(f"{tag}: vague reference ('{VAGUE.search(body).group(0)}') without evidence")
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


def plan(spec: dict) -> list[str]:
    lines = [f"file {spec['fileId']} ({spec['kind']})"]
    for c in spec.get("comments", []):
        mode = "anchored" if (spec["kind"] == "docs" and c.get("anchored", True)) else "drive"
        lines.append(f"  + [{mode}:{c.get('location') or c.get('quote', '')[:30]}] {c['body']}")
    for r in spec.get("replies", []):
        lines.append(f"  > reply {r['commentId']}{' + resolve' if r.get('resolve') else ''}: {r['body']}")
    return lines


def post(spec: dict) -> dict:
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
    a = ap.parse_args(argv)
    spec = json.loads(a.spec.read_text(encoding="utf-8"))
    errs = validate(spec)
    if errs:
        print("REJECTED:\n" + "\n".join(f"- {e}" for e in errs))
        return 2
    print("\n".join(plan(spec)))
    if not a.post:
        print("dry run: nothing sent (add --post after the user approves)")
        return 0
    print(json.dumps(post(spec), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
