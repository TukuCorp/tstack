---
name: expense
description: Automate Tung's monthly Allotrope Vietnam expense reimbursement submission — find this period's invoices in his own Gmail, validate against company policy, file PDFs and update the Google Sheet worksheet for the period, and draft (never send) the submission email to the right recipients.
---

# Expense

Automates the monthly Allotrope Vietnam expense reimbursement submission process for
Tung Ho (<EMAIL>), driven entirely by the `gws` Google Workspace CLI plus
the `claude-in-chrome` MCP tools for one fallback case. No shared script, no external
dependency beyond those (both already available on this machine). Use `claude-in-chrome`
for the browser fallback, not the `browser-control` skill/CLI — this was a deliberate
correction from a live run, not a stylistic preference.

**Never source invoice data from local folders on disk.** Always search Tung's own
Gmail label directly for the target period before treating any invoice as his own.
A previous run of this process by hand wrongly assumed a local folder of downloaded
invoice PDFs was Tung's own data — it actually belonged to a colleague (every invoice
at this company is issued to the same buyer, "CÔNG TY TNHH ALLOTROPE VIETNAM", so
invoice content alone never proves whose expense it is). Only a direct, date-scoped
Gmail search under Tung's own label proves ownership. This rule is not optional.

**Never call a Gmail "send" operation.** This skill only ever creates a Gmail
**draft** (`gws gmail users drafts create`) and stops there. Tung reviews and sends
it himself, every time, in every harness — including any scheduled/unattended
invocation.

## Reference data

### Company identity (used in every compliance check)
- Buyer name must contain: `ALLOTROPE` and `VIETNAM`
- Buyer tax code must equal: `0317819013`
- Buyer address must contain: `Lê Thánh Tôn`
  (full: `L17-11, Tầng 17, Tòa nhà Vincom Center, 72 Lê Thánh Tôn, Phường Sài Gòn, TP
  Hồ Chí Minh, Việt Nam`)

### Gmail source
- Label: `Grab Tax Invoice` — this is the ONLY place invoices are sourced from.
- Account: `<EMAIL>` (Tung's own mailbox).

### Recipients for the submission draft
- To: `<EMAIL>` (supervisor), `<EMAIL>` (<FINANCE_CONTACT>),
  `<EMAIL>` (Lauren)
- Cc: `<EMAIL>` (<CONTROLLER>, Controller)

### Drive root folder
- Parent folder ID for all period subfolders:
  `<SHEET_ID>`

### Official worksheet columns (InCorp template — columns A-G are the official
submission range; column H is a working/audit column only, never mixed into a final
copy of the official template)
`Item #, Date, VAT Sales Order No, Company Name, Total VAT Amount (VND), Description,
Notes, Compliance Notes`

### Expense period rule
Given an invoice's issue date, let `day` be its day-of-month:
- If `day <= 15`: the period ends in that same month. Period = 16th of the *previous*
  month through 15th of *this* month.
- If `day > 15`: the period ends in the *next* month. Period = 16th of *this* month
  through 15th of *next* month (roll the year forward if crossing December→January).
- The period **label** (and Drive subfolder name) is the full English month name plus
  year of the period's *end* date. Example: an invoice dated `2026-07-04` (day 4 <=
  15) is in the period ending `2026-07-15`, labeled `"July 2026"`.

### Submission due date rule
Given the period's end month `M` and end year `Y`:
1. If `M` is 3, 6, 9, or 12 (fiscal-quarter-end): base due date = 3rd of month `M+1`.
2. Otherwise: base due date = 15th of month `M+1`.
   (Roll `Y` forward if `M == 12`.)
3. **Always check** whether the base due date falls on Saturday or Sunday, and if so
   shift it to the following Monday — this happens often, never skip this step.
   Example: period ending `2026-07-15` → base due date `2026-08-15` → that's a
   Saturday → real due date is Monday `2026-08-17`.

