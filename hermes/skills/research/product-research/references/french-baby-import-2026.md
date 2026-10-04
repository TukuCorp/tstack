# French premium baby brands: Vietnam availability + Amazon.fr import (verified 2026-08-03)

Context: suitcase-import France → HCMC for a 3-month-old (DOB 2026-05-08). Two parallel
subagents: (A) Amazon.fr product verification via live browser DOM extraction, (B) VN
availability sweep (Tiki/Lazada browser + Brave/DDG `site:` queries for Shopee + brand-site
store locators). Firecrawl credits were out + amazon.fr curl bot-walled (HTTP 202) →
browser DOM extraction was the working path (see SKILL.md "Amazon scraping" section).

## VN availability verdicts (18 brands)
- **RARE/ABSENT in VN (import)**: Petit Bateau, IKKS Baby, Catimini, Tartine et
  Chocolat, Cyrillus, Vertbaudet, Absorba (clothing); Moulin Roty, Kaloo, Vilac, Nathan,
  Doudou et Compagnie (toys); Petit Ours Brun, T'choupi (books — only niche FR
  bookstores in Hanoi carry French kids' books).
- **PARALLEL-only (tiny resale, no official channel)**: Jacadi (1-off Shopee resells),
  Djeco (1 LazGlobal item), Janod (2 magnet-map items). Still worth importing for
  selection/price.
- **AVAILABLE in VN (buy locally, skip)**: Sophie la Girafe — widely parallel-imported
  (Lazada 3,903 listings, HCMC resellers, teethers ~900k₫).

## Amazon.fr quirks (verified)
- **Moulin Roty**: signature doudous NOT on Amazon.fr (notebooks/coloring books only) →
  moulinroty.com / Oxybul / Smallable (~€13-19 doudou à langer).
- **Jacadi**: no clothing on Amazon.fr (cosmetics only) → jacadi.fr.
- **Tartine et Chocolat**: only €78-198 items on Amazon.fr — skip for mid-premium budget.
- **Janod**: Amazon.fr carries 12M+ tables/trolleys (bulky) — no compact baby items.

## Petit Bateau anchor ASINs (prices drift; ASINs stable)
- 54220 bodies 2pk B083WLRLLS (~€14) · Trio long-sleeve 3pk B084HCW1ND (€26.95) ·
  Bio 3pk B08FBBJ1PR (€17.59) · pyjama B0FKHQ2V5K (€15.20) · gigoteuse sleeveless
  0-6M B0CS2ZP1QN (€48.99 — the French AC-room sleep sack, highest-value item) ·
  hat B0BT86GSKM (€12) · socks 3pk B0DV9WWZG7 (€22).
- Other verified toys: Kaloo Lapinoo puppet B08GM6YZGF (€20.95, 4.9★/2.1K) · D&C
  mouchoir rabbit B000HZ8QYK (€12.90) · D&C flat rabbit B00TS0VPCA (€17.99) · Djeco
  DJ06111 B06XBN86DX (€20.92) · Vilac rattle B086WP3JKT (~€12) · Lilliputiens Stella
  B0CKC39VF6 (€8.32).
- Books: Petit Ours Brun 6-book box B0FD2V8XY9 (€12.50, labelled 2Y+ = buy-ahead) ·
  Bébé T'choupi (6mo+, ~€6 ea: 2092497979 / 2095016343) · Nathan animated
  (2092596594, €10.99).

## Buying rules that generalized well
- Baby at 3M, arrival at 4-5M → buy French 6M/68 + 12M/74 (buy up, babies grow fast).
- HCMC climate = lightweight cotton only; skip wool/heavy knitwear.
- Suitcase import: compact, light, non-fragile — no activity gyms, no ride-ons, no big
  plush; books pack flat and are high-value-per-gram imports.
- Check the marquee "absent" claim yourself (browser_console) before trusting a
  subagent's negative finding — Moulin Roty's Amazon.fr absence was re-verified this way.
