#!/usr/bin/env python3
"""Render a .pptx to per-slide PNGs for visual QA.

Usage:
    python render_deck.py "deck.pptx" [out_dir] [--dpi 110] [--slides 6,9,12]

Requires LibreOffice (soffice) for pptx->pdf and PyMuPDF (fitz) for pdf->png.
Always eyeball the PNGs after a build: in-place edits keep the original box
sizes, so replaced text can overflow or collide with images placed below it.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF


SOFFICE_CANDIDATES = [
    "soffice",
    "libreoffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
]


def find_soffice():
    for c in SOFFICE_CANDIDATES:
        if shutil.which(c) or Path(c).exists():
            return c
    raise SystemExit("LibreOffice (soffice) not found; install it or add to PATH.")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python render_deck.py <deck.pptx> [out_dir] [--dpi N] [--slides a,b,c]")
        sys.exit(1)
    deck = Path(args[0]).resolve()
    out = Path(args[1]).resolve() if len(args) > 1 else deck.parent / "render"
    dpi = int(sys.argv[sys.argv.index("--dpi") + 1]) if "--dpi" in sys.argv else 110
    only = None
    if "--slides" in sys.argv:
        only = {int(x) for x in sys.argv[sys.argv.index("--slides") + 1].split(",")}

    out.mkdir(parents=True, exist_ok=True)
    soffice = find_soffice()
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out), str(deck)],
        check=True,
    )
    pdf = out / (deck.stem + ".pdf")
    doc = fitz.open(str(pdf))
    n = 0
    for i, page in enumerate(doc):
        if only is not None and i not in only:
            continue
        page.get_pixmap(dpi=dpi).save(str(out / f"slide-{i:02d}.png"))
        n += 1
    print(f"Rendered {n} slide(s) -> {out}")


if __name__ == "__main__":
    main()
