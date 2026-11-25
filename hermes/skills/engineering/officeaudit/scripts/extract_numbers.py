"""Pull every number out of a .pptx or .docx with its location, for /officeaudit deck.

With --model book.xlsx, each number is tied out against the workbook's cached values
(matching at the precision shown, with %, k/m/bn scaling) and marked TIED or UNTIED.
Read-only. Writes <out>/numbers.json and <out>/numbers.md.

Usage: python -X utf8 extract_numbers.py <deck.pptx|report.docx> [--model book.xlsx] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

NUM_RE = re.compile(
    r"(?<![\w.\-])(?P<cur>[$€£¥₫])?\s?(?P<num>-?\d{1,3}(?:,\d{3})+(?:\.\d+)?|-?\d+(?:\.\d+)?)"
    r"\s?(?P<unit>%|pp|bps|x|k|K|m|M|mn|bn|B|million|billion|thousand|trillion|tn"
    r"|MW|MWh|GW|GWh|kW|kWh|TWh|tCO2e?|MtCO2e?|ktCO2e?|t|ha|km|USD|VND|EUR)?(?![\w])"
)
SCALE = {"k": 1e3, "K": 1e3, "thousand": 1e3, "m": 1e6, "M": 1e6, "mn": 1e6, "million": 1e6,
         "bn": 1e9, "B": 1e9, "billion": 1e9, "tn": 1e12, "trillion": 1e12}


def numbers_in(text: str) -> list[dict]:
    out = []
    for m in NUM_RE.finditer(text):
        raw = m.group("num")
        value = float(raw.replace(",", ""))
        decimals = len(raw.split(".")[1]) if "." in raw else 0
        unit = m.group("unit") or ""
        is_year = decimals == 0 and not unit and not m.group("cur") and 1900 <= value <= 2100 and "," not in raw
        out.append({"text": m.group(0).strip(), "value": value, "decimals": decimals,
                    "unit": unit, "currency": m.group("cur") or "", "likely_year": is_year,
                    "low_signal": decimals == 0 and abs(value) <= 10 and not unit and not m.group("cur")})
    return out


def from_pptx(path: Path) -> list[dict]:
    from pptx import Presentation
    items = []
    prs = Presentation(str(path))

    def walk(shapes, slide_no):
        for sh in shapes:
            name = sh.name
            if sh.shape_type == 6:  # group
                walk(sh.shapes, slide_no)
                continue
            if sh.has_text_frame and sh.text_frame.text.strip():
                items.append((f"slide {slide_no} / {name}", sh.text_frame.text))
            if getattr(sh, "has_table", False) and sh.has_table:
                for r, row in enumerate(sh.table.rows, 1):
                    for c, cell in enumerate(row.cells, 1):
                        if cell.text.strip():
                            items.append((f"slide {slide_no} / {name} r{r}c{c}", cell.text))
            if getattr(sh, "has_chart", False) and sh.has_chart:
                for plot in sh.chart.plots:
                    cats = list(plot.categories)
                    for s in plot.series:
                        for i, v in enumerate(s.values):
                            if v is not None:
                                cat = cats[i] if i < len(cats) else i + 1
                                items.append((f"slide {slide_no} / {name} chart '{s.name}' @ {cat}", repr(v)))

    for n, slide in enumerate(prs.slides, 1):
        walk(slide.shapes, n)
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
            items.append((f"slide {n} / notes", slide.notes_slide.notes_text_frame.text))
    return items


def from_docx(path: Path) -> list[dict]:
    import docx
    d = docx.Document(str(path))
    items = [(f"para {i}", p.text) for i, p in enumerate(d.paragraphs, 1) if p.text.strip()]
    for t, table in enumerate(d.tables, 1):
        for r, row in enumerate(table.rows, 1):
            for c, cell in enumerate(row.cells, 1):
                if cell.text.strip():
                    items.append((f"table {t} r{r}c{c}", cell.text))
    return items


def model_values(path: Path) -> list[tuple[str, float]]:
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    vals = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    vals.append((f"{ws.title}!{c.coordinate}", float(v)))
    return vals


def targets(n: dict) -> list[float]:
    """Model values that would display as this number."""
    v, unit = n["value"], n["unit"]
    if unit == "%":
        return [v / 100, v]
    if unit in SCALE:
        return [v * SCALE[unit], v]
    return [v]


def tie(n: dict, vals: list[tuple[str, float]], limit: int = 3) -> list[str]:
    hits = []
    for t in targets(n):
        scale = t / n["value"] if n["value"] else 1
        tol = 0.5 * 10 ** (-n["decimals"]) * abs(scale) + 1e-9
        for ref, v in vals:
            if abs(abs(v) - abs(t)) <= tol:
                hits.append(ref)
                if len(hits) >= limit:
                    return hits
    return hits


def extract(path: Path, model: Path | None = None) -> dict:
    suffix = path.suffix.lower()
    if suffix == ".pptx":
        blocks = from_pptx(path)
    elif suffix == ".docx":
        blocks = from_docx(path)
    else:
        raise SystemExit(f"unsupported file type {suffix}: export Google Slides/Docs to pptx/docx, read PDFs directly")
    vals = model_values(model) if model else None
    rows = []
    for loc, text in blocks:
        for n in numbers_in(text):
            n["location"] = loc
            n["context"] = text.strip().replace("\n", " ")[:160]
            if vals is not None and not n["likely_year"]:
                n["tied_to"] = tie(n, vals)
                n["status"] = "TIED" if n["tied_to"] else "UNTIED"
            rows.append(n)
    summary = {"numbers": len(rows)}
    if vals is not None:
        signal = [r for r in rows if not r["likely_year"] and not r["low_signal"]]
        summary.update(tied=sum(r.get("status") == "TIED" for r in signal),
                       untied=sum(r.get("status") == "UNTIED" for r in signal),
                       model=str(model))
    return {"file": str(path), "summary": summary, "numbers": rows}


def to_markdown(res: dict) -> str:
    s = res["summary"]
    lines = [f"# Numbers in {Path(res['file']).name}", "", "Summary: " + ", ".join(f"{k} {v}" for k, v in s.items()), ""]
    has_tie = "tied" in s
    lines += ["| Location | Number | Status | Model cells | Context |", "|---|---|---|---|---|"] if has_tie else \
             ["| Location | Number | Context |", "|---|---|---|"]
    for r in res["numbers"]:
        ctx = r["context"].replace("|", "/")
        if has_tie:
            status = "year" if r["likely_year"] else ("low-signal " if r["low_signal"] else "") + r.get("status", "")
            lines.append(f"| {r['location']} | {r['text']} | {status} | {', '.join(r.get('tied_to', []))} | {ctx} |")
        else:
            lines.append(f"| {r['location']} | {r['text']} | {ctx} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", type=Path)
    ap.add_argument("--model", type=Path)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    res = extract(a.file, a.model)
    out = a.out or Path(tempfile.mkdtemp(prefix="officeaudit-"))
    out.mkdir(parents=True, exist_ok=True)
    (out / "numbers.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    (out / "numbers.md").write_text(to_markdown(res), encoding="utf-8")
    print(f"{out / 'numbers.md'}\n" + json.dumps(res["summary"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
