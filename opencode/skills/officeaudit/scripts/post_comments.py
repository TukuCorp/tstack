"""Post evidence-anchored Drive comments for /officeaudit comments.

Drive API comments often show unanchored in the Docs/Sheets/Slides editor, so every comment
body must itself name its target: `Sheet!A1` for Sheets, `slide N` for Slides, an exact quote
for Docs. Vague comments are rejected before anything is sent.

Spec file (JSON):
  {"fileId": "...", "kind": "sheets|slides|docs|file",
   "comments": [{"location": "Inputs!C12", "quote": "optional exact text", "body": "..."}],
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
        if kind == "docs" and quote and quote[:40].lower() not in body.lower():
            errs.append(f"{tag}: body must quote its target text")
        if kind == "file" and not (loc and loc.lower() in body.lower()):
            errs.append(f"{tag}: file-level comment must name what it refers to (page, section, timestamp) in the body")
        if VAGUE.search(body) and not (loc and loc.lower() in body.lower()) and not (quote and quote[:40].lower() in body.lower()):
            errs.append(f"{tag}: vague reference ('{VAGUE.search(body).group(0)}') without evidence")
    for n, r in enumerate(spec.get("replies", []), 1):
        if not r.get("commentId") or not r.get("body", "").strip():
            errs.append(f"reply {n}: needs commentId and body")
    return errs


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
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)
    if p.returncode != 0:
        raise RuntimeError(f"gws {' '.join(args)} failed: {p.stderr.strip() or p.stdout.strip()}")
    return json.loads(p.stdout or "{}")


def existing_comments(file_id: str) -> list[dict]:
    out, token = [], None
    while True:
        params = {"fileId": file_id, "pageSize": 100,
                  "fields": "comments(id,content,resolved),nextPageToken"}
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
        lines.append(f"  + [{c.get('location') or c.get('quote', '')[:30]}] {c['body']}")
    for r in spec.get("replies", []):
        lines.append(f"  > reply {r['commentId']}{' + resolve' if r.get('resolve') else ''}: {r['body']}")
    return lines


def post(spec: dict) -> dict:
    fid = spec["fileId"]
    before = {c["content"].strip() for c in existing_comments(fid) if not c.get("resolved")}
    created, skipped, replied = [], [], []
    for c in spec.get("comments", []):
        if c["body"].strip() in before:
            skipped.append(c["body"][:60])
            continue
        body = {"content": c["body"]}
        if c.get("quote"):
            body["quotedFileContent"] = {"mimeType": "text/plain", "value": c["quote"]}
        res = gws("drive", "comments", "create", params={"fileId": fid, "fields": "id"}, body=body)
        created.append(res["id"])
    for r in spec.get("replies", []):
        body = {"content": r["body"]}
        if r.get("resolve"):
            body["action"] = "resolve"
        res = gws("drive", "replies", "create",
                  params={"fileId": fid, "commentId": r["commentId"], "fields": "id"}, body=body)
        replied.append(res["id"])
    after_ids = {c["id"] for c in existing_comments(fid)}
    missing = [i for i in created if i not in after_ids]
    return {"created": len(created), "replied": len(replied), "skipped_duplicates": skipped,
            "verified": not missing, "missing_after_post": missing}


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