(Vietnamese public holidays, especially Tết, are NOT modeled here — if a computed due
date falls in late January through mid-February, flag it for a manual sanity check
against that year's actual holiday calendar.)

### VAT invoice compliance check
An invoice is compliant only if ALL of the following hold. Record the specific
failing reason code(s) for anything that fails — never silently exclude a
non-compliant invoice, always keep it in the worksheet with the flag.
1. Buyer name (case-insensitive) contains both "ALLOTROPE" and "VIETNAM" — else
   `WRONG_ENTITY`.
2. Buyer tax code (digits only) equals `0317819013` — else `WRONG_TAX_CODE`.
3. A clear VND-denominated total is present — either no foreign-currency pricing at
   all, or foreign-currency unit prices *plus* a clearly labeled VND total (e.g.
   "Tổng cộng tiền thanh toán qui đổi VND") — else `NOT_VND`.
4. Buyer address contains "Lê Thánh Tôn" — else `WRONG_ADDRESS`.

### Vendor → category lookup
Lowercase and diacritic-strip the seller name + line-item description, concatenate,
then match keywords below as substrings (longest match wins if several hit; default
to `"Uncategorized - review"` if none match):

| Keyword (diacritic-insensitive) | Category |
|---|---|
| grab | Air/Ground Transportation |
| gsm | Air/Ground Transportation |
| di chuyen xanh | Air/Ground Transportation |
| cuoc van chuyen | Air/Ground Transportation |
| taxi | Air/Ground Transportation |
| vietnam airlines | Air Travel |
| vietjet | Air Travel |
| ve may bay | Air Travel |
| bamboo airways | Air Travel |
| khach san | Lodging |
| hotel | Lodging |
| ca phe | Meals |
| coffee | Meals |
| trung nguyen | Meals |
| quan | Meals |
| nha hang | Meals |
| sasco | Meals |
| ngoc bao linh | Meals |
| in an | Printing |
| photo | Printing |
| chatgpt | AI Subscription |
| claude | AI Subscription |
| openai | AI Subscription |
| anthropic | AI Subscription |

## Procedure

### 1. Auth check (always first)
```bash
gws drive about get --params '{"fields":"user"}'
```
Confirm the response's `user.emailAddress` is `<EMAIL>`. If this fails or
returns the wrong account, STOP and tell the user to run `gws`'s login flow — do not
proceed into a half-broken run.

### 2. Determine the period
If invoked with no argument, find the **most recently closed** period as of today —
do NOT apply the expense period rule's day<=15/day>15 test directly to today's date,
that computes which period today falls *inside* (usually the still-open one, not the
one ready to submit). Instead:
- If today's day-of-month `<= 15`: the most recently closed period ended on the 15th
  of *last* month. Period = 16th of two-months-ago through 15th of last month, labeled
  by last month's name+year.
- If today's day-of-month `> 15`: the most recently closed period ended on the 15th of
  *this* month. Period = 16th of last month through 15th of this month, labeled by
  this month's name+year.
Verified against the real precedent (invoked 2026-07-20, day 20 > 15 → correctly
resolved to the period ending 2026-07-15, "July 2026" — not the naive
day>15-so-next-month reading, which would have wrongly produced "August 2026").

If invoked with an explicit period argument (e.g. a target month/year), compute that
period's start and end dates directly instead (16th of the prior month through the
15th of the named month).

**Extending a period's end date past its normal 15th cutoff (e.g. to catch invoices
that arrived a couple of days late) is a one-off exception, only on the user's explicit
request for that specific run** — never do it by default. When it happens, still use
the period's normal month label (extending the end date doesn't change which month the
period/folder is named after), and say so plainly in both the Gmail search step and the
draft body (e.g. "period July 16 - August 18, 2026 (extended a few days past the usual
15th to catch invoices that came in on the 17th)").

### 3. Search Gmail for this period's invoices
```bash
gws gmail users messages list --params '{
  "userId": "me",
  "q": "label:\"Grab Tax Invoice\" after:<PERIOD_START_YYYY/MM/DD> before:<DAY_AFTER_PERIOD_END_YYYY/MM/DD>"
}'
```
Gmail's `after:`/`before:` date filters are day-granular; `before:` is exclusive, so
pass the day *after* the period's end date to include messages on the end date
itself. Widen by a day or two on each side and re-filter by the invoice's actual
printed date if results seem incomplete — the email's received date and the
invoice's issue date are usually the same day but are not guaranteed to be.

### 4. For each message, extract invoice fields
For each message ID from step 3:
- List attachments from the message (`gws gmail users messages get --params
  '{"userId":"me","id":"<messageId>","format":"full"}'`) and look for a
  `application/pdf` part.
- **If a PDF attachment exists:** download it —
  ```bash
  gws gmail users messages attachments get --params '{"userId":"me","messageId":"<messageId>","id":"<attachmentId>"}' > attachment.json
  ```
  then decode the `data` field (base64url — replace `-`→`+`, `_`→`/` before standard
  base64 decoding) and write it to a local scratch PDF file. Read/inspect the PDF to
  extract: issue date, invoice number, serial, seller name, buyer name, buyer tax
  code, buyer address, currency info, and total VND amount.
