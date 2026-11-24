# gws — Google Workspace CLI Reference

Full command reference for `@googleworkspace/cli` (`gws`).

Install: `npm install -g @googleworkspace/cli`

Multi-account pattern — always prefix with config dir env var:
```bash
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-work gws <command>
GOOGLE_WORKSPACE_CLI_CONFIG_DIR=~/.config/gws-personal gws <command>
```

All output is JSON. Use `| jq` or `| python -m json.tool` to pretty-print.

---

## Auth

```bash
# Interactive OAuth setup (run once per account)
gws auth setup

# Check current auth status
gws auth status

# Revoke auth
gws auth revoke

# List configured accounts
gws auth list
```

---

## Drive

### List files
```bash
gws drive files list
  [--query "QUERY"]              # Drive search syntax (see below)
  [--fields "files(id,name,...)"]# Limit returned fields
  [--page-size N]                # Results per page (default 10, max 100)
  [--order-by "modifiedTime desc"]
  [--spaces "drive"]             # drive | appDataFolder | photos
  [--include-items-from-all-drives]
  [--corpora "user"]             # user | domain | drive | allDrives
```

Drive query syntax examples:
```
name contains 'Q1 Report'
mimeType = 'application/pdf'
'FOLDER_ID' in parents
modifiedTime > '2026-01-01T00:00:00'
trashed = false
fullText contains 'Vietnam'
```

### Get file metadata
```bash
gws drive files get FILE_ID
  [--fields "id,name,mimeType,size,webViewLink,parents,modifiedTime"]
```

### Upload file
```bash
gws drive +upload ./local-file.pdf
  [--parent-id FOLDER_ID]        # destination folder
  [--name "Display Name.pdf"]    # override filename
  [--mime-type "application/pdf"]
```

### Download file
```bash
gws drive files download FILE_ID
  [--output ./local-path.pdf]
```

### Copy file
```bash
gws drive files copy FILE_ID
  [--name "Copy of File"]
  [--parent-id FOLDER_ID]
```

### Move file (update parents)
```bash
gws drive files update FILE_ID
  --add-parents NEW_FOLDER_ID
  --remove-parents OLD_FOLDER_ID
```

### Delete file (moves to trash)
```bash
gws drive files delete FILE_ID
```

### Create folder
```bash
gws drive files +create-folder "Folder Name"
  [--parent-id PARENT_FOLDER_ID]
```

### Export Google Docs/Sheets/Slides to file
```bash
gws drive files export FILE_ID
  --mime-type "application/pdf"   # or application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
  --output ./exported.pdf
```

### List recent changes
```bash
gws drive changes list
  [--page-token TOKEN]
  [--include-corpus-removals]
```

---

## Gmail

### List messages
```bash
gws gmail messages list
  [--query "QUERY"]              # Gmail search syntax
  [--max-results N]              # default 10
  [--label-ids "INBOX,UNREAD"]
  [--include-spam-trash]
  [--fields "messages(id,threadId)"]
```

Gmail query syntax examples:
```
is:unread
from:partner@example.com
to:<EMAIL>
subject:"Board Update"
has:attachment
after:2026/01/01
label:important
```

### Get message
```bash
gws gmail messages get MESSAGE_ID
  [--format full]        # minimal | full | raw | metadata
  [--metadata-headers "Subject,From,To,Date"]
```

### Send email
```bash
gws gmail +send
  --to "recipient@example.com"
  --subject "Subject line"
  --body "Email body text"
  [--cc "cc@example.com"]
  [--bcc "bcc@example.com"]
  [--attachment ./file.pdf]
  [--html]               # treat body as HTML
```

### Reply to thread
```bash
gws gmail +reply THREAD_ID
  --body "Reply text"
  [--to "recipient@example.com"]
```

### Create draft
```bash
gws gmail drafts +create
  --to "recipient@example.com"
  --subject "Draft subject"
  --body "Draft body"
```

### List drafts
```bash
gws gmail drafts list [--max-results N]
```

### Add label
```bash
gws gmail messages modify MESSAGE_ID
  --add-label-ids "LABEL_ID"
  --remove-label-ids "INBOX"
```

### List labels
```bash
gws gmail labels list
```

