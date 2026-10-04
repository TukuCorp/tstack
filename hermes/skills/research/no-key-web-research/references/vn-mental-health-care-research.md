# VN Mental-Health / Psychiatry / PPD Doctor Research

Verified 2026-08-18 while enriching HCMC psychiatrists for postpartum depression
(trầm cảm sau sinh) — a second-opinion research brief. Extends the parent playbook
(`references/vn-hospital-doctor-research.md`) to the psychiatry/mental-health domain.
Use when the ask is psychiatrists / psychologists / depression / PPD in HCMC.

## Vinmec doctor profiles (the key HCMC mental-health network)
- URL pattern: `vinmec.com/vie/chuyen-gia-y-te/<slug>-<id>-vi` (English:
  `vinmec.com/eng/professionals/<slug>-<id>-en`). Examples seen: nguyen-trung-nghia-51753,
  huynh-thanh-tan-51812.
- **Field to trust above all: "Nơi làm việc" = the CURRENT campus.** One specialist can
  hold titled roles at BOTH Vinmec Times City (Hà Nội) AND Vinmec Central Park (HCMC).
  E.g. Nguyễn Trung Nghĩa is "Trưởng CK Sức khỏe Tinh thần Central Park" + "Trưởng CK
  Tâm thần Times City"; Huỳnh Thanh Tân's "Nơi làm việc" = Times City (Hà Nội) even
  though others claimed Central Park.
- Profile fields: "Chức vụ", "Số năm kinh nghiệm", "Quá trình đào tạo", "Thế mạnh
  chuyên môn"/"Các vấn đề lâm sàng" (strongest condition signal), memberships, awards,
  publications. Booking: `vinmec.com/vie/dang-ky-kham/?doctor_id=<N>`.
- **Patient rating (only public recency-weighted scores found)**: "4.9 trên 5
  (+177 khách hàng đánh giá)". Published only once a doctor has ≥30 surveys in the last
  8 quarters; includes sub-scores (tác phong diện mạo, giao tiếp, năng lực chuyên môn,
  thời gian thăm khám). Quote verbatim.
- Mental-health centre: "Trung tâm Chăm sóc Sức khỏe Tinh thần"
  (`/vie/co-so-y-te/trung-tam-cham-soc-suc-khoe-tinh-than-98706-vi-tam-ly`).

## AIH — Bệnh viện Quốc tế Mỹ (aih.com.vn)
- The homepage embeds the ENTIRE doctor roster server-side (name + speciality + blurb).
  Grep directly: `curl aih.com.vn` then `re.finditer(r'<Name>', text)` with context
  (±160 chars) to read the speciality. Use when a named "doctor" must be confirmed as
  the right physician/specialty at a given hospital.

## BookingCare (cross-check aggregator)
- Doctor pages carry a "Khám và điều trị" breakdown by patient subgroup — the strongest
  explicit condition signal; e.g. Lê Hoàng Ngọc Trâm under "Phụ nữ mang thai": "Trầm cảm
  chu sinh (trầm cảm trong lúc mang thai, và sau sinh); Loạn thần sau sinh."
- Listickles such as "6 bác sĩ khám trầm cảm sau sinh giỏi TPHCM" and "Trầm cảm khi
  mang thai … TPHCM" name additional specialists + their current clinic + "Cập nhật lần
  cuối" date. Prefer the NEWEST version — schedule details drift (FV slot-day for
  Ngô Tích Linh: older version = Mon/Fri, 27/07/2026 version = Tue). They also name
  non-physician psychologists (e.g. SunnyCare) for therapy-only options.
- youmed.vn is a JS SPA — skip; use the backend/hospital primary instead.

## Title ladder (seniority proxy)
BS → ThS/CKI → CKII → TS → PGS/GS; nội trú/BSNT usually ~8–12 yrs, CKII ~15–25,
TS/PGS ~20+. Prefer stated "X năm kinh nghiệm" on the hospital profile; else estimate
from graduation/residency years and label ước tính.

