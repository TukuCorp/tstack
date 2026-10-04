# Reading a measured architectural plan out of a PDF

The contractor's sheets are CAD exports: dimension text is exploded vector
curves, so `page.get_text()` returns **zero characters** even though the sheet is
covered in numbers. OCR and `web_extract` have nothing to work with. The numbers
have to be read visually and then confirmed by measuring the linework.

## 1. Inventory the sheet

```python
import fitz
doc = fitz.open("contractor/MB 2-3-4-Model.pdf")
for i, p in enumerate(doc):
    print(i, p.rect, len(p.get_text()), len(p.get_drawings()))
```

Expect `len(text) == 0` and tens of thousands of drawing items. Also check how
many plans the page carries — these sheets put two plans side by side (left =
typical floors, right = a different floor). **They are not identical**; crop the
one you are studying and label your crops so you do not mix them.

## 2. Calibrate millimetres per point

The printed scale (1/100) is nominal — the sheet is plotted to fit the page, so
derive the factor from a dimension you can also measure:

```
# find the two wall faces a printed dimension refers to, read their pt distance,
# then:  K = printed_mm / measured_pt        (43.0 mm per pt on the MB 2-3-4 set)
```

Re-derive per sheet; do not carry a factor across sheets. Record it in the
project's `designs/<slug>.measurements.md` so the next session does not redo it.

## 3. Crop by plan millimetres, not by pixels

Establish a datum (the outermost wall on that axis) and its pt coordinate, then
convert: `pt = datum_pt ± mm / K` (the sign depends on whether the axis runs up or
down the page). Write one helper that takes plan mm and returns a `fitz.Rect`, and
specify every crop in plan mm from then on — it keeps the crop and the dimension
chain in the same frame of reference.

```python
pm = page.get_pixmap(matrix=fitz.Matrix(10, 10), clip=rect_pt)   # 10x for digits
pm.save("band_10x.png")
```

Render the page at ~300 dpi for overview crops, and read **numbers** at 8–12×.

## 4. Read it, one band at a time

Ask vision for the printed chain **in sequence from a named datum**, plus the
door and window positions in that band. One band per read — a whole-page read
returns plausible garbage for digits. Keep each review image ≤ ~1500 px on the
long edge; downscale to JPEG if a read stalls.

## 5. Confirm with the vector linework

```python
items = page.get_drawings()
# walls show up as peaks in a length-weighted histogram of horizontal/vertical
# segments; build separate histograms for the two axes and look for peaks.
```

- A wall is usually a pair of parallel lines ~200 mm apart with fill between
  them. Hatch-filled walls may have `fill` set and a thin stroke — **do not filter
  on stroke width or `fill is None`** while hunting for walls, you will drop the
  ones carrying the hatch.
- Peak spacing is the fastest sanity check on a printed chain: if the printed
  numbers imply a wall at 4900 and the histogram has a line pair at 4850/4950, the
  printed number is probably to face and the line pair is the wall.

## 6. Reconcile, then record

Compare the printed chain against the model as a sequence (see SKILL.md step 3).
Write what you measured and the factor you derived into the project's measurement
file, including any unresolved model-vs-sheet mismatch — a future session must not
have to rediscover it.

## Traps seen in practice

- A dimension chain that does not close (parts ≠ overall) is usually a
  face-vs-centreline datum on the wall thicknesses, not a misread.
- Vision will read a room name from a neighbouring room if the crop is tight and
  the label sits outside it; ask for the label position, not just the text.
- A crop taken from the wrong plan of the two shows a familiar-but-wrong chain.
  Note in your own scratch which plan each crop came from.
