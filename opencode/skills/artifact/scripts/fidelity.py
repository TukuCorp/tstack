"""Check a built page against its source: Vietnamese diacritics, linked sources, light+dark theme, numbers.
usage: python -X utf8 fidelity.py <source: brief .md/.txt or original .html> <page.html>
Exit 1 on FAIL (diacritics, links, theme). WARN lines need judgment: a number may be shown in a chart."""
import html, re, sys

VN = r'[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]'
DARK = r'luxury|dark|night|black|dracula|dim|abyss|business|coffee|forest|halloween|sunset|synthwave'

def text(t):
    t = re.sub(r'(?is)<(script|style)[^>]*>.*?</\1>', ' ', t)
    return html.unescape(re.sub(r'<[^>]+>', ' ', t))

src_raw = open(sys.argv[1], encoding='utf-8').read()
page_raw = open(sys.argv[2], encoding='utf-8').read()
src, page = text(src_raw), text(page_raw)
fails, warns = [], []

# 1. Vietnamese diacritics kept (no transliteration such as Bảng -> Bang).
s_vn, p_vn = len(re.findall(VN, src, re.I)), len(re.findall(VN, page, re.I))
if s_vn >= 10 and p_vn < 0.6 * s_vn:
    fails.append(f'Vietnamese diacritics dropped (source {s_vn}, page {p_vn}): write the file as UTF-8 and keep source terms verbatim')

# 2. Source URLs are clickable links, not plain text.
urls = {u.rstrip('.,;') for u in re.findall(r'https?://[^\s)"<>]+', src_raw)}
hrefs = set(re.findall(r'href="(https?://[^"]+)"', page_raw))
unlinked = [u for u in urls if not any(u in h or h in u for h in hrefs)]
if unlinked:
    fails.append(f'{len(unlinked)} source URLs not linked as <a href>: {", ".join(sorted(unlinked)[:4])}')

# 3. Light and dark both work: no fixed dark theme on <html>, and some light/dark mechanism present.
if re.search(rf'<html[^>]*data-theme="({DARK})"', page_raw) or not re.search(r'prefers-color-scheme|prefersdark|daisyui', page_raw):
    fails.append('no light/dark pair: do not pin a dark data-theme on <html>; follow prefers-color-scheme')

# 4. Numbers from the source appear somewhere (text or attributes). URLs excluded.
num = r'\d[\d.,]*\d|\d{3,}'
norm = lambda s: re.sub(r'[.,\s]', '', s)
page_all = page + ' ' + ' '.join(re.findall(r'="([^"]*)"', page_raw))
have = {norm(n) for n in re.findall(num, page_all)}
src_nourl = re.sub(r'https?://\S+', ' ', src)
missing = sorted({n for n in re.findall(num, src_nourl) if len(norm(n)) >= 3 and norm(n) not in have})
if missing:
    warns.append(f'{len(missing)} source numbers not found, confirm none were dropped: {", ".join(missing[:12])}')

# 5. Fewer words, not more: the page should not out-talk its source.
sw, pw = len(src_nourl.split()), len(page.split())
if sw >= 200 and pw > 1.15 * sw:
    warns.append(f'page has {pw} words vs {sw} in the source: cut prose, show it as visuals')

for w in warns:
    print('WARN', w)
for f in fails:
    print('FAIL', f)
print('fidelity:', 'OK' if not fails else f'{len(fails)} issue(s)')
sys.exit(1 if fails else 0)