- **If no PDF attachment exists** (some vendors only send a notification email with a
  lookup-portal link and code): by default, file this as a placeholder row — Total
  VAT Amount `0`, Compliance Notes `AMOUNT_PENDING - fill in manually`, and a Notes
  cell containing the portal link/code so it's easy to resolve later. Only attempt
  the browser fallback (navigate to the lookup URL/code from the email, read the
  rendered invoice) when the user has asked for it or when it's clearly quick and
  safe to do — it is not the mandatory default path.
  - Use `claude-in-chrome` MCP tools for this, not the `browser-control` skill/CLI.
  - Lookup portals commonly gate the search behind a CAPTCHA image field ("Mã kiểm
    tra" or similar). **Never solve a CAPTCHA.** Fill in the known lookup/reference
    code field, leave the CAPTCHA field alone, and ask the user to type it and submit
    — then continue once they confirm.
  - **Never click a portal's "print invoice" / "In hóa đơn" button (or anything that
    calls `window.print()`).** It opens a native OS print dialog that blocks the
    page's CDP input queue and cannot be dismissed programmatically — the tab hangs
    until the user cancels it by hand. Read the invoice fields straight off the
    rendered detail view/screenshot instead.
  - If the portal has no scriptable PDF/XML download either, ask the user to save the
    invoice PDF manually (from the portal's own download option, e.g. a right-click
    save or a "save as PDF" through their own print dialog) into the project's local
    folder. Once it lands there, read it, then file it into Drive exactly like a
    PDF pulled from Gmail (step 9) — same naming convention, same worksheet row.

### 5. Compliance check
Apply the VAT invoice compliance check above to each invoice's extracted fields.
Non-compliant invoices are NOT excluded — they stay in the worksheet with their
failure reason(s) recorded.

### 6. Find or create the period's Drive folder
```bash
gws drive files list --params '{"q":"name=\x27<PeriodLabel>\x27 and \x27<SHEET_ID>\x27 in parents and mimeType=\x27application/vnd.google-apps.folder\x27 and trashed=false"}'
```
If no result, create it:
```bash
gws drive files create --json '{"name":"<PeriodLabel>","parents":["<SHEET_ID>"],"mimeType":"application/vnd.google-apps.folder"}' --params '{"fields":"id,name,webViewLink"}'
```

