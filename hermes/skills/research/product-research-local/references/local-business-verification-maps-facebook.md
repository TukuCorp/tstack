# Verifying local shops/businesses: Google Maps reviews + Facebook presence

Use when the user asks to find "the top N <shops/restaurants/vendors> in <city>" and
**verify** them — confirm each is a real, well-rated, locally-present business. The
two evidence sources are **Google Maps** (rating + review count + address) and the
business's **Facebook page** (follower count + VN address). This is NOT e-commerce
research — do not route it to Tiki/Lazada/Shopee.

Worked example this produced: 10 boutique HCMC florists, every one carrying a live
Maps rating/review count and a real Facebook page.

## Candidate discovery

- Roundup blogs (mytour, toplist) give a wide net; the shops' own sites give the
  accurate name.
- `web_search "site:facebook.com <shop>"` returns the FB page URL AND, in the
  snippet, the like/follower count — a fast pre-check before the live read.

## Google Maps: rating + review count

Navigate `https://www.google.com/maps/search/<url-encoded query>` inside
`browser-control`. A **specific name query** ("Tiệm hoa tươi Dear Rainy Trương
Định") lands on a **place page**; a **generic query** ("Alo Hoa Tươi") lands on a
**results feed**. Handle both, via `page.evaluate`:

- Place page:
  - name → `h1`
  - rating + review count → `div.F7nice` `.innerText` (reads like `4.9(147)`).
    **Use this, not** the `[role=img][aria-label*=star]` label, which sometimes
    drops the count.
  - address → `button[data-item-id=address]`; phone → `button[data-item-id^=phone]`;
    category → `button[jsaction*=category]`; website → `a[data-item-id=authority]` `href`
  - check the body text for `Permanently closed`
- Results feed: `document.querySelector('div[role=feed]').innerText` gives one line
  per card: `Name | rating(count) | category · address | hours · phone`. The first
  card is often Sponsored.

Batch every candidate into ONE `browser-control execute --file <script.js>` run: a
JS loop with `await page.goto(...)` → `await page.waitForTimeout(5500)` →
`page.evaluate(...)`, accumulate into an array, then
`fs.writeFileSync('<workspace>/out.json', JSON.stringify(arr))` and read the JSON
afterwards. This survives terminal output truncation (a 15-query pretty-printed
result gets cut by `head`/`tail`) and avoids one tool call per shop. Keep ~5.5s
between queries.

## Facebook: page presence + follower count

- Navigate `https://www.facebook.com/<handle>`; read `document.body.innerText`. The
  header carries `NAME | 8.8K followers • N following | <category> | <address>`.
  Follower count + an in-city address confirms real local presence. Public pages
  render logged-out; a logged-in browser session returns more detail.
- Same `--file` loop pattern: array of `[name, url]`, navigate, wait ~4.5s,
  `page.evaluate`, write JSON, read it.

## Pitfalls

- **Never "open" a listing by clicking the first `a.hfpxzc` result.** The first
  card is frequently Sponsored, so several different queries all resolve to the
  SAME sponsored place — each looked "verified" but was the wrong shop. Read the
  feed text instead, or navigate to a place page with a specific-enough query.
- If `h1` reads `Sponsored` after a click, you landed on the wrong place — discard.
- A **guessed FB handle can resolve to an unrelated page** (e.g.
  `facebook.com/LaMflorist` → an unrelated 151-follower account). Confirm the
  returned page name matches the shop; if not, treat FB presence as unverified.
- When Maps only offers a results feed for a shop with no distinct listing, report
  its rating as **unverified** rather than inferring one.
- Report review counts as "as of today" — they move.
