# Identifying a product by its packaging (image-first kit)

Companion to the "Identifying a product from its packaging" section of `product-research`.
Use when the discriminating feature is visual (mascot, illustration, colour) and text search
only returns generic roundups or unrelated stock imagery.

## 1. Bing image search, two ways

**curl (fastest, works when only the headless path is needed)**

```bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
curl -s -A "$UA" "https://www.bing.com/images/async?q=pukka+night+time+tea+box&first=1&count=35&adlt=off" -o out.html
```

Parse in Python (NOT with a compound quoted grep — those trip the command parser on this host):

```python
import re, html, json
h = open("out.html", encoding="utf-8", errors="ignore").read()
for m in re.findall(r'm="(\{[^"]*?\})"', h):
    d = json.loads(html.unescape(m))
    print(d.get("t", "")[:110], "|", d.get("murl", "")[:130], "|", d.get("purl", "")[:80])
```

- `t` = result title, `murl` = image URL, `purl` = page the image came from.
- **Query shape is the whole game.** Product/brand-shaped queries return real pack shots;
  descriptive queries ("sleep tea purple cat box uk") make Bing serve an unrelated fallback set
  (sleep-cycle infographics, photos of real cats) while still echoing your query in `<title>`.
  Junk results ⇒ rewrite the query around candidate brands; they do not prove absence.

**browser-control (for JS-rendered search pages, Google Images, or when curl is walled)**

```js
// save as C:/Users/tukum/AppData/Local/Temp/bc_collect.js ; run:
// browser-control execute --file ./bc_collect.js --json
const all = {};
for (const q of ["pukka night time tea box", "clipper sleep easy tea box"]) {
  await page.goto("https://www.bing.com/images/search?q=" + encodeURIComponent(q) + "&form=HDRSC2&count=35",
                  { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.waitForTimeout(2500);
  const raw = await page.$$eval("a.iusc", els => els.map(e => e.getAttribute("m")).filter(Boolean));
  for (const m of raw) { try { const d = JSON.parse(m); if (d.murl) all[d.murl] = { t: d.t, p: d.purl }; } catch (e) {} }
}
fs.writeFileSync("C:/Users/tukum/AppData/Local/Temp/tea_imgs.json", JSON.stringify(all, null, 1));
return { total: Object.keys(all).length };
```

Gotchas that cost time:
- `require("fs")` throws `ReferenceError: require is not defined` inside execute — the sandbox
  injects `fs` and `path` aliases directly; use them bare.
- CLI `--json` stdout starts with `Session: <id>. Continue with --session <id>.` before the JSON
  body — locate the first `{` and parse from there, or the `json.load` dies at char 0.
- `curl` on Google Images returns a ~273-byte stub; DDG's `i.js` needs a `vqd` token that the HTML
  endpoint no longer exposes. Use `browser-control` for those, curl+Bing for everything else.

## 2. Download + contact sheet (one vision call per 25 images)

```python
import json, os, subprocess, math
from PIL import Image, ImageDraw

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
OUT = "C:/Users/tukum/AppData/Local/Temp/teaimg"; os.makedirs(OUT, exist_ok=True)
data = json.load(open("C:/Users/tukum/AppData/Local/Temp/tea_imgs.json", encoding="utf-8"))

index = []
for i, (u, v) in enumerate(data.items()):
    path = os.path.join(OUT, f"{i:03d}.jpg")
    subprocess.run(["curl", "-sL", "-m", "25", "-A", UA, "-H", "Referer: " + (v.get("p") or "https://www.bing.com/"), u, "-o", path])
    try:
        im = Image.open(path); im.load()
        if os.path.getsize(path) < 3000: raise ValueError
        index.append({"i": i, "file": path, "t": v["t"], "u": u, "p": v.get("p", "")})
    except Exception:
        pass

CELL, COLS, ROWS = 320, 5, 5
for s in range(math.ceil(len(index) / (COLS * ROWS))):
    batch = index[s * COLS * ROWS:(s + 1) * COLS * ROWS]
    sheet = Image.new("RGB", (COLS * CELL, ROWS * CELL), (255, 255, 255)); d = ImageDraw.Draw(sheet)
    for k, item in enumerate(batch):
        cx, cy = (k % COLS) * CELL, (k // COLS) * CELL
        im = Image.open(item["file"]).convert("RGB"); im.thumbnail((CELL - 30, CELL - 30))
        sheet.paste(im, (cx + 15, cy + 30))
        d.rectangle([cx, cy, cx + CELL - 1, cy + CELL - 1], outline=(0, 0, 0))
        d.text((cx + 6, cy + 6), f"#{item['i']}", fill=(200, 0, 0))
    sheet.save(f"C:/Users/tukum/AppData/Local/Temp/sheet_{s}.png")
json.dump(index, open("C:/Users/tukum/AppData/Local/Temp/mosaic_index.json", "w", encoding="utf-8"), indent=1)
```

Keep `mosaic_index.json`: it maps tile `#N` → title/url, which is how a hit becomes a citation.
~50-90% of URLs download (hotlink protection, dead listings); the survivors are enough.

## 3. Vision grounding checklist

Montage answers are a TRIAGE signal, never a finding.

1. Ask for a description **and a transcription of the brand/product wording printed on the pack**.
2. Discard the answer if that transcription does not match the pack you actually put in the tile.
3. Re-check any hit at full resolution: quadrant crops, or a tight crop of the pack region upscaled
   to ~1200px.
4. Re-fetch the same pack from a second retailer/brand site and repeat — two agreeing checks before
   the attribute goes into the answer.
5. Report near-misses as what they are: "closest so far is X, whose box shows Y" — and never upgrade
   a hallucinated claim into a deliverable.

## 4. Verified UK sleep-tea packaging (cats)

| Product | What the pack actually shows |
|---|---|
| teapigs "Snooze" (sleepy tea) | Curled sleeping cat in white line art on a blue box — the only clear feline; cat is blue/white, not purple |
| Celestial Seasonings Sleepytime | Cat curled by the fire next to the bear mascot (US brand, imported into the UK) |
| Pukka Night Time | Botanical artwork + dark human yoga silhouettes; no animal |
| Twinings Superblends Sleep (spiced apple & vanilla) | Apple, vanilla, camomile, passionflower; no animal |
| Clipper Organic Sleep Easy | Black teacup silhouette + crescent moon and stars; no animal |
| Yogi Tea Bedtime | Indigo mandala + chamomile/fennel/valerian botanicals; no animal |
| Heath & Heather Organic Night Time | Deep teal, moon/stars, chamomile + hops + butterfly; no animal |
| English Tea Shop "Sleepy Me" | Aqua botanical border, two small human figures, bee and butterfly; no cat |
| H&B Relaxation Support | Dark green, botanical illustration, purple badge; no animal |
| Shelgo Tea "CatNap" (UK) | Black engraving-style cat head in a top hat on a kraft pouch with a purple label — cat is black, label is purple |
