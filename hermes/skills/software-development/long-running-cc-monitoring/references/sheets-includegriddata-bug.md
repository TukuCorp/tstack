# Sheets includeGridData Range Parsing Bug

## Symptom

```bash
gws sheets spreadsheets get --params '{"spreadsheetId": "ID", "ranges": ["Weekly!G2"], "includeGridData": true}'
# → "Unable to parse range: [\"Weekly!G2\"]"
```

The error occurs with ANY range specification when `includeGridData: true` is set — even the sheet title alone or simple ranges like `A1:Z10`. The error is specific to the `get` endpoint with `includeGridData`; the `values get` endpoint works fine with the same range strings.

## Root cause

The range parser in the Google Sheets API (as invoked by the `gws` CLI) fails on certain spreadsheets when `includeGridData` combines with a `ranges` parameter. Sheet tabs with unusual characters, merged cells, or non-standard grid properties seem to trigger it, but it can also occur on seemingly normal sheets.

## Workaround

**Do not specify ranges.** Fetch the full sheet data and index into the response array:

```bash
gws sheets spreadsheets get --params '{"spreadsheetId": "ID", "includeGridData": true, "fields": "sheets.data.rowData.values.textFormatRuns,sheets.data.rowData.values.formattedValue"}'
```

Then parse the `rowData` array:
- `sheets[0].data[0].rowData[row_index].values[col_index]`
- Row index is 0-based (row 2 = index 1)
- Column index is 0-based (col G = index 6)

## Working alternative: values API (no formatting)

When you only need cell text (not strikethrough/bold/color formatting), use the `values get` endpoint instead — it never has this parsing bug:

```bash
gws sheets spreadsheets values get --params '{"spreadsheetId": "ID", "range": "Weekly!G2"}'
```

This returns the formatted text value without `textFormatRuns`.

## Two-tier read strategy

For CC Pipeline orchestrator verification:

1. **Task selection scan** → use `values get` with full columns (e.g. `Weekly!B:G`) for fast text reads
2. **Strikethrough verification** → use `get --includeGridData` without ranges, then index into `rowData` for `textFormatRuns`

This avoids the bug entirely while keeping both paths fast.
