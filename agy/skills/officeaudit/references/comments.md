# /officeaudit comments

Turn audit findings (or my notes) into Google Drive/Docs comments on the file, so the owner sees them where they work. Posting is visible to everyone with access: always dry-run, show the plan, and post only after I approve.

## 1. Ground the target

- Resolve the exact file: an id or URL from me, the file id kept from the audit export, or a Drive search (`gws drive files list`) narrowed until exactly one file matches. Confirm its type: Sheets, Slides, Docs, or another Drive file (PDF, uploaded Office file).
- Read the live file at each place you will comment on (the cell's current value or formula, the slide's current text, the sentence as it stands now). Never take a target from memory, an old export or a search snippet; the owner may have changed it since the audit.
- List existing comments first (the script does this when posting) so you reply to an open thread rather than duplicating it.

## 2. Draft every comment with its evidence

- **Google Docs (`kind: "docs"`)**: `post_comments.py` uses the **Docs API `documents.batchUpdate` `insertComment`** request by default (`"anchored": true`), which pins each comment to the exact UTF-16 text range (`kix.*` anchor) in the Docs editor and triggers `@email` notifications. Give the exact `quote` from the live Doc; when `quote` appears more than once, add `context` (a nearby unique phrase in the same paragraph) or 1-based `occurrence` (plus `tabId` on multi-tab docs, and optional `assignee`). Only set `"anchored": false` if you need the unanchored Drive API fallback (in which case the body itself must repeat the quote).
- **Sheets, Slides, and other Drive files**: Drive API comments often appear unanchored in the Google editors, so the comment text itself must say where it points:
  - **Sheets**: location `Sheet!C12` or `Sheet!A2:D10`, and the body names the same range: "Calc!E4: types 0.12 instead of linking Inputs!$B$4, so 2029 profit ignores the margin input."
  - **Slides**: location `slide 4`, and the body names the slide and quotes the visible text: "Slide 4, title '1,823 by 2030': the model shows 1,823 for 2030, but the subtitle says 2029."
  - **Other files**: the body names the page, section or timestamp.

Write each comment so it stands alone: what is wrong, the evidence, and the suggested fix, in one to three sentences. Drop or merge anything vague ("this cell looks off"); if a finding cannot be pinned to a place, make it one file-level summary comment or leave it out and say so. Keep my tone: direct and polite; these go to colleagues.

## 3. Dry run, approve, post

Write the batch to a spec file in the scratch folder:

```json
{"fileId": "<id>", "kind": "docs",
 "comments": [{"quote": "5.568.100", "context": "Phương án 2", "body": "@owner ..."}],
 "replies": [{"commentId": "<existing id>", "body": "Fixed in v3", "resolve": true}]}
```

```
python -X utf8 ~/.gemini/config/skills/officeaudit/scripts/post_comments.py <spec.json>          # validate + show plan
python -X utf8 ~/.gemini/config/skills/officeaudit/scripts/post_comments.py <spec.json> --post   # after I approve
```

The script rejects comments without matching evidence, more than 25 actions at once (ask before splitting), and skips exact duplicates of open comments. For Docs, `--post` reads the live Doc, resolves every `quote` to its exact UTF-16 range, guards the batch with `requiredRevisionId`, and aborts before sending if any quote is missing or ambiguous. Show me the dry-run plan and wait for approval before `--post`. Replies and resolves use comment ids from the live comment list only.

## 4. Verify

After posting, the script re-lists comments and reports `created`, `anchored` (`kix.*` count), `replied`, `skipped_duplicates`, and whether every new id is present. Tell me those counts, and quote the evidence of the highest-severity comments.