### 7. Find or create the period's worksheet
Look for a Sheet named `<PeriodLabel>_Expenses` inside the period folder (`gws drive
files list` with a `parents` filter on the folder ID and
`mimeType='application/vnd.google-apps.spreadsheet'`). If absent, create it:
```bash
gws sheets spreadsheets create --json '{"properties":{"title":"<PeriodLabel>_Expenses"},"sheets":[{"properties":{"title":"Worksheet"}}]}' --params '{"fields":"spreadsheetId,spreadsheetUrl"}'
gws drive files update --params '{"fileId":"<spreadsheetId>","addParents":"<periodFolderId>","removeParents":"root"}' --json '{}'
```
Then write the header row (RAW input, see step 9's leading-zero note):
```bash
gws sheets spreadsheets values update --params '{"spreadsheetId":"<id>","range":"Worksheet!A1","valueInputOption":"RAW"}' --json '{"values":[["Item #","Date","VAT Sales Order No","Company Name","Total VAT Amount (VND)","Description","Notes","Compliance Notes"]]}'
```

### 8. Dedup against the existing worksheet
```bash
gws sheets spreadsheets values get --params '{"spreadsheetId":"<id>","range":"Worksheet!A1:H"}'
```
Skip any invoice from step 4 whose "VAT Sales Order No" (invoice number) already
appears in column C of the existing rows — it's already been filed by a previous run.

### 9. File each new invoice's PDF
```bash
gws drive files create --json '{"name":"<YYYYMMDD>_<serial>_<invoiceNumber>.pdf","parents":["<periodFolderId>"]}' --upload "<Windows-style local path to the scratch PDF>" --params '{"fields":"id,name,webViewLink"}'
```
**`--upload` requires a real Windows-style path** (e.g. `C:\Users\...`), not a
Git-Bash-style `/c/...` path — the latter fails with `os error 2` on this machine.

### 10. Append each new invoice's worksheet row
```bash
gws sheets spreadsheets values append --params '{"spreadsheetId":"<id>","range":"Worksheet!A1","valueInputOption":"RAW"}' --json '{"values":[[<itemNumber>,"<DD/MM/YYYY>","<invoiceNumber>","<sellerName>",<totalVND>,"<category>","<notes>","<complianceNotesOrEmpty>"]]}'
```
**Always use `valueInputOption: RAW`, never `USER_ENTERED`.** Sheets' default
behavior strips leading zeros from strings that look numeric — an invoice number like
`00003292` silently becomes `3292` under `USER_ENTERED`. RAW preserves it as literal
text.

`itemNumber` is the row's position in the worksheet (count of existing data rows + 1,
from step 8's read). `category` comes from the vendor lookup table above. `notes` is
free text (line-item description, or a judgment-call flag — see step 12). Leave
`complianceNotesOrEmpty` empty for compliant invoices; for non-compliant ones, put the
joined failure reason codes there.

**After filing all new invoices for the run, write/refresh a TOTAL row** (matches
every prior month's worksheet, e.g. July 2026): one row with columns A-C empty,
`"TOTAL"` in column D (Company Name), and the sum of column E (Total VAT Amount)
across all data rows in column E — including pending/placeholder amounts once
resolved. If a TOTAL row already exists from an earlier run in this period,
overwrite it in place (`values update` on its exact row) rather than appending a
second one.

### 11. Compute the due date and check if a draft already exists
Apply the due date rule above to the period's end date. Then check for an existing
draft with the same subject to avoid creating a duplicate:
```bash
gws gmail users drafts list --params '{"userId":"me"}'
```
(Inspect each draft's subject; if `"<PeriodLabel> Expense Reimbursement - Tung Ho"`
already exists, delete it first with `gws gmail users drafts delete --params
'{"userId":"me","id":"<draftId>"}'` before creating the replacement in step 12 — this
keeps re-runs from leaving stale duplicate drafts around.)

### 12. Draft the submission email (never send)
Sum the compliant + pending amounts for the period's total, and flag anything
unusual — a non-compliant invoice, a pending/placeholder amount, an unusually large
line item, a judgment call needing someone's approval (e.g. "this dinner needs <SUPERVISOR>'s
sponsorship confirmation") — directly in the draft body so it's visible before Tung
reviews and sends.

**Body format** (matches the actual precedent email, thread `19f7e17d2609aac6`,
"July 2026 Expense Reimbursement - Tung Ho", <SUPERVISOR>-approved):
- Greeting by first name, matching the To: recipients in order (e.g. "Hi <CONTROLLER>,
  Lauren, <SUPERVISOR>,").
- One line stating the submission and period: "Please find my expense reimbursement
  submission for the period <start> - <end>, <Year> in the usual folder."
- "Total: <X> VND across <N> items, both/all invoices filed:" followed by a numbered
  list, one line per item: `<n>. <vendor/description>, <DD/MM> - <amount> VND` — append
  a judgment-call flag inline on that line where relevant (e.g. "- this was our local
  team outing dinner, pending <SUPERVISOR>'s sponsorship if it's reasonable under our annual
  budget").
- Sign-off "Best,\nTung".
- **Exactly one Drive link, on its own line at the very end** — the period folder's
  own `webViewLink` captured in step 6 (e.g.
  `https://drive.google.com/drive/folders/<periodFolderId>`). This single folder
  already contains both the invoice PDFs and the worksheet, so do **not** add a
  second, separate link to the worksheet.

Construct and create the draft:
```bash
TO="<EMAIL>,<EMAIL>,<EMAIL>"
CC="<EMAIL>"
SUBJECT="<PeriodLabel> Expense Reimbursement - Tung Ho"
BODY="Hi <CONTROLLER>, Lauren, <SUPERVISOR>,

Please find my expense reimbursement submission for the period <start> -
<end>, <Year> in the usual folder.

Total: <X> VND across <N> items, both invoices filed:
1. <vendor>, <DD/MM> - <amount> VND
2. <vendor>, <DD/MM> - <amount> VND<flag if any>

Best,
Tung

<periodFolderWebViewLink>"

RAW=$(printf "To: %s\r\nCc: %s\r\nSubject: %s\r\nContent-Type: text/plain; charset=UTF-8\r\n\r\n%s" \
  "$TO" "$CC" "$SUBJECT" "$BODY" | base64 -w0 | tr '+/' '-_' | tr -d '=')

gws gmail users drafts create --params '{"userId":"me"}' \
  --json "{\"message\":{\"raw\":\"$RAW\"}}"
```
Tell the user the draft is ready for their review and that nothing has been sent.

## Gotchas

- Vietnamese invoices inconsistently use `.` or `,` as a thousands separator, even
  within the same document set — cross-check any extracted total against the
  invoice's written-out Vietnamese amount-in-words line (e.g. "Ba trăm nghìn đồng" =
  300,000) rather than trusting the numeric formatting alone.
- Never assume a local, already-downloaded folder of invoice PDFs belongs to Tung
  personally — every employee's invoices at this company are issued to the same
  buyer name, so invoice content alone can never prove ownership. Only a direct
  Gmail search under Tung's own label does.
- The 7-column official range (`Item #` through `Notes`) and the 8th `Compliance
  Notes` audit column must stay distinct — if this worksheet is ever copied into a
  fresh copy of the official InCorp template for final submission, copy only columns
  A-G.
- This skill never sends email. If any future change adds a "send" capability, that
  is a deliberate, separate decision requiring explicit human approval each time —
  not something this skill does on its own, ever, in any harness.
