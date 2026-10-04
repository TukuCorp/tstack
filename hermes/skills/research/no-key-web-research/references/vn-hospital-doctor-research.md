# VN Hospital / Doctor Research Playbook

Verified 2026-08-06 while ranking HCMC dermatologists/podiatrists (onychocryptosis brief).
Use when the user asks to find/rank Vietnamese doctors, hospitals, or clinics (HCMC focus),
especially when `web_search` is down (Firecrawl credits) and DDGS is blocked.

## Source inventory (HCMC — reachable via curl, browser UA)

| Site | What it has | Notes |
|------|-------------|-------|
| tamanhhospital.vn | BVĐK Tâm Anh. Doctor dir `/chuyen-gia/` + profiles `/chuyen-gia/<slug>/`; patient-ed `/benh/<slug>/`; case stories `/tin-tuc/` | `tamanh.com.vn` is a TOY SHOP — wrong domain. Filter map parseable from `<option>` values: `filter_chuyenkhoa` (Khoa Da liễu=432), `filter_diadiem` (TP.HCM=36, Q8=1114, PK Q7=509), `filter_chucvu`, `filter_hocvi`, `filter_hoc ham`. Profile "GIỚI THIỆU" states "X năm kinh nghiệm". Pagination `/chuyen-gia/page/2/` does NOT carry filter params — refilter from page 1 or search `?s=` |
| fvhospital.com | FV Hospital. Doctor profiles at `/doctors/<slug>/` (NOT `/bac-si/<slug>/` — that path serves a JPEG/404); dept team pages `/specialties/<dept>/doi-ngu-bac-si-.../`; JCI 2016–2025 | "Kinh nghiệm" + "Bằng cấp" sections give career dates; "Lịch khám" gives consult slots |
| cih.com.vn | Bệnh viện Quốc tế City (CIH). Doctor list `/bac-si/`; dept pages `/chuyen-khoa/<slug>/` name the dept's doctors with stated years | Khoa Da Liễu has only 2 doctors; top-level `/bac-si/` misses dept-only doctors |
| dalieudhyd.vn | Khoa Da liễu – Thẩm mỹ da, BV ĐHYD TP.HCM (UMC). 19 doctor profiles at `/bs/<slug>/` with "Bằng cấp chuyên môn" + "Kinh nghiệm" + schedule | Dept site is SEPARATE from umc.edu.vn (which rejects curl: 400 Invalid Hostname). Some docs dual-affiliated with BV Da liễu TP.HCM |
| BV Da liễu TP.HCM | No working website (all guessed domains dead) | Verify via news RSS + dalieudhyd cross-refs; AloBacsi Q&A confirms tiểu phẫu móng quặp; 836K visits/yr (Dân trí) |
| BV TP Thủ Đức | Domain dead | RENAMED → Bệnh viện Đa khoa Thủ Đức (Tuổi Trẻ 08/2025); no public derm roster found |

## Endpoints that work when web_search is down

- tuoitre.vn/tim-kiem.htm?keywords=<q> — SSR; article hrefs `/slug-<ts>.htm` parseable. (vnexpress/dantri/thanhnien search pages: JS shell or blocked.)
- Bing News RSS (`format=rss&setlang=vi`) + urldecode the `url=` param of `bing.com/news/apiclick.aspx` links → real article URLs (vnexpress, dantri, kenh14 all curl-OK).
- Google News RSS — headlines + dates only (its /rss/articles/ redirects 400 to curl).
- PubMed eutils — esearch/esummary for PMIDs, titles, DOIs (Rung 2c).
- Wayback CDX — use `matchType=domain` (wildcard prefix 403s); retry on 503.

## When the shared Firecrawl backend rate-limits (NOT credit-loss) — 2026-08-18
`web_search` AND `web_extract` draw from ONE per-minute budget (`Rate Limit Exceeded ...
Consumed (req/min): 15, Remaining: 0 ... resets in Ns`). When BOTH hit it mid-task the
backend is alive — don't abandon it:
- Queue extractions **serially in `execute_code`** with `time.sleep(8–11)` between calls
  (≈15/min). 4–6 pages fit the 5-min script window. Filter inside the script (`re.search`
  on filtered lines) so only the doctor/content head returns — never dump full nav/layout.
- **FV `/doctors/<slug>/` profiles put the real bio AFTER a long nav menu**; filter from
  the last `^Dr\.|^Dr |^ThS|^BSCK|^BS\b` heading, else everything is menu noise. Same for
  other `/en/doctors/` pages.
- If a single page still 503s on the shared budget, wait ~30s (reset) and retry once before
  falling back to DDGS/wayback.

## Aggregators (cross-check only)

- bookingcare.vn — SSR; profiles state "Hơn X năm kinh nghiệm"; listicles (e.g. "12 bác sĩ Da liễu giỏi TP.HCM") carry reviewer/editor names + update dates. Tier 4 — never rank on these alone.
- youmed.vn — JS SPA, nothing in HTML. Skip.

## Ranking methodology that worked

- Title ladder as seniority proxy: BS → ThS/CKI → CKII → TS → PGS/GS (CKI/BSNT usually ~8–12 yrs, CKII ~15–25, TS/PGS ~20+).
- Prefer stated "X năm kinh nghiệm" on hospital profiles; else estimate from graduation/residency years in the bio and LABEL as ước tính.
- Flag management-heavy roles (Trưởng khoa, Giám đốc, người sáng lập khoa) when the user wants a pure clinician; note they may still practice.
- Condition-specific evidence beats generic profiles: a hospital case story naming the doctor + technique (e.g. Tam Anh móng quặp case: BS.CKI Võ Huy Tâm, laser CO₂ matrix destruction) is the strongest signal.
- Cover the specialist center even if not named (BV Da liễu TP.HCM for skin) and note hospital renames found via news RSS.
- State gaps explicitly: unpublished years, unreachable sites, headline-only RSS citations (redirect blocked).

## Hygiene

- Save every fetched page to a per-session fetch dir (e.g. `research/_fetch_YYYY-MM-DD/`) — it doubles as the verification ledger for the brief.
- Verify claimed experience years on the PRIMARY (hospital) page before trusting an aggregator figure.
