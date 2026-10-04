"""Scaled plan-sheet generator — copy beside the study's outputs and edit.

Sheet space: millimetres on an A3 landscape page (420 x 297).
World space: the plan's own millimetres (model space, y grows toward the rear).
A Panel maps one world window onto one rect on the sheet, flipping y once.

Workflow: edit GEOMETRY / the draw function / the build_sheet call at the bottom,
then
    python panel_plan_sheet.py      ->  sheet.svg + sheet_print.png + sheet_web.png

See references/option-sheet-production.md for the draw order and the self-review
loop that must follow every regeneration.
"""
from __future__ import annotations

import math
import os

A3W, A3H = 420.0, 297.0
INK, WALL, GLASS, NEW, SOFT = "#1b1b1b", "#3a3a3a", "#2f6fd0", "#e2711d", "#cfd4d8"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Sheet:
    def __init__(self, w: float = A3W, h: float = A3H, bg: str = "#ffffff"):
        self.w, self.h, self.parts = w, h, []
        self.parts.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="{bg}"/>')

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=0.2, dash=None, op=1.0):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{d}/>')

    def line(self, x1, y1, x2, y2, stroke=INK, sw=0.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill="none", stroke=INK, sw=0.2):
        self.parts.append(
            f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def poly(self, pts, stroke=INK, sw=0.2, fill="none", dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
        self.parts.append(f'<polyline points="{p}" fill="{fill}" stroke="{stroke}" '
                          f'stroke-width="{sw}"{d}/>')

    def text(self, x, y, s, size=2.2, fill=INK, anchor="middle", weight="normal"):
        self.parts.append(
            f'<text x="{x:.2f}" y="{y:.2f}" font-family="Helvetica,Arial,sans-serif" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{esc(s)}</text>')

    def write(self, path: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}mm" '
                f'height="{self.h}mm" viewBox="0 0 {self.w} {self.h}">')
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(head + "".join(self.parts) + "</svg>")
        return path


class Panel:
    """Maps a world window (x0, y0, x1, y1 in plan mm) onto a sheet rect."""

    def __init__(self, sheet: Sheet, win, dst):
        wx0, wy0, wx1, wy1 = win
        dx0, dy0, dw, dh = dst
        self.s = min(dw / (wx1 - wx0), dh / (wy1 - wy0))
        self.cx = dx0 + (dw - (wx1 - wx0) * self.s) / 2.0
        self.cy = dy0 + (dh - (wy1 - wy0) * self.s) / 2.0
        self.x0, self.y1 = wx0, wy1
        self.sh = sheet

    def px(self, wx):                 # world x -> sheet x
        return self.cx + (wx - self.x0) * self.s

    def py(self, wy):                 # world y -> sheet y (flip: plan rear is up)
        return self.cy + (self.y1 - wy) * self.s

    @property
    def scale_label(self):
        return f"1:{round(1 / self.s)}"

    def rect_mm(self, x, y, w, h, **kw):
        self.sh.rect(self.px(x), self.py(y + h), w * self.s, h * self.s, **kw)

    def line_mm(self, x1, y1, x2, y2, **kw):
        self.sh.line(self.px(x1), self.py(y1), self.px(x2), self.py(y2), **kw)

    def poly_mm(self, pts, **kw):
        self.sh.poly([(self.px(x), self.py(y)) for x, y in pts], **kw)

    def wall(self, x, y, w, h, fill=WALL):
        self.rect_mm(x, y, w, h, fill=fill)

    def label(self, wx, wy, s, size=2.0, **kw):
        self.sh.text(self.px(wx), self.py(wy), s, size=size, **kw)

    def _dim_label(self, sx, sy, text, size, rot=False):
        half = len(text) * size * 0.31
        self.sh.rect(sx - half, sy - size * 0.85, half * 2, size * 1.15, fill="#ffffff")
        self.sh.text(sx, sy + size * 0.35, text, size=size)

    def dim_h(self, x0, x1, wy, text, off=500, size=1.9):
        """Horizontal dimension drawn OUTSIDE the plan (wy is a clear y line)."""
        y = wy - off
        self.line_mm(x0, y, x1, y, sw=0.18)
        for x in (x0, x1):
            self.line_mm(x, y - 120, x, y + 120, sw=0.18)
        self._dim_label(self.px((x0 + x1) / 2.0), self.py(y), text, size)

    def dim_v(self, y0, y1, wx, text, off=500, size=1.9):
        """Vertical dimension drawn OUTSIDE the plan (wx is a clear x line)."""
        x = wx - off
        self.line_mm(x, y0, x, y1, sw=0.18)
        for y in (y0, y1):
            self.line_mm(x - 120, y, x + 120, y, sw=0.18)
        self._dim_label(self.px(x), self.py((y0 + y1) / 2.0), text, size)


# ----------------------------------------------------------------- primitives
def opening(p, x, y, w, h):
    """Cut a hole out of a drawn wall band; add the leaf or the glazing after."""
    p.rect_mm(x, y, w, h, fill="#ffffff")


def leaf(p, hx, hy, w, a=90.0, swing=None, r=None):
    """Door leaf from hinge (hx, hy); a=0 points +x, a=90 points +y (toward rear).

    Leave `swing` as None inside crowded option panels — the arc quadrant
    collides with furniture and reads as a real clash.
    """
    a_r = math.radians(a)
    p.line_mm(hx, hy, hx + w * math.cos(a_r), hy + w * math.sin(a_r), stroke=INK, sw=0.6)
    if swing:
        r = r or w
        pts = [(hx + r * math.cos(math.radians(swing[0] + (swing[1] - swing[0]) * i / 12)),
                hy + r * math.sin(math.radians(swing[0] + (swing[1] - swing[0]) * i / 12)))
               for i in range(13)]
        p.poly_mm(pts, sw=0.15)


def glazing(p, x, y, w, h=110):
    p.rect_mm(x, y, w, h, fill="#dce9f8", stroke=GLASS, sw=0.35)
    p.line_mm(x, y + h / 2, x + w, y + h / 2, stroke=GLASS, sw=0.2)


def bed(p, x, y, w=1600, d=2000, note="GIƯỜNG 1.6×2.0"):
    """Bed with its headboard on the low-y edge; swap x/y to place it otherwise."""
    p.rect_mm(x, y, w, d, fill="#ffffff", stroke=INK, sw=0.35)
    p.rect_mm(x, y, w, 250, fill="#e9eef2", stroke=INK, sw=0.25)
    p.rect_mm(x + 120, y + d - 520, w - 240, 400, fill="#f3f4f6", stroke=SOFT, sw=0.2)
    p.label(x + w / 2, y + d / 2, note, size=1.5)


def desk(p, x, y, w=1400, d=650, chair="north"):
    """Desk plus its chair 330 mm off the working edge (chair='north'|'south')."""
    p.rect_mm(x, y, w, d, fill="#f5f2ea", stroke=INK, sw=0.3)
    cy = y + d + 330 if chair == "north" else y - 330
    p.sh.circle(p.px(x + w / 2), p.py(cy), 240 * p.s, fill="#ffffff", stroke=INK, sw=0.3)


def wardrobe(p, x, y, w, d=600):
    p.rect_mm(x, y, w, d, fill="#eef1f3", stroke=INK, sw=0.3)
    p.line_mm(x + w / 2, y, x + w / 2, y + d, stroke=INK, sw=0.15)


# ------------------------------------------------------------------- the sheet
def build_sheet(path, panels, win, title, legend=(), cols=2, footer=None):
    """panels: [(panel_title, caption, draw_fn)] — draw_fn receives a Panel.

    caption: "what it wins | Costs: what it costs" — one clause per ' | '.
    """
    sh = Sheet()
    sh.text(14, 16, title, size=7.5, anchor="start", weight="bold")
    pw, ph = 190.0, 108.0
    for i, (ptitle, cap, fn) in enumerate(panels):
        col, row = i % cols, i // cols
        x0 = 12.0 + col * (pw + 14.0)
        y0 = 26.0 + row * (ph + 20.0)
        p = Panel(sh, win, (x0, y0, pw - 20, ph - 24))
        fn(p)
        sh.text(x0, y0 - 2, ptitle, size=4.2, anchor="start", weight="bold")
        for k, line in enumerate(cap.split(" | ")):
            sh.text(x0, y0 + ph - 12 + k * 4.2, line, size=2.1, anchor="start")
        sh.text(x0 + pw - 20, y0 - 2, p.scale_label, size=3.0, anchor="end")
        sh.rect(x0 - 6, y0 - 8, pw - 8, ph + 6, stroke=SOFT, sw=0.3)
    ly = A3H - 12.0
    for k, line in enumerate(legend):
        sh.text(14 + k * 100, ly, line, size=2.2, anchor="start")
    if footer:
        sh.text(A3W - 14, ly, footer, size=2.0, anchor="end")
    return sh.write(path)


def rasterise(svg="sheet.svg", px=4):
    """SVG -> PNG with PyMuPDF (no browser/cairo), plus a web-sized copy."""
    import fitz
    from PIL import Image
    fitz.open(svg)[0].get_pixmap(matrix=fitz.Matrix(px, px)).save("sheet_print.png")
    im = Image.open("sheet_print.png").convert("RGB")
    im.resize((1900, int(im.size[1] * 1900 / im.size[0]))).save("sheet_web.png")
    return im.size


if __name__ == "__main__":
    # Example: one room in its own mm coordinates, one option, one new partition.
    X0, X1, Y0, Y1 = 200.0, 3760.0, 4950.0, 8850.0   # clear room extents
    PART_Y = 6600.0                                    # the new partition

    def draw(p):
        p.rect_mm(X0, Y0, X1 - X0, Y1 - Y0, fill="#fbfaf7")          # room tint
        p.dim_v(Y0, PART_Y, X0, "1650", off=700)
        p.dim_h(X0, X1, Y0, "3560", off=700)
        bed(p, 1250, 6800, 1600, 2000)
        desk(p, 2300, 5010, 1400, 650, chair="north")
        p.wall(X0 - 200, Y0 - 200, 200, (Y1 - Y0) + 400)             # existing walls
        p.wall(X1, Y0 - 200, 200, (Y1 - Y0) + 400)
        p.wall(X0, PART_Y, X1 - X0, 100, fill=NEW)                   # new work, last
        opening(p, 300, PART_Y, 1200, 100)
        leaf(p, 1500, PART_Y + 50, 900, a=180)                       # leaf only
        p.label((X0 + X1) / 2, 6100, "KHÔNG GIAN LÀM VIỆC", size=2.4)

    build_sheet(
        "sheet.svg",
        [("Study at the window", "5.9 m² work | Costs: bedroom 2150 deep", draw)],
        win=(X0 - 1200, Y0 - 1500, X1 + 1200, Y1 + 900),
        title="P.NGỦ → WORKSPACE + BEDROOM",
        legend=("NEW: partition (orange)", "EXISTING: walls, doors, fixtures"),
        cols=1,
        footer="dimensions in mm",
    )
    print("wrote sheet.svg", rasterise(), os.path.abspath("sheet.svg"))