## Verification traps — FLAG in the deliverable, never silently drop
1. **NAME ≠ SPECIALTY (highest risk).** A hospital's doctor of a given name may be a
   DIFFERENT physician than the specialty you want. Real case: AIH "Nguyễn Hồng Trung"
   is an orthopedic-trauma surgeon & Medical Director (ThS Ngoại khoa, Huế), NOT a
   psychiatrist. Read the roster's specialty field; never infer from the name a search
   hit returned.
2. **AGGREGATOR "city" FIELD ≠ real practice site.** BookingCare listed Nguyễn Hữu Lợi
   under "Hà Nội" (Viện Pháp y Tâm thần Trung ương = Hanoi forensic psychiatry) while a
   candidate list assumed HCMC. Cross-check the doctor's actual hospital + city.
3. **THIRD-PARTY "campus" CLAIMS** must be checked against the hospital's own profile
   "Nơi làm việc" (Huỳnh Thanh Tân "Central Park" claim vs official Times City page).
4. **Multi-affiliation candidates**: verify each site separately (Ngô Tích Linh = UMC +
   FV + private clinic all independently confirmed; dual-campus Vinmec roles).

## Verified HCMC psychiatry shortlist (as of 2026-08, cite-as-is)
- TS.BS Ngô Tích Linh — Chủ nhiệm Bộ môn Tâm thần UMP; Trưởng PK Tâm thần kinh UMC
  (215 Hồng Bàng Q5); senior psychiatrist BV FV (Q7); private clinic Q5. 35+ yrs, MD 1985,
  PhD 1997. Explicit PPD experience (BookingCare #1).
- ThS.BS Lê Hoàng Ngọc Trâm — **Senior Consultant, Psychiatry, BV FV (Q7) since 2022**;
  earlier consultant at BV Quốc tế City (Bình Tân) 2020–22 & Vạn Hạnh 2021–22 (all three
  in her FV official profile). Explicit perinatal (trầm cảm chu sinh / loạn thần sau sinh)
  + stress/PPD + TMS for depression. MD 2017, ThS Tâm thần UMP 2020. **Best PPD-matching
  psychiatrist in the 6-hospital set (FV).**
- ThS.BSCKI.BSNT Nguyễn Trung Nghĩa — Trưởng CK Sức khỏe Tinh thần **Vinmec Central
  Park (HCMC)** + Times City. Valedictorian psychiatry residency UMP. 4.9/5 (177 reviews).
- ThS.BS Nguyễn Minh Mẫn — Trưởng Đơn vị Tâm lý Lâm sàng UMC; physician-psychologist
  (Mahidol/Nebraska/U-Washington). More counselling than prescribing psychiatry.

### Flagged / removed
- Nguyễn Hồng Trung (AIH) — orthopedic surgeon/Medical Director, NOT psychiatry. Remove.
- Nguyễn Hữu Lợi — Hanoi (Viện Pháp y Tâm thần TƯ, forensic). HCMC NOT verifiable; video-only.
- Huỳnh Thanh Tân — official Vinmec profile = Vinmec Times City (Hà Nội); Central Park
  claim unverified. Rating 4.9/5 (95 reviews) confirmed. Offers rTMS for patients avoiding
  meds incl. pregnant/nursing women.

### Additional HCMC specialists found (missed before), explicit perinatal/PPD focus
- ThS.BSCKI Trần Nguyễn Khánh Minh — Trung tâm Y khoa Vạn Hạnh, Q3; internal-residency
  psychiatry UMP; explicit trầm cảm khi mang thai.
- BSCKII Trần Minh Khuyên — Phòng khám BV ĐHYD 1 (20-22 Dương Quang Trung Q10) + private
  PM Q11; former Head of clinical dept BV Tâm thần TPHCM; Paris psychotherapy cert.
- BSCKII Nguyễn Ngọc Quang — BV Chợ Rẫy (Tâm Thần kinh); former Trưởng khoa Tâm thần,
  BV Tâm thần TPHCM; pregnancy-depression author/expert.
- ThS.BS Nguyễn Thi Phú — BV ĐHYD/UMC + Hello Doctor clinic (152/6 Thành Thái Q10); ~20 yrs.
- ThS.BS Lê Nguyễn Thụy Phương — psychiatrist BV FV + Giám đốc Y khoa HYPPO Clinic;
  ~15 yrs; depression/bipolar.
- BSCKI Lê Quốc Nam — private PM Tâm thần kinh Quốc Nam (5/35 Nơ Trang Long, Q Bình Thạnh);
  ~30 yrs; Paris psychotherapy.
- BSCKI Nguyễn Trọng Tuân — BV Tâm thần TPHCM; FFI France.
- Psychologist (non-physician): TS Sunny Đặng Phương / SunnyCare (Bình Thạnh) — therapy only.

## On-staff named doctors for the 6 target hospitals (verified 2026-08-18)
Second-opinion brief → must name the ACTUAL psychiatrist at EACH hospital from the hospital's
own profile, not a regional shortlist. Results:
- **Tam Anh HCMC**: ThS.BS Nguyễn An Khải — Bác sĩ Tâm thần, Khoa Thần kinh, Trung tâm Khoa
  học Thần kinh BVĐK Tâm Anh TP.HCM. MD UMP 2020, MSc Nội khoa–Tâm thần UMP 2025; adult
  depression/anxiety/bipolar/psychosis. Joined Tam Anh 2026 (recent). NO PPD listing.
  https://tamanhhospital.vn/chuyen-gia/nguyen-an-khai/ (Tam Anh Hà Nội's psychiatrist
  Phạm Văn Dương is NOT HCMC.)
