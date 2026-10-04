#!/usr/bin/env python3
"""Dump a .pptx/.ppt shape inventory so content can be replaced in place.

Usage:
    python inspect_template.py "path/to/template.pptx" [--slide N]

For every slide it prints each shape's index, type, geometry (inches), and the
current text. Use the printed indices to target replacements in the build
script (set_text / delete_shape / add_picture_cover at the existing positions).
"""
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Emu


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python inspect_template.py <template.pptx> [--slide N]")
        sys.exit(1)
    path = Path(args[0])
    only = None
    if "--slide" in sys.argv:
        only = int(sys.argv[sys.argv.index("--slide") + 1])

    prs = Presentation(str(path))
    w = Emu(prs.slide_width).inches
    h = Emu(prs.slide_height).inches
    print(f"FILE: {path.name}")
    print(f"SLIDE SIZE: {w:.2f} x {h:.2f} in  |  SLIDES: {len(prs.slides)}\n")

    for si, slide in enumerate(prs.slides):
        if only is not None and si != only:
            continue
        print(f"=== SLIDE {si}  ({len(slide.shapes)} shapes) ===")
        for i, sh in enumerate(slide.shapes):
            st = str(sh.shape_type).split()[0] if sh.shape_type is not None else "?"
            try:
                x, y = Emu(sh.left).inches, Emu(sh.top).inches
                sw, sh_ = Emu(sh.width).inches, Emu(sh.height).inches
                geo = f"x={x:5.2f} y={y:5.2f} w={sw:5.2f} h={sh_:5.2f}"
            except Exception:
                geo = "geo=n/a"
            txt = ""
            if sh.has_text_frame:
                txt = sh.text_frame.text.replace("\n", " / ").replace("\x0b", " / ")[:70]
            img = " [IMAGE]" if st == "PICTURE" else ""
            print(f"  [{i:2}] {st:11} {geo}{img}  txt={txt!r}")
        print()


if __name__ == "__main__":
    main()
