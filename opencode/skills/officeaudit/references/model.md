# /officeaudit model

Audit an existing spreadsheet model and say what it can safely be used for. Do not rebuild it.

## 1. Mandate

Settle, from the request or the file, and ask only for what is missing and matters:
- what the model is for (investment case, tariff or subsidy design, GHG inventory, budget, grant application) and who will use the output;
- which outputs drive the decision (IRR, NPV, LCOE, payback, emissions, funding gap, budget total);
- a materiality threshold (default: anything that moves a decision output by 1% or more, or changes a quoted figure as rounded).

## 2. Scan

```
python -X utf8 C:/Users/<USER>/.config/opencode/skills/officeaudit/scripts/scan_workbook.py <file.xlsx>
```

It writes `scan.md` (summary) and `scan.json` (every finding with sheet, cell and kind). Kinds:
- `error_value`: a cell showing #REF!, #DIV/0!, #N/A, etc.
- `ref_error_in_formula`, `broken_defined_name`: references to deleted cells.
- `external_link`: a formula that reads another workbook (breaks when shared).
- `inconsistent_formula`: a formula that breaks the pattern of its row or column neighbours. The most common cause of silent errors; read every one.
- `constant_in_formula_run`: a typed number between formulas (a value pasted over a formula).
- `hardcoded_literal`: a number typed inside a formula (`=E3*0.12`): an assumption hidden from the inputs sheet.
- `volatile_function`: NOW, TODAY, RAND, OFFSET, INDIRECT: results change on recalculation or are hard to trace.
- `hidden_sheet`, `uncalculated`.

If `uncalculated` is reported (saved without cached values, e.g. written by a script), rerun with `--recalc`, which recalculates a temporary copy with LibreOffice. LibreOffice may evaluate some Excel functions differently; say so when relying on those values.

The scan is a starting point. A finding can be intentional (a hardcoded 1.1 VAT factor with a label next to it); downgrade it with a reason rather than dropping it silently.

## 3. Read the model

With the scan in hand, read the structure: inputs, calculation and output sheets, and how they link. Check:
- **Flow**: inputs live in one place and are referenced, not retyped; outputs trace back to inputs without loops or manual overrides.
- **Assumptions**: each key driver (price, tariff, capacity factor, growth, discount rate, emission factor, FX rate) has a source, a date and a unit. Unsourced or stale drivers are findings even when the formulas are clean.
- **Units and time**: MW vs MWh, real vs nominal, VND vs USD, annual vs monthly, sign conventions, year columns aligned across sheets.
- **Totals**: subtotals sum to totals; balance or check rows are zero; percentages sum to 100% where they should.
- **Decision layer**: the outputs the decision needs exist and are linked. A clean operating model without the decision output is `Not ready` for that decision, not "fine".

Separate "the model is broken" (mechanics) from "the model is unsupported" (assumptions) from "the model is stale" (old inputs). They need different fixes and different owners.

## 4. Tie-out ledger

For each decision output: value, cell, what it depends on (two or three key inputs with cells), and its source status (sourced / assumption / unknown). Note any output that changes by more than the threshold under a plausible input error; that is where a reviewer should look first.

## 5. Report

```
## Model audit: <file> — <Ready | Ready with caveats | Not ready | Not assessable>
<one-line reason> | Purpose: <x> | Decision outputs: <list with values>

| # | Severity | Status | Location | Finding | Fix |
|---|---|---|---|---|---|
| 1 | critical | confirmed | Calc!E4 | =E3*0.12 types the margin instead of Inputs!$B$4; 2029 profit ignores the input | link to Inputs!$B$4 |

### Tie-out ledger
| Output | Value | Cell | Driven by | Source status |

### Scan summary
<counts by kind; what was checked and dismissed, with reasons>
```

Fixes are suggestions. If asked to apply them, work on a copy (`<stem>-audited.xlsx`), change only the listed cells, and re-run the scan on the copy to show the findings are gone.
