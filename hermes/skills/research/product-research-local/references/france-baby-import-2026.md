# France Baby Import 2026 — basket state & verified facts

Project source of truth (repo files):
- Brainstorm: `baby-context/research/2026-08-03_france-baby-import-brainstorm.md`
- HTML report: `baby-context/reports/2026-08-03-france-baby-import.html`
- Brand sweep verdicts: `references/french-baby-brands-vietnam-availability.md`

Context: baby born 2026-05-08 (HCMC), ~3M at research, 4-5M at traveler arrival.
Suitcase-import channel only (compact/light/non-fragile; ~5 kg budget). 17/18 French
mid-premium baby brands absent in VN. Purchase channel: Amazon.fr (Moulin Roty /
Jacadi / Cyrillus / Vertbaudet via brand sites).

## Verified prices (Aug 2026 — drift; re-verify at checkout)

Clothing (Petit Bateau unless noted):
- Gigoteuse sleeveless sleep sack 0-6M: EUR 48.99 (4.6*, 44) — top-value single item
- Trio long-sleeve bodies 3pk 6M/12M: EUR 26.95 (4.8*, 604)
- Organic crossover bodies 3pk 12M: EUR 17.59 (4.7*, 822)
- Classic ribbed bodies 2pk 6M/12M: EUR 14.12 (4.5*, 365) — the crossed-collar icon
- Footless cotton pyjama 12M: EUR 15.20 (5.0*) — long-sleeve; demoted in rerank
- Bonnet "Marshmallow" nb/6M: EUR 12.00 (4.4*, 70) — pairs with moufles below
- Striped socks 3pk: EUR 22.00 (5.0*) — weak value; dropped in rerank
- Catimini bath cape + glove set 6M/12M: EUR 29.90 (4.8*, 13) — only Catimini on Amazon.fr worth carrying
- IKKS camisole 6M: EUR 26.75 — rare old-season stock; promoted in rerank (sleeveless)

Toys/books: Kaloo Lapinoo puppet 20.95 (4.9*, 2.1K); D&C mouchoir rabbit 12.90 (4.7*, 6.3K);
D&C flat rabbit 17cm 17.99; Djeco baby line ~20; Vilac Jura rattle ~12; Lilliputiens Stella
teether 8.32 (4.8*, 266); Moulin Roty doudou à langer ~15 (brand site only); Petit Ours Brun
6-book box 12.50; Bébé T'choupi ~6 each (5.0*); Nathan "Promenade sous l'océan" 10.99.

## Short-sleeve rerank (user preference, 2026-08-06)

User prefers short-sleeve (HCMC heat). Applied changes:
- Long-sleeve Trio → PB "Lot de 3 bodies manches courtes en coton" (exists on PB site,
  incl. printed variant; price same band as long-sleeve — verify at checkout)
- Crossover bodies → manches courtes variant
- Footless pyjama demoted (gigoteuse covers AC-night warmth; or swap to short-sleeve sleepsuit)
- Socks dropped entirely (trivial in VN, barely needed in heat)
- IKKS camisole promoted (sleeveless by definition)
- Resulting clothing basket: ~EUR 140-150, ~1.5 kg (was ~160 / 2.0 kg)
- Optional hot-climate add: PB "brassière" (sleeveless cotton vest) — the French AC layering piece

## Breathable anti-scratch mittens (user requirement: cool + breathable for HCMC)

- TOP PICK: PB "Moufles anti-griffures en côte" (Ref 5573501440) EUR 6.90 — 100% cotton
  ribbed jersey, OEKO-TEX, elastic wrist; same Marshmallow collection as the bonnet.
  Caveat: colorway availability varies (Marshmallow/Multico showed OOS on PB site 08-06).
- Made-in-France alts: SEVIRA KIDS (Amazon.fr), Trois Kilos Sept (troiskilossept.com, organic).
- Local fallback (verified on Tiki 08-06): KUKU bao tay 51k VND, BABIBOO cotton 27k,
  generic cotton sets 22-33k VND. Generic cotton mittens ARE findable locally — import
  only for the brand match.
- Material rules for HCMC: thin 100% cotton jersey OK; muslin/gaze de coton more
  breathable; bamboo cooling. AVOID fleece/molleton/velour (Sterntaler), polyester mesh,
  winter-lined. At 4-5M many parents drop mittens anyway (trim+file nails) — pack 1-2 pairs max.

## Books — language nuance (user asked "are these English?")

All book picks are FRENCH-language (bilingual-library intent is the point of importing).
POB / T'choupi have no real English editions. Nathan Emiri Hayashi series EXISTS in
English via Twirl Books (US) — so the French import only makes sense for the French.
If user wants English books → drop the book section (~EUR 41, ~1.2 kg freed).

## Research techniques that worked (2026-08-06)

- Amazon.fr via curl → 0 bytes (bot-wall). petit-bateau.fr product pages curl fine with
  desktop UA: price in `<meta name="description">` ("dès 6.90 EUR") + JSON-LD `"price": 6.9`.
- PB category/search pages client-rendered; SFCC `Search-ShowAjax` API → 0 bytes.
- DDG HTML endpoint works for French product discovery (`site:petit-bateau.fr <product>`
  → exact SEO-slug URLs). Bing RSS served unrelated junk for these queries.
- lemeilleuravis.fr / meilleurs-5.fr "top 10" pages = affiliate mirrors of generic Amazon
  multi-packs — useful only to confirm commodity class.
- Tiki JSON API quick-check for VN-side availability (bao tay chống cào) worked first try.
