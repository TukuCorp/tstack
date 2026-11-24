# Contract review

Read the whole contract before flagging anything: clauses interact (a broad indemnity can be capped by the liability clause; a definition can widen a covenant). Identify the type, confirm my side, then review each material clause against the playbook, falling back to the defaults here.

## Clauses to cover

Commercial agreements (vendor, services, licence, partnership):

| Clause | Check |
|---|---|
| Limitation of liability | cap size and basis (fixed, multiple of fees), mutual or not, carve-outs from the cap, consequential-damages exclusion and its carve-outs, per-claim or aggregate |
| Indemnification | mutual or not, triggers (IP, data breach, injury, any breach), capped or not, notice, control of defence and settlement |
| IP | each side keeps pre-existing IP, ownership of new work, work-for-hire scope, licence scope, feedback clauses |
| Data protection | DPA where personal data is processed, controller/processor roles, sub-processors, breach notice (72h under GDPR), transfers, deletion |
| Confidentiality | scope, term, carveouts, return or destruction (see `nda-triage.md`) |
| Reps and warranties | scope, disclaimers, survival |
| Term and termination | initial term, auto-renewal and notice window, termination for convenience, cure period, transition and survival |
| Law and disputes | law, venue, arbitration rules and seat, jury and class waivers, fee shifting |
| Assignment | consent, change of control |
| Payment, insurance, force majeure | net terms, late fees, escalators, coverage minimums, scope and exit rights |

Investment documents (term sheet, SAFE or note, SPA or SHA, side letter), read from the investor's side:

| Clause | Check |
|---|---|
| Economics | price or cap and discount, option pool in or out of the pre-money, liquidation preference (multiple, participating or not, seniority), dividends |
| Anti-dilution | broad-based weighted average is standard; full ratchet is RED |
| Pro rata and MFN | pro rata in future rounds; MFN on SAFEs or side letters, and whether it is limited to economic terms |
| Information and governance | information rights and their threshold, board or observer seat, protective provisions (consent matters) |
| Transfers and exits | ROFR, co-sale, drag-along (thresholds, minimum price, who can trigger), registration rights |
| Founder terms | vesting and acceleration, IP assignment from founders, non-competes where enforceable |
| Fund-specific | permitted transfers to affiliates or successor funds, confidentiality that lets us report to LPs, no liability for portfolio conflicts, ESG or sanctions reps the fund itself needs |

If a section is unusual or missing for its document type, say so.

## Grading

- **GREEN (accept)**: matches or beats my position, or a minor and commercially reasonable variation. Note only.
- **YELLOW (negotiate)**: outside my position but within market range. Give the redline, a fallback, and the cost of accepting as is.
- **RED (escalate)**: outside the acceptable range or materially risky: uncapped liability, broad uncapped indemnity, assignment of pre-existing IP, no DPA for personal data, unreasonable non-compete or exclusivity, full-ratchet anti-dilution, participating preference above 1x, drag-along with no price floor. Explain the risk, give market-standard language, estimate exposure, and name who should look (counsel, the partner on the deal).

## Redlines

For every YELLOW and RED item:

```
**§<x> <clause>** — <YELLOW/RED>, <Must-have / Should-have / Nice-to-have>
Current: "<exact quote>"
Proposed: "<ready-to-insert language>"
Why (shareable): <1-2 sentences for the other side's counsel>
Fallback: <what we accept if they refuse>
```

Be specific (insertable language, not advice), firm on what matters and reasonable elsewhere, and match the tone to the relationship (a lead investor's counsel, a founder, a vendor).

## Negotiation plan

- **Tier 1, must-haves**: deal breakers (uncapped exposure, regulated-data gaps, core IP, terms that break fund obligations). Never concede without escalation.
- **Tier 2, should-haves**: real risk with room to move (cap size, indemnity scope, termination rights, information rights).
- **Tier 3, nice-to-haves**: trade these for Tier 2 wins (preferred law when the other is fine, notice periods, definitions, insurance certificates).

## Report format

```
## Contract review: <document> — <overall risk: low / medium / high>

Route: contract | Type: <type> | Parties: <names and roles> | My side: <side> | Deadline: <date or none> | Review basis: <playbook / defaults / both>
Assumptions: <only if context was partial>

### Top issues
1. <one line each, 3-5 items, with GREEN/YELLOW/RED>

### Clause by clause
**<Clause> — <GREEN/YELLOW/RED>**: contract says <summary>; my position <x>; gap <y>; impact <z>.
(redline block for YELLOW/RED)

### Negotiation plan
<lead with, trade away, timing>

### Next steps
1. ...

Screening aid, not legal advice; send RED items to counsel.
```

For a contract over about 50 pages, offer to review the material sections first. For a non-English contract, ask whether to review in the original or in translation.