### Get thread
```bash
gws gmail threads get THREAD_ID [--format full]
```

---

## Calendar

### List upcoming events
```bash
gws calendar events list
  [--calendar-id primary]        # primary | CALENDAR_ID | email
  [--time-min "2026-05-01T00:00:00Z"]
  [--time-max "2026-05-31T23:59:59Z"]
  [--max-results N]
  [--order-by startTime]
  [--single-events]              # expand recurring events
  [--q "search term"]
```

### Quick agenda view
```bash
gws calendar +agenda
  [--days 7]                     # number of days ahead (default 7)
  [--calendar-id primary]
```

### Create event
```bash
gws calendar +create "Event Title"
  --start "2026-05-05T10:00:00"
  --end "2026-05-05T11:00:00"
  [--timezone "Asia/Ho_Chi_Minh"]
  [--description "Agenda and notes"]
  [--location "Zoom link or address"]
  [--attendees "a@example.com,b@example.com"]
  [--calendar-id primary]
  [--send-notifications]
```

### Get event
```bash
gws calendar events get CALENDAR_ID EVENT_ID
```

### Update event
```bash
gws calendar events patch CALENDAR_ID EVENT_ID
  [--summary "New title"]
  [--start "..."]
  [--end "..."]
```

### Delete event
```bash
gws calendar events delete CALENDAR_ID EVENT_ID
```

### List calendars
```bash
gws calendar calendar-list list
```

---

## Sheets

### Create spreadsheet
```bash
gws sheets spreadsheets create
  --title "Spreadsheet Title"
```
Returns `spreadsheetId` — save this for subsequent operations.

### Get spreadsheet metadata
```bash
gws sheets spreadsheets get SHEET_ID
  [--fields "spreadsheetId,properties,sheets.properties"]
```

### Read values
```bash
gws sheets values get SHEET_ID
  --range "Sheet1!A1:Z100"
  [--major-dimension ROWS]       # ROWS | COLUMNS
  [--value-render-option FORMATTED_VALUE]
```

### Write values (update)
```bash
gws sheets values +update SHEET_ID
  --range "Sheet1!A1"
  --values '[["H1","H2","H3"],["v1","v2","v3"]]'
  [--value-input-option USER_ENTERED]   # RAW | USER_ENTERED
```

### Append values
```bash
gws sheets values +append SHEET_ID
  --range "Sheet1!A1"
  --values '[["new row 1","val"],["new row 2","val"]]'
  [--value-input-option USER_ENTERED]
  [--insert-data-option INSERT_ROWS]
```

### Clear values
```bash
gws sheets values clear SHEET_ID --range "Sheet1!A1:Z100"
```

### Batch update values
```bash
gws sheets values batch-update SHEET_ID
  --data '[{"range":"Sheet1!A1","values":[["v1"]]},{"range":"Sheet1!B1","values":[["v2"]]}]'
```

---

## Docs

### Get document
```bash
gws docs documents get DOC_ID
  [--fields "title,body,documentId"]
```

### Create document
```bash
gws docs documents +create
  --title "Document Title"
```
Returns `documentId`.

### Batch update (insert text, apply formatting)
```bash
gws docs documents batch-update DOC_ID
  --requests '[{"insertText":{"location":{"index":1},"text":"Hello World\n"}}]'
```

Common request types:
- `insertText` — insert at index
- `deleteContentRange` — remove range
- `updateTextStyle` — bold, italic, font, color
- `updateParagraphStyle` — heading level, alignment
- `insertTable` — insert table

---

## Useful Field Selectors

Drive file fields: `id,name,mimeType,size,webViewLink,parents,modifiedTime,createdTime,owners,shared`

Gmail message fields: `id,threadId,labelIds,snippet,payload(headers,body,parts)`

Calendar event fields: `id,summary,description,start,end,attendees,location,htmlLink`

---

## Tips

- Output is always JSON — pipe to `jq '.files[] | {id, name}'` etc. for extraction
- Drive search is powerful: combine `fullText contains`, `modifiedTime >`, `mimeType =`
- For large result sets, check for `nextPageToken` in response and use `--page-token` to paginate
- Gmail queries support the same syntax as the Gmail search bar
- Calendar `--single-events` is required to see individual instances of recurring events
