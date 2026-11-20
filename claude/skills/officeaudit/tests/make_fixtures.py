"""Rebuild the checked-in fixtures (run once; outputs are committed).

model.xlsx has planted defects; LibreOffice recalculates it so cached values exist,
as they would in a file saved by Excel. deck.pptx and report.docx quote its numbers,
plus one number that ties to nothing.
"""
import shutil
import subprocess
import tempfile
from pathlib import Path

import openpyxl
from docx import Document
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches

HERE = Path(__file__).parent / "fixtures"
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"


def build_model(path: Path):
    wb = openpyxl.Workbook()
    inp = wb.active
    inp.title = "Inputs"
    inp["A2"], inp["B2"] = "Discount rate", 0.08
    inp["A3"], inp["B3"] = "Year-1 revenue", 1500
    inp["A4"], inp["B4"] = "Margin", 0.12
    inp["A5"], inp["B5"] = "Growth", 0.05
    calc = wb.create_sheet("Calc")
    cols = "BCDEF"
    calc["A2"] = "Year"
    for i, c in enumerate(cols):
        calc[f"{c}2"] = 2026 + i
    calc["A3"], calc["B3"] = "Revenue", "=Inputs!B3"
    for prev, c in zip(cols, cols[1:]):
        calc[f"{c}3"] = f"={prev}3*(1+Inputs!$B$5)"
    calc["A4"] = "Profit"
    for c in cols:
        calc[f"{c}4"] = f"={c}3*Inputs!$B$4"
    calc["E4"] = "=E3*0.12"                 # planted: typed margin, breaks the row pattern
    calc["A5"] = "Change"
    for prev, c in zip(cols, cols[1:]):
        calc[f"{c}5"] = f"={c}4-{prev}4"
    calc["D5"] = 42                          # planted: value pasted over a formula
    calc["A7"], calc["B7"] = "Bad ratio", "=C3/0"   # planted: #DIV/0!
    calc["A8"], calc["B8"] = "As of", "=TODAY()"    # planted: volatile
    old = wb.create_sheet("Old")
    old["A1"] = "legacy"
    old.sheet_state = "hidden"               # planted: hidden sheet
    tmp = Path(tempfile.mkdtemp())
    raw = tmp / "model.xlsx"
    wb.save(raw)
    subprocess.run([SOFFICE, "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(tmp / "out"), str(raw)],
                   check=True, capture_output=True, timeout=180)
    shutil.copy2(tmp / "out" / "model.xlsx", path)


def build_deck(path: Path):
    prs = Presentation()
    s1 = prs.slides.add_slide(prs.slide_layouts[1])
    s1.shapes.title.text = "Revenue reaches 1,823 by 2030"
    s1.placeholders[1].text = "Margin held at 12%\nYear-1 revenue $1,500\nPayback 7.3 years"
    s2 = prs.slides.add_slide(prs.slide_layouts[5])
    s2.shapes.title.text = "Profit by year"
    tbl = s2.shapes.add_table(2, 2, Inches(1), Inches(2), Inches(4), Inches(1)).table
    tbl.cell(0, 0).text, tbl.cell(0, 1).text = "2026", "180"
    tbl.cell(1, 0).text, tbl.cell(1, 1).text = "2027", "189.0"
    data = CategoryChartData()
    data.categories = ["2026", "2027"]
    data.add_series("Revenue", (1500, 1575))
    s2.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(5), Inches(2), Inches(4), Inches(3), data)
    prs.save(path)


def build_report(path: Path):
    d = Document()
    d.add_paragraph("Revenue grows 5% a year from $1.5 k in 2026.")
    d.add_paragraph("Emissions fall by 3.2 MtCO2e.")
    t = d.add_table(rows=1, cols=2)
    t.cell(0, 0).text, t.cell(0, 1).text = "Discount rate", "8%"
    d.save(path)


if __name__ == "__main__":
    HERE.mkdir(exist_ok=True)
    build_model(HERE / "model.xlsx")
    build_deck(HERE / "deck.pptx")
    build_report(HERE / "report.docx")
    print("fixtures written to", HERE)
