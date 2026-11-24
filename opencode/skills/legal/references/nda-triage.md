# NDA triage

Screen the NDA against each criterion, classify it, report. Positions below are defaults; the playbook overrides them.

## Defaults

- Mutual, unless only one side discloses (then unilateral in the right direction).
- Agreement term 1-3 years; confidentiality survives 2-5 years; trade secrets as long as they stay secret.
- All five standard carveouts present (below).
- No non-solicit, non-compete, exclusivity or standstill.
- No residuals clause, or one limited to unaided memory.
- Governing law in a mainstream commercial jurisdiction, same as the courts; no mandatory arbitration.

## Investor-specific checks

A fund sees many companies in the same space, so these matter more than in a corporate NDA:
- **Freedom to invest**: the NDA must not stop the fund or its affiliates from evaluating, investing in or advising companies that compete with the discloser. Look for an express acknowledgement of this; its absence is YELLOW, a clause that restricts it is RED.
- **Portfolio companies**: information must not be deemed shared with portfolio companies, and the fund must not be liable for what a portfolio company does independently.
- **Permitted recipients**: partners, employees, LPs where needed, co-investors under similar terms, and advisers (lawyers, accountants).
- **Who signs**: the fund or management entity, not an individual partner personally.
- **Standstill** is normal only in a public-company or M&A context; otherwise RED.

## Screening checklist

1. **Structure**: type (mutual / unilateral disclosing / unilateral receiving), right for the relationship, standalone (not a clause in a bigger agreement).
2. **Definition of confidential information**: not "all information of any kind"; marking rules workable (written confirmation of oral disclosure within ~30 days); does not sweep in public or independently developed information.
3. **Obligations**: reasonable care (at least as for own information); use limited to the stated purpose; disclosure to need-to-know people under similar duties; nothing impractical (logs, mandatory encryption).
4. **Standard carveouts** (all five): public through no fault of the recipient; already known; independently developed without use of the information; received from a third party without restriction; required by law or legal process (with notice where allowed).
5. **Permitted disclosures**: employees, contractors and advisers under similar duties, affiliates if needed, legal or regulatory demands.
6. **Term**: agreement and survival in range; not perpetual except for trade secrets.
7. **Return or destruction**: on request or termination; retention allowed for legal, compliance and backup copies; certification fine, sworn affidavit onerous.
8. **Remedies**: injunctive-relief acknowledgement is normal; no liquidated damages; symmetric in a mutual NDA.
9. **Red-flag provisions**: non-solicit, non-compete, exclusivity, standstill, broad residuals, any IP assignment or licence, audit rights.
10. **Law and forum**: mainstream jurisdiction, law and courts consistent, no mandatory arbitration.

## Classification

**GREEN (sign)**: all true: right type and direction, all carveouts, term in range, no restrictive covenants, residuals absent or narrow, mainstream law, no liquidated damages, employees/advisers permitted, retention exception present, definition reasonable, freedom to invest preserved.

**YELLOW (fix, then sign)**: not fundamentally wrong, but one or more of: broader definition than ideal; term above range but within market (5-year term, 7-year survival); one carveout missing that is easy to add; narrow residuals; acceptable but non-preferred jurisdiction; minor asymmetry; workable marking rules; no explicit retention exception; no express freedom-to-invest acknowledgement; odd but harmless provisions.

**RED (do not sign as is)**: one or more of: wrong type or direction; missing independent-development or legal-compulsion carveout; non-solicit, non-compete, exclusivity or (outside M&A) standstill; 10+ years or perpetual without a trade-secret reason; definition covering public or independently developed information; broad residuals; IP assignment or licence; liquidated damages; unbounded audit rights; hostile jurisdiction with mandatory arbitration; restriction on investing in competitors; not really an NDA.

## Standard fixes

- **Overbroad definition**: limit to non-public information disclosed for the purpose that is marked confidential or that a reasonable person would understand to be confidential.
- **Missing independent development**: add the standard carveout; without it, an internal or portfolio project can be claimed as derived.
- **Non-solicit**: delete. If they insist: targeted solicitation only (general ads excluded), 12 months maximum.
- **Residuals**: resist. If required: general ideas retained in the unaided memory of people with authorised access; excludes trade secrets and patentable information; no IP licence.
- **Perpetual term**: replace with 2-5 years from disclosure or termination, whichever is later; trade secrets for as long as they qualify.
- **No freedom to invest**: add "Recipient may evaluate, invest in or advise companies that compete with Discloser, provided it does not use Confidential Information in doing so."

## Report format

```
## NDA triage: <GREEN | YELLOW | RED>

Route: NDA | Counterparty: <name> | Type: <mutual/unilateral> | Term: <x> (survival <y>) | Law: <jurisdiction> | Review basis: <playbook / defaults / both>

| Criterion | Result | Note |
|---|---|---|
| Structure | PASS / FLAG / FAIL | ... |
| ... one row per checklist item ... |

### Issues
**<n>. <title> (YELLOW/RED)** — §<x>: "<exact quote>"
Risk: <what could go wrong>. Fix: <exact replacement language>.

### Recommendation
<sign / sign after these fixes / do not sign: send our form or counter>

Screening aid, not legal advice; send RED items to counsel.
```

If the document is labelled an NDA but carries commercial terms, classify RED, say why in one line, and switch to the contract route.
