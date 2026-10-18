---
name: excel-automation
description: Automate live Excel via xlwings — drive an open workbook in real time, run VBA macros, build charts and tables, refresh pivots and queries, export PDFs, and write UDFs. Use for "/excel-automation", live Excel dashboards, VBA execution, or Excel work needing a running Excel instance. Not for file-only .xlsx edits with Excel closed; use the xlsx or officecli skill for those.
user-invocable: true
---

# Excel Automation (xlwings)

Drive a running desktop Excel from Python with **xlwings**: read and write a
workbook the user has open, run VBA, refresh charts and data, export PDFs, and
write UDFs. Requires Windows (or macOS) with Excel installed.

```bash
python -m pip install xlwings
xlwings addin install        # only needed for UDFs / calling Python from Excel
```

## Connect

```python
import xlwings as xw

# The user's running Excel. Check before touching books.active.
if xw.apps.count == 0:
    raise RuntimeError("Excel is not running; ask the user to open the workbook")
wb = xw.books['Budget.xlsx']   # by name; xw.books.active is whatever the user last clicked
sheet = wb.sheets['Sheet1']    # or wb.sheets[0]

# A separate hidden instance for batch work (never shows the user's books)
app = xw.App(visible=False, add_book=False)
wb = app.books.open(r'C:\full\path\file.xlsx')
new_wb = app.books.add()       # not xw.Book(): that targets the active (user's) app
```

## Live Workbook Safety

- Never `quit()` or `kill()` an App you did not create. `xw.apps.active` is the
  user's Excel with their unsaved work.
- Check `xw.apps.count` before `xw.books.active`, and prefer selecting the
  workbook by name.
- Before writing to a workbook the user has open, confirm with the user or save
  a backup first: `wb.api.SaveCopyAs(r'C:\full\path\Budget.backup.xlsx')`
  (writes a copy, leaves the open workbook untouched).
- Change `display_alerts`, `screen_updating`, and `calculation` only inside
  `try`, and restore the saved values in `finally`.
- After writing, read the cells back and compare. Excel coerces values (ints
  return as floats, dates as `datetime`, leading zeros dropped).

```python
app = wb.app
saved = (app.display_alerts, app.screen_updating, app.calculation)
try:
    app.display_alerts = False
    app.screen_updating = False
    app.calculation = 'manual'
    sheet['A2'].value = rows               # one 2D write, never cell by cell
    app.calculate()
finally:
    app.display_alerts, app.screen_updating, app.calculation = saved
written = sheet['A2'].resize(len(rows), len(rows[0])).options(ndim=2).value
assert written == rows, written
```

## Ranges And Formatting

```python
import pandas as pd

sheet['A1'].value = 'Hello'
sheet['A1:C2'].value = [[1, 2, 3], [4, 5, 6]]
block = sheet['A1'].expand().value                         # connected block
df = sheet['A1'].options(pd.DataFrame, expand='table', index=False).value
sheet['E1'].options(index=False).value = df                # write a DataFrame
last_row = sheet.range((sheet.cells.last_cell.row, 1)).end('up').row

sheet['A1'].font.bold = True
sheet['A1'].color = (255, 255, 0)
sheet['B:B'].number_format = '#,##0.00'
sheet['A:D'].autofit()
```

## Charts, Tables, Refresh

```python
chart = sheet.charts.add(left=300, top=10, width=400, height=250)
chart.set_source_data(sheet['A1'].expand())
chart.chart_type = 'line'

table = sheet.tables.add(source=sheet['A1'].expand(), name='Sales')
table.update(df, index=False)      # replace the table body, resizing it
```

- xlwings has no `table.refresh()` or `chart.refresh()`. Charts redraw when
  their source cells change. To force a redraw on Windows use
  `chart.api[1].Refresh()` (`chart.api` is a `(ChartObject, Chart)` tuple).
- Existing pivot tables, Power Query tables and other connections:
  `wb.api.RefreshAll()`, then `wb.app.api.CalculateUntilAsyncQueriesDone()` and
  `wb.app.calculate()`. Do not call `table.api.Refresh()`; `ListObject.Refresh`
  only works for SharePoint-linked lists.

## VBA

```python
total = wb.macro('Module1.CalculateTotal')(100, 200)   # returns the VBA return value
```

The workbook must be `.xlsm` (or the macro in an open add-in) and macros must be
enabled. Reading or writing VBA code through `wb.api.VBProject` also needs
File > Options > Trust Center > Trust Center Settings > Macro Settings >
**Trust access to the VBA project object model**; without it COM raises
"Programmatic access to Visual Basic Project is not trusted". Ask the user to
tick it; do not change it from a script.

## UDFs

```python
import xlwings as xw

@xw.func
@xw.arg('data', ndim=2)
def total(data):
    return sum(v for row in data for v in row if isinstance(v, (int, float)))
```

Put the module next to the workbook (or list it under UDF Modules in the
xlwings ribbon tab), then click **Import Functions**. The function becomes
`=total(A1:C10)`.

## Export And Save

Use absolute paths for every open, save and export. Excel resolves relative
paths against its own current directory (usually Documents), not your shell's.

```python
pdf = r'C:\full\path\report.pdf'
sheet.api.ExportAsFixedFormat(0, pdf)    # 0 = xlTypePDF; sheet.to_pdf(pdf) also works
wb.save(r'C:\full\path\report.xlsx')
```

## Batch Over Files (Hidden App)

```python
from pathlib import Path
import xlwings as xw

app = xw.App(visible=False, add_book=False)
try:
    app.display_alerts = False
    summary = app.books.add()
    out = summary.sheets[0]
    out['A1'].value = ['File', 'Total Sales']
    row = 2
    for path in Path(r'C:\data\sales').glob('*.xlsx'):
        wb = None
        try:
            wb = app.books.open(str(path), read_only=True)
            ws = wb.sheets['Sales']
            last = ws.range((ws.cells.last_cell.row, 2)).end('up').row
            col = ws.range((2, 2), (max(last, 2), 2)).options(ndim=1).value
            out[f'A{row}'].value = [path.name, sum(v for v in col if isinstance(v, (int, float)))]
            row += 1
        finally:
            if wb is not None:
                wb.close()
    summary.save(r'C:\data\sales\summary.xlsx')
finally:
    app.quit()    # safe: this script created the app
```

Bound COM calls such as `SpecialCells` to a real range (`ws.used_range.api`),
never a whole column, and catch the COM error it raises when no cells match.

## Gotchas

- A cell in edit mode or an open Excel dialog blocks COM ("Call was rejected by
  callee"). Ask the user to press Esc, then retry.
- A script that dies before `app.quit()` leaves a hidden `EXCEL.EXE`. Clean up
  only instances your script started (`app.pid`), never the user's.
- Not for servers or headless machines: xlwings needs an interactive desktop
  session with Excel.
