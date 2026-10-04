# De Quervain's Tenosynovitis — Baby Holding Aids in HCMC

Worked example of `product-research-local` from June 30, 2026.

## Context
User's wife (7-8 weeks postpartum, baby born May 8, 2026) diagnosed with De Quervain's tenosynovitis. Needed products to help hold/care for newborn while recovering. Based in HCMC, Vietnam.

## Initial research (parallel delegates)

### Subagent A: Medical evidence
- AAOS (OrthoInfo): De Quervain's is "associated with pregnancy and the postpartum period... symptoms within 4-6 weeks" — confirmed fit.
- Pain specifically aggravated by "lifting a child" (thumb-up position).
- Treatment hierarchy: activity modification → thumb spica splinting → icing → NSAIDs → steroid injection → surgery at 6+ weeks.
- Key product class: thumb spica brace (immobilizes BOTH wrist and thumb).
- Top-rated on Amazon: MUELLER Adjust-to-Fit Thumb Brace (⭐4.5, 31K reviews), FREETOO Thumb Brace (⭐4.5, 6.6K).

### Subagent B: Vietnam availability
Lazada, Tiki, Shopee searched with Vietnamese terms.
- **Best brace available**: Dr. MED DR-W132-1 (Korean, specifically for De Quervain's) — 250–319k₫, next-day HCMC.
- **Medical supply store**: Y Tế Vạn Thành on Lazada (HCMC-based, carries GoodFit GF305W at 109k₫, United Medicare UM G02 at 395k₫).
- **In-person**: Medical supply shops on Trần Hưng Đạo D1, Long Châu/Pharmacity for basic ice packs.

## Phase 2: Baby carriers (user already-owned → refined → sling/wrap focus)

User had Ergobaby Omni structured carrier already. Asked for sling/wrap with **sideways/cradle position** for newborn.

### Available options ranked:

| Rank | Product | Price | Platform | Why |
|------|---------|-------|----------|-----|
| 1 | EmBé Sling Flex/Flex Plus | 770k₫ | Tiki | Native cradle position, one-hand adjust (De Q friendly), breathable, HCMC seller, 103 sold |
| 2 | Ergobaby Aura Wrap | 1,450k₫ | Lazada | Stretch wrap from gold-standard brand, can do cradle carry, two-shouldered distribution |
| 3 | EmBé NovaSoft (premium) | 1,190k₫ | Tiki | Same sling design, upgraded fabric, 5 colors |
| 4 | Infantino Sling Rider | ~1,000k₫ | Lazada | US brand ring sling, but single listing, import status uncertain |

### Other products also needed:
- **Nursing pillow** (gối cho con bú) — 150-350k₫ locally — reduces arm/wrist strain during feeding
- **Ice packs** — any pharmacy (Long Châu), 30-80k₫
- **TheraBand FlexBar** / TheraPutty — for rehab after acute phase, ~150-250k₫ on Shopee

## Key technique: extracting product URLs from e-commerce DOM

Lazada and Tiki often render product pages that the accessibility snapshot shows as truncated or missing hrefs. Use JS via browser_console:

```javascript
// Lazada: extract product links with titles
Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('lazada.vn/products/')).map(a => ({text: a.innerText.trim().substring(0,80), href: a.href})).filter(x => x.text)

// Tiki: use data-view-id attribute
Array.from(document.querySelectorAll('a[data-view-id*="product"]')).map(a => ({title: a.querySelector("h3")?.innerText?.trim()?.substring(0,60), href: a.href})).filter(x=>x.href && !x.href.includes('search?q='))

// Broader Tiki approach
Array.from(document.querySelectorAll('a')).filter(a => a.href && a.href.includes('tiki.vn/') && a.href.includes('spid=')).map(a => ({text: a.innerText.trim().substring(0,60), href: a.href})).filter(x => x.text)
```

## Price ranges discovered (VND, June 2026)

| Category | Budget | Mid | Premium |
|----------|--------|-----|---------|
| Thumb spica brace | 54-95k | 109-250k | 319-667k |
| Baby carrier (sling) | 145-164k | 325-770k | 801k-1.19M |
| Baby carrier (structured) | 199-300k | 770k-1.45M | 2.8M-5.9M |
| Nursing pillow | 150k | 350k | — |
| Ice pack | 30k | 80k | — |
| Rehab putty | 50k | 100k | — |
