# /officeaudit deck

First-pass QC of a deck, memo or report before it circulates. Every number, unit, footnote, chart and conclusion should trace to a source or a model output. This is a QC pass, not a sign-off for external circulation; say so in the verdict line when the deck is going outside the firm.

## 1. Classify

Name the deliverable (board or IC deck, donor or client report, grant proposal, briefing note, workshop slides) and its audience. Identify the controlling file and its sources: usually the deck is the output and a workbook, a prior report or a dataset is the source. Ask for the source model if numbers clearly come from one and none was given; without it, the audit can only check internal consistency, which caps the verdict at `Ready with caveats`.

## 2. Extract numbers

```
python -X utf8 C:/Users/<USER>/.config/opencode/skills/officeaudit/scripts/extract_numbers.py <deck.pptx|report.docx> [--model <book.xlsx>]
```

It lists every number with its location (slide and shape, table cell, chart series point, notes; or paragraph and table cell) and unit. With `--model`, each is marked `TIED` (some cell in the workbook shows that value at the precision displayed, allowing % and k/m/bn scaling) or `UNTIED`. Years are skipped; small bare integers are marked low-signal.

Read the result critically:
- `UNTIED` is a lead, not a verdict: the number may come from another source, be derived (a difference of two cells), or be wrong. Check each one that matters.
- `TIED` only means a matching value exists somewhere. For headline numbers, confirm it is the right cell (right year, right scenario, right sheet), not a coincidental match.
- Charts: series values come from the chart's embedded data. If the chart was pasted as a picture, the extractor cannot see it; read it from the slide image.

For PDFs, or images of tables, read the file and list the numbers by page yourself.

## 3. Checks

1. **Tie-out**: headline and decision numbers match the source, at the stated rounding, for the right period and scenario.
2. **Internal consistency**: the same figure is identical everywhere it appears (summary vs body vs appendix vs chart); totals add up; percentages match their base; growth rates match the start and end values.
3. **Baselines**: every change or comparison names what it is measured against. "+32%" is incomplete; "+32% YoY" or "+32% vs plan" is complete. Check the baseline period too: a Covid year, a one-off quarter, a seasonal peak, or a window that starts at a trough flatters the change. Flag the comparison and name the fairer baseline.
4. **Units and labels**: units stated and consistent (MW/MWh, tCO2e/MtCO2e, USD/VND, real/nominal, year basis); chart axes labelled; footnotes and sources present and dated.
5. **Staleness**: data dates, FX rates, tariffs and policy references are current for the audience; flag anything older than the decision needs. A headline number with no "as of" date is a finding.
6. **Claims**: each conclusion follows from the numbers shown; flag a claim the data does not support, or support that is only asserted. A quantitative claim with no number behind it ("strong traction", "healthy pipeline", "significant savings") is a finding: give the figure or soften the claim.
7. **Hygiene** (minor unless it misleads): typos in numbers, inconsistent decimals, leftover placeholder text, wrong slide numbers in cross-references.

Route model-level problems (a wrong formula behind a number) to `/officeaudit model` rather than solving them here.

## 4. Report

```
## Deck QC: <file> — <Ready | Ready with caveats | Not ready | Not assessable>
<one-line reason> | Audience: <x> | Source model: <file or none> | Numbers: <n> (<tied> tied, <untied> untied)

| # | Severity | Status | Location | Finding | Fix |
|---|---|---|---|---|---|
| 1 | critical | confirmed | slide 1 / title | "1,823" is 2030 revenue but the title says 2029 | change the year or the value |

### Untied numbers that matter
<location, number, what it should tie to, result of the check>

### Consistency
<figures that appear more than once and disagree>
```

Edits to the deck, if asked, go to a copy, changing only the listed items.
