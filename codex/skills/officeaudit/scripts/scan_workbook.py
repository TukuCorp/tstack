"""Deterministic first pass over an .xlsx/.xlsm workbook for /officeaudit model.

Read-only: opens the workbook twice (formulas and cached values) and never saves it.
Writes <out>/scan.json (all findings) and <out>/scan.md (summary, capped per kind).

Usage: python -X utf8 scan_workbook.py <workbook> [--out DIR] [--recalc]
--recalc first recalculates a temporary copy with LibreOffice (soffice) when the file
has formulas without cached values; the original is never touched.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import openpyxl
from openpyxl.formula.translate import Translator
from openpyxl.utils import get_column_letter

ERRORS = {"#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NUM!", "#NULL!", "#SPILL!", "#CALC!"}
VOLATILE = ("NOW", "TODAY", "RAND", "RANDBETWEEN", "OFFSET", "INDIRECT", "CELL", "INFO")
# Literals this common are rarely a buried assumption (unit factors, percent, months).
BENIGN_LITERALS = {"0", "1", "2", "100", "12", "1000", "-1"}
SEVERITY = {
    "error_value": "high", "ref_error_in_formula": "high", "external_link": "high",
    "inconsistent_formula": "high", "constant_in_formula_run": "medium",
    "hardcoded_literal": "medium", "volatile_function": "low", "uncalculated": "medium",
    "hidden_sheet": "low", "broken_defined_name": "high",
}
MD_CAP = 40

STRING_RE = re.compile(r'"(?:[^"]|"")*"')
SHEET_PREFIX_RE = re.compile(r"(?:'(?:[^']|'')+'|[A-Za-z_][\w.]*)!")
REF_RE = re.compile(r"\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?|\$?[A-Z]{1,3}:\$?[A-Z]{1,3}|\$?\d+:\$?\d+")
FUNC_RE = re.compile(r"\b[A-Z][A-Z0-9.]*\(")
NAME_RE = re.compile(r"\b[A-Za-z_][\w.]*\b")
NUM_RE = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?%?")


def literals_in(formula: str) -> list[str]:
    """Numeric literals typed into a formula, after removing strings, refs and names."""
    f = STRING_RE.sub(" ", formula[1:] if formula.startswith("=") else formula)
    f = SHEET_PREFIX_RE.sub(" ", f)
    f = REF_RE.sub(" ", f)
    f = FUNC_RE.sub("(", f)
    f = NAME_RE.sub(lambda m: " " if not m.group(0)[0].isdigit() else m.group(0), f)
    return [n for n in NUM_RE.findall(f) if n.rstrip("%") not in BENIGN_LITERALS]


def volatile_in(formula: str) -> list[str]:
    up = STRING_RE.sub(" ", formula).upper()
    return [fn for fn in VOLATILE if re.search(rf"\b{fn}\(", up)]


def rel_key(formula: str, coord: str, anchor: str) -> str:
    """Formula translated to a common anchor cell; equal keys mean 'same formula, shifted'."""
    try:
        return Translator(formula, origin=coord).translate_formula(anchor)
    except Exception:  # unparsable formula: compare raw text
        return formula


def is_formula(v) -> bool:
    return isinstance(v, str) and v.startswith("=")


def is_number(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def runs(cells: list[tuple[str, object]]):
    """Split an ordered row/column of (coord, value) into runs of non-empty cells."""
    run = []
    for coord, v in cells:
        if v is None or v == "":
            if run:
                yield run
            run = []
        else:
            run.append((coord, v))
    if run:
        yield run


def check_run(run, sheet, axis, issues):
    formulas = [(c, v) for c, v in run if is_formula(v)]
    if len(formulas) < 3:
        return
    anchor = run[0][0]
    keys = {c: rel_key(v, c, anchor) for c, v in formulas}
    common, count = Counter(keys.values()).most_common(1)[0]
    if count >= 3 and count / len(formulas) >= 2 / 3:
        example = next(v for c, v in formulas if keys[c] == common)
        for c, v in formulas:
            if keys[c] != common:
                issues.append(issue(sheet, c, "inconsistent_formula",
                                    f"{v} differs from its {axis} neighbours (pattern of {example})"))
    # A typed number sitting between formulas in the same run: a pasted-over value.
    for i in range(1, len(run) - 1):
        c, v = run[i]
        if is_number(v) and is_formula(run[i - 1][1]) and is_formula(run[i + 1][1]):
            issues.append(issue(sheet, c, "constant_in_formula_run",
                                f"typed value {v} between formulas along the {axis}"))


def issue(sheet, cell, kind, detail):
    return {"sheet": sheet, "cell": cell, "kind": kind, "severity": SEVERITY[kind], "detail": detail}


def recalc_copy(path: Path, tmp: Path) -> Path | None:
    soffice = shutil.which("soffice") or r"C:\Program Files\LibreOffice\program\soffice.exe"
    if not Path(soffice).exists() and not shutil.which("soffice"):
        return None
    src = tmp / ("src" + path.suffix)
    shutil.copy2(path, src)
    out = tmp / "out"
    subprocess.run([soffice, "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(out), str(src)],
                   check=True, capture_output=True, timeout=180)
    res = out / "src.xlsx"
    return res if res.exists() else None


def scan(path: Path, recalc: bool = False) -> dict:
    wb_f = openpyxl.load_workbook(path, data_only=False)
    values_path = path
    tmpdir = None
    wb_v = openpyxl.load_workbook(path, data_only=True)
    issues: list[dict] = []
    stats = {"sheets": [], "formula_cells": 0, "uncalculated": 0, "recalculated_copy": False}

    def count_uncached():
        n = 0
        for ws in wb_f.worksheets:
            wv = wb_v[ws.title]
            for row in ws.iter_rows():
                for c in row:
                    if is_formula(c.value) and wv[c.coordinate].value is None:
                        n += 1
        return n

    if recalc and count_uncached():
        tmpdir = tempfile.TemporaryDirectory()
        copy = recalc_copy(path, Path(tmpdir.name))
        if copy:
            wb_v = openpyxl.load_workbook(copy, data_only=True)
            values_path = copy
            stats["recalculated_copy"] = True

    for ws in wb_f.worksheets:
        wv = wb_v[ws.title]
        n_formulas = 0
        if ws.sheet_state != "visible":
            issues.append(issue(ws.title, "-", "hidden_sheet", f"sheet is {ws.sheet_state}"))
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                cached = wv[c.coordinate].value
                if isinstance(cached, str) and cached in ERRORS:
                    issues.append(issue(ws.title, c.coordinate, "error_value",
                                        f"shows {cached}" + (f" from {v}" if is_formula(v) else "")))
                if not is_formula(v):
                    continue
                n_formulas += 1
                if cached is None:
                    stats["uncalculated"] += 1
                if "#REF!" in v:
                    issues.append(issue(ws.title, c.coordinate, "ref_error_in_formula", v))
                if re.search(r"\[[^\]]+\]", STRING_RE.sub("", v)):
                    issues.append(issue(ws.title, c.coordinate, "external_link", v))
                lits = literals_in(v)
                if lits:
                    issues.append(issue(ws.title, c.coordinate, "hardcoded_literal",
                                        f"{v} (typed numbers: {', '.join(lits)})"))
                vol = volatile_in(v)
                if vol:
                    issues.append(issue(ws.title, c.coordinate, "volatile_function", f"{v} ({', '.join(vol)})"))
        stats["formula_cells"] += n_formulas
        stats["sheets"].append({"name": ws.title, "state": ws.sheet_state,
                                "dims": ws.dimensions, "formulas": n_formulas})
        grid = defaultdict(dict)
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    grid[c.row][c.column] = c.value
        if grid:
            max_r = max(grid)
            max_c = max(max(cols) for cols in grid.values())
            for r in range(1, max_r + 1):
                cells = [(f"{get_column_letter(k)}{r}", grid[r].get(k)) for k in range(1, max_c + 1)]
                for run in runs(cells):
                    check_run(run, ws.title, "row", issues)
            for k in range(1, max_c + 1):
                cells = [(f"{get_column_letter(k)}{r}", grid[r].get(k)) for r in range(1, max_r + 1)]
                for run in runs(cells):
                    check_run(run, ws.title, "column", issues)

    for name, dn in getattr(wb_f.defined_names, "items", lambda: [])():
        if "#REF!" in str(dn.attr_text):
            issues.append(issue("-", name, "broken_defined_name", str(dn.attr_text)))
    if stats["uncalculated"]:
        issues.append(issue("-", "-", "uncalculated",
                            f"{stats['uncalculated']} formula cells have no cached value; "
                            "rerun with --recalc or open and save in Excel before trusting values"))
    seen, unique = set(), []
    for i in issues:
        key = (i["sheet"], i["cell"], i["kind"])
        if key not in seen:
            seen.add(key)
            unique.append(i)
    order = {"high": 0, "medium": 1, "low": 2}
    unique.sort(key=lambda i: (order[i["severity"]], i["kind"], i["sheet"], i["cell"]))
    if tmpdir:
        tmpdir.cleanup()
    return {"workbook": str(path), "values_from": "recalculated copy" if values_path != path else "cached values",
            "stats": stats, "counts": dict(Counter(i["kind"] for i in unique)), "issues": unique}


def to_markdown(res: dict) -> str:
    s = res["stats"]
    lines = [f"# Workbook scan: {Path(res['workbook']).name}", "",
             f"Formula cells: {s['formula_cells']} | values from: {res['values_from']} | "
             f"uncalculated: {s['uncalculated']}", "", "| Sheet | State | Range | Formulas |", "|---|---|---|---|"]
    lines += [f"| {x['name']} | {x['state']} | {x['dims']} | {x['formulas']} |" for x in s["sheets"]]
    lines += ["", "| Finding | Count |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k, v in sorted(res["counts"].items())]
    by_kind = defaultdict(list)
    for i in res["issues"]:
        by_kind[i["kind"]].append(i)
    for kind, items in by_kind.items():
        lines += ["", f"## {kind} ({items[0]['severity']})"]
        lines += [f"- `{i['sheet']}!{i['cell']}`: {i['detail']}" for i in items[:MD_CAP]]
        if len(items) > MD_CAP:
            lines.append(f"- ... {len(items) - MD_CAP} more in scan.json")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("workbook", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--recalc", action="store_true")
    a = ap.parse_args(argv)
    res = scan(a.workbook, a.recalc)
    out = a.out or Path(tempfile.mkdtemp(prefix="officeaudit-"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "scan.json").write_text(json.dumps(res, indent=1, default=str), encoding="utf-8")
    (out / "scan.md").write_text(to_markdown(res), encoding="utf-8")
    print(f"{out / 'scan.md'}\n" + json.dumps(res["counts"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
