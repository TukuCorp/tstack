# Vietnam Hospitality / Accommodation Research

Extends `product-research-local` from retail products to hotels, flights, and accommodation.
Learned on the Hanoi Nov 3-7, 2026 hotel search (2.5M VND ceiling, Old Quarter).

## Booking-site matrix

| Site | Best for | Notes |
|---|---|---|
| **Agoda** | Lowest nightly rates | Consistently cheapest for Hanoi Old Quarter boutiques; shows per-night calendar prices |
| **Kayak** | Price comparison + per-day breakdown | Shows exact dates; good for "which night is cheapest" |
| **Hotels.com** | Deal alerts, last-minute discounts | "We have 1 left at" flash deals; good for last-minute |
| **Tripadvisor** | Reviews + ranking | Use "Cheap Hotels" + "Best Value" sort; check dates in URL (default Nov 8-9) |
| **Expedia / Travelocity** | Cross-check | Similar rates to Hotels.com |
| **Trivago** | Price trend by date | Good for "which day is cheapest" trend charts |

## Search procedure

1. TripAdvisor "Cheap Hotels" for the city + dates → note TA rating + review count.
2. Cross-check prices on Agoda and Kayak for the exact dates.
3. Filter by user's ceiling and central location.
4. Return ~5 with: name, area, TA rating (reviews), price/night (VND), booking link.

## Hanoi Old Quarter ~2.5M VND/night (high TA, Nov 2026)

| Hotel | Area | TA | Price/night |
|---|---|---|---|
| Bespoke Trendy Hotel Hanoi | 12-14 Nguyen Quang Bich | 5.0 (6,074) | 1.1-2.6M VND |
| AIRA Boutique Hanoi Hotel & Spa | Old Quarter | 5.0 (4,049) | 1.5-2.3M VND |
| Hanoi La Selva Hotel | 57 Lo Su | 5.0 (2,203) | 0.7-2.0M VND |
| Bendecir Hotel & Spa | 27 Lo Su | 4.8 (1,062) | 1.0-1.8M VND |
| Hanoi La Palm Premier Hotel & Spa | 35 Hang Quat | 4.9 (2,807) | 0.9-1.8M VND |
| Meritel Hanoi | 151-153 Hang Bong | 5.0 (3,593) | 1.9-4.0M VND |
| La Siesta Premium Hang Be | Hang Be | 5.0 (4,315) | ~2.4M VND |
| Hanoi Splendid Premium Hotel | 36 Lo Su | 5.0 (1,004) | ~2.4M VND |
| The Oriental Jade Hotel (step-up) | 92-94 Hang Trong | 5.0 (6,218) | 3.2-4.2M VND |

## Demand-layer triangulation (why is it expensive that week)

Per `no-key-web-research` Rung 7: triangulate four demand layers before answering:
1. **Expos/conferences at destination** (Vietnam Aerospace Forum Nov 4-6, Vietfood Nov 4-7,
   IEAE Nov 5-7, Vietnam Export Promotion Forum Nov 4)
2. **Sports/mass-participation events** (Standard Chartered Hanoi Marathon Nov 6-8)
3. **Public-holiday long weekends at BOTH endpoints** (Singapore Deepavali Nov 8, observed Nov 9;
   SG school holidays Nov 21-Dec 31)
4. **Government summits holding inventory** (CLMV 12 + ACMECS 11, Hanoi Nov 2026)

A sell-out is usually the stack, not any single event.

## User rules (durable)

- Ceiling ~2.5M VND/night, central/Old Quarter (Hoan Kiem) in Hanoi.
- Book via Agoda/Kayak (lowest rates); verify reviews on TripAdvisor.
- Breakfast included on most Old Quarter boutique hotels.
- Lock refundable rates early when dates overlap expos/summits.
