"""Procedural dark PCB background for noctty (Matrix palette)."""
import random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2560, 1440
SS = 2                      # supersample factor for anti-aliasing
P = 22                      # routing grid pitch (px at 1x)
GW, GH = W // P + 1, H // P + 1
random.seed(int(sys.argv[2]) if len(sys.argv) > 2 else 7)

BG = (9, 12, 9)
TRACE = (16, 46, 24)
TRACE_HI = (30, 105, 52)
PAD = (22, 64, 33)
IC_FILL = (12, 17, 13)
IC_EDGE = (20, 44, 26)

img = Image.new("RGB", (W * SS, H * SS), BG)
glow = Image.new("RGB", (W * SS, H * SS), (0, 0, 0))
d, g = ImageDraw.Draw(img), ImageDraw.Draw(glow)
occ = np.zeros((GW, GH), bool)

def px(c):  # grid cell -> supersampled pixel
    return (c[0] * P * SS + P * SS // 2, c[1] * P * SS + P * SS // 2)

def density(x, y):
    # sparser top-left where most text sits, denser toward right/bottom edges
    return 0.15 + 0.85 * max(x / GW, y / GH) ** 1.6

def pad(c, r, col, hole=True, draw=d):
    x, y = px(c); r *= SS
    draw.ellipse((x - r, y - r, x + r, y + r), fill=col)
    if hole:
        h = r * 0.45
        draw.ellipse((x - h, y - h, x + h, y + h), fill=BG)

DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]

def route(start, di, hi=False, width=3):
    path, c = [start], start
    occ[c] = True
    for step in range(random.randint(8, 60)):
        if random.random() < 0.12:
            di = (di + random.choice([-1, 1])) % 8
        dx, dy = DIRS[di]
        n = (c[0] + dx, c[1] + dy)
        if not (0 <= n[0] < GW and 0 <= n[1] < GH) or occ[n]:
            break
        # block diagonal crossings
        if dx and dy and occ[c[0] + dx, c[1]] and occ[c[0], c[1] + dy]:
            break
        occ[n] = True
        path.append(n); c = n
    if len(path) < 4:
        return
    pts = [px(p) for p in path]
    col = TRACE_HI if hi else TRACE
    d.line(pts, fill=col, width=width * SS, joint="curve")
    if hi:
        g.line(pts, fill=TRACE_HI, width=width * SS * 3, joint="curve")
    end_r = random.choice([5, 6, 7])
    pad(path[0], 4, PAD, hole=False)
    pad(path[-1], end_r, TRACE_HI if hi else PAD)
    if hi:
        pad(path[-1], end_r * 2.5, (20, 80, 38), hole=False, draw=g)

# --- IC footprints, with traces fanning out of their pins ---
pins = []
for _ in range(9):
    for _try in range(50):
        w, h = random.randint(4, 9), random.randint(3, 7)
        x, y = random.randint(2, GW - w - 3), random.randint(2, GH - h - 3)
        if random.random() > density(x + w / 2, y + h / 2):
            continue
        if occ[x - 2:x + w + 3, y - 2:y + h + 3].any():
            continue
        occ[x:x + w + 1, y:y + h + 1] = True
        (x0, y0), (x1, y1) = px((x, y)), px((x + w, y + h))
        d.rounded_rectangle((x0, y0, x1, y1), radius=6 * SS, fill=IC_FILL,
                            outline=IC_EDGE, width=2 * SS)
        d.ellipse((x0 + 10 * SS, y0 + 10 * SS, x0 + 18 * SS, y0 + 18 * SS), fill=IC_EDGE)
        for i in range(x + 1, x + w):
            pins.append(((i, y - 1), 6)); pins.append(((i, y + h + 1), 2))
        for j in range(y + 1, y + h):
            pins.append(((x - 1, j), 4)); pins.append(((x + w + 1, j), 0))
        break

random.shuffle(pins)
for c, di in pins:
    if random.random() < 0.75 and not occ[c]:
        route(c, di, hi=random.random() < 0.08)

# --- free-running buses and single traces ---
for _ in range(1400):
    c = (random.randrange(GW), random.randrange(GH))
    if occ[c] or random.random() > density(*c):
        continue
    route(c, random.choice([0, 2, 4, 6, 1, 3]), hi=random.random() < 0.04,
          width=random.choice([2, 3, 3, 5]))

# --- scattered vias ---
for _ in range(500):
    c = (random.randrange(GW), random.randrange(GH))
    if not occ[c] and random.random() < density(*c) * 0.5:
        occ[c] = True
        pad(c, 4, PAD)

glow = glow.filter(ImageFilter.GaussianBlur(14 * SS))
out = Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(glow, np.int16) * 0.6, 0, 255).astype(np.uint8))
out = out.resize((W, H), Image.LANCZOS)

# vignette: darken slightly toward the middle-left text area
yy, xx = np.mgrid[0:H, 0:W]
v = 0.75 + 0.25 * np.clip(np.hypot((xx - W * 0.35) / W, (yy - H * 0.4) / H) * 1.8, 0, 1)
arr = (np.asarray(out, np.float32) * v[..., None]).astype(np.uint8)
Image.fromarray(arr).save(sys.argv[1], optimize=True)
lum = arr @ np.array([0.2126, 0.7152, 0.0722])
print(f"saved {sys.argv[1]}  mean lum {lum.mean() / 255:.3f}  p99 {np.percentile(lum, 99) / 255:.3f}  max {lum.max() / 255:.3f}")