- **City International (CIH)**: NO current named PPD psych on the public site. Psychiatry
  sits under the neurology-led Neuroscience Centre (Medical Director PGS.TS.BS Nguyễn Thi
  Hùng). Its former named mood/insomnia psychiatrist Lê Hoàng Ngọc Trâm left for FV in 2022.
- **FV Hospital (full psychiatry roster)** — https://www.fvhospital.com/en/specialties/psychiatry/meet-our-experts/ :
  Lê Hoàng Ngọc Trâm (PPD⭐, since 2022) · Ngô Tích Linh (also UMC Head of Psychiatry) ·
  Nguyễn Đào Uyên Trang (mood-disorder mgmt, since 2024) · Đào Thị Thu Hương (MDD/bipolar,
  since 2024) · Phan Duy Thúc (US-trained child/adult, ABPN). Each `/doctors/<slug>/` bio is
  behind a long nav menu — filter from the last `Dr.`/`Dr ` heading. FV hotline (028) 35 11 33 33.
- **UMC**: ThS.BS Nguyễn Minh Mẫn (Trưởng Đơn vị Tâm lý Lâm sàng; ~25 yrs, depression/suicide
  prevention; youmed.vn profile) · TS.BS Ngô Tích Linh (Chủ nhiệm Bộ môn Tâm thần + Trưởng PK
  Tâm thần kinh UMC) · ThS.BS Nguyễn Thi Phú.
- **AIH**: Dr. Mihajlovic Jadranka — listed under PSYCHIATRY but is a physician with a
  mental-health/wellness focus (NOT board psychiatrist; grad 2001 Serbia; EN/PT/DE/SR).
  Clinical psychologist: Ms. Ho Ngọc Bảo Trân (MSc Clinical Psychology USSH 2024; VN/EN).
  https://aih.com.vn/en/doctor/en-mihajlovic-jadranka-dr
- **Vinmec Central Park** (Đơn vị Sức khỏe Tâm thần): ThS.BSNT Nguyễn Thiên Hưng (psychiatrist;
  UMP HCMC; depression/bipolar/anxiety; since 2023) + ThS. Trần Cẩm Thuỳ (psychologist & IMHC
  team lead, 20+ yrs, depression/anxiety/PTSD, VN/EN/FR/ES). Note UI expert page:
  https://www.vinmec.com/vie/chuyen-gia-y-te/nguyen-thien-hung-51916-vi . Vinmec Central Park
  hotline 028 3622 1166. Nguyễn Trung Nghĩa is the network/IMHC head (Times City base).
- **Gap to state honestly**: no source declares a dedicated PPD-only psychiatrist at UMC,
  Tam Anh HCMC, AIH, or Vinmec Central Park; the clearest pregnancy/postpartum-explicit
  psychiatrist in this 6-hospital set is Lê Hoàng Ngọc Trâm (FV).
