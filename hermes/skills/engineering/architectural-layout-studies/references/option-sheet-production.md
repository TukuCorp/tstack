# Producing the option sheet

The artifact the user picks from: **one A3 landscape page, N panels side by side at
one scale, over the real as-drawn geometry**, plus a separate as-drawn base sheet
with the dimension chains.

## Panel transform

Keep the plan's own millimetre coordinates (model mm, y growing toward the rear)
and let one `Panel` object map a world window onto a sheet rect. Never hand-flip
signs in the drawing code — one flip in one place is where the bugs live.

```
s = min(dst_w / win_w, dst_h / win_h)      # sheet mm per world mm
true scale = round(1 / s)                  # report THIS; the printed 1:50 is nominal
```

At an A3 panel of ~95 × 150 mm you get roughly 1:55–1:60 for a 3.5 × 7.5 m window.
Quote the real scale on the sheet.

## Draw order, per panel

1. Room tints (very pale) — a reader needs to see where one room stops.
2. Fixtures and furniture, drawn at real sizes (bed 1600×2000, desk 650 deep,
   wardrobe 600 deep, WC set).
3. Walls, solid filled, as they exist.
4. Door and window openings cut OUT of the wall band (white rect over the band),
   then the leaf line.
5. **New work last, in the accent colour** — the partition, glazing or curtain is
   the only thing the user is comparing between panels.
6. Labels, then the caption block.

Dimension chains go on the base sheet only — on the four option panels they crowd
the furniture out of the drawing.

## Labels and captions

- Fixed sheet-mm sizes (~1.5–2.6). One short line per zone. Centre on free floor,
  never on furniture.
- Each panel: a title ≤ ~38 characters (longer titles clip at the panel edge), then
  a caption of "what is built → what it wins → `Costs:` …".
- Area in m² per zone, computed from clear dimensions (wall thickness dropped).
- A legend line for the accent colour, and one for what is existing.

## Rasterising without a browser

PyMuPDF reads SVG directly — no Chrome, Inkscape or cairosvg needed:

```python
import fitz
from PIL import Image
d = fitz.open("sheet.svg")
pm = d[0].get_pixmap(matrix=fitz.Matrix(4, 4))     # ~350 dpi on A3
pm.save("sheet_print.png")
im = Image.open("sheet_print.png").convert("RGB")
im.resize((1900, int(im.size[1] * 1900 / im.size[0]))).save("sheet_web.png")
```

4× for the print/deliverable copy, 8× only to inspect a detail.

## Self-review loop (before delivering)

Crop the sheet in halves and read each with a **defect-only** prompt. The
checklist that has actually caught things:

1. any text clipped at a page edge or inside its own box;
2. labels overlapping furniture, walls or each other;
3. furniture crossing a wall, a door opening, or another furniture symbol;
4. the new partition not reaching wall to wall;
5. anything spilling outside the panel frame into the caption block;
6. does the caption describe what is actually drawn.

Fix, re-render, re-read. Two passes is normally enough. Expect one soft false
positive per pass — a partition drawn to the interior wall face reads as
"not connected", and a door leaf drawn without its arc reads as "missing swing".
Verify the numbers before changing a drawing that is right.

## Conventions that read well

- Accent (orange) reserved for new work only; existing walls dark and solid.
- Glass = blue double line; curtain/divider = dashed; existing fixtures grey.
- Faint 500 mm grid behind the plan for scale by eye.
- A white label box behind dimension text so lines never run through digits.
- Sheet furniture is schematic but **to scale** — a bed drawn 1600 wide is what
  makes the clearance argument on the sheet.
