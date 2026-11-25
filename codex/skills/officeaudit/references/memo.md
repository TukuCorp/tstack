# /officeaudit memo

Read the memo as the skeptical reader who has to decide: would an investment committee, a funder or a client approve this on what is written? This review covers the argument. The numbers belong to `/officeaudit deck`; when the memo has figures that matter, run that check too and merge both logs.

## 1. Classify

Name the deliverable (IC or investment memo, funding or grant proposal, strategy brief, workplan, recommendation note), the decision it asks for, and who decides. Find the brief it answers: the fund's mandate, the client's terms of reference, the grant's call. Use the one the memo cites or the user gives; if neither exists, ask for it, and if none can be had, skip check 6 and say so in the verdict line.

No script covers the argument, so this subcommand starts with a direct read. Read the whole memo before judging any part of it.

## 2. Checks

1. **Ask**: the decision, amount and timing are explicit and appear early. "Approve USD 2m for a Series A at a USD 8m pre-money by March" passes. "Discuss the opportunity" does not. An ask that appears only in an appendix counts as missing from the front.
2. **Thesis**: the case can be proven wrong. "If the utility signs the PPA, revenue reaches X by year 3" can fail; "the market is attractive" cannot. Flag a thesis that no outcome would disprove.
3. **Success measures**: each goal has a measure, a baseline and a date, and the measure tracks the goal. Flag vanity measures, such as MOUs signed with no offtake or pipeline value with no conversion rate.
4. **Proportion**: effort and risk fit the likely impact. Flag a platform built for a one-off, a heavy process on a small ticket, or a large bet on low-confidence evidence.
5. **Costs and resources**: money, people, time and dependencies are stated, including the ones the memo would rather not mention (follow-on reserves, management time, a partner's approval). A cost nobody stated is a hidden risk.
6. **Fit**: the memo matches the brief from step 1 (sector, geography, stage, ticket size, impact criteria) and says so where it stretches it.
7. **Alternatives**: the memo names what the money or time could do instead, and why this option wins. Silence on alternatives is a finding when the stakes are material.
8. **Risks**: the main risks are named, with what would trigger them and what limits the damage. A risk list without mitigations, or with only generic ones ("market risk"), is a finding.
9. **Consistency**: the summary, body and appendix make the same case; no section quietly contradicts another.

Most findings here are judgment, so mark them `needs review` unless the text itself proves the point. A gap the text shows is `confirmed`: the ask is missing, the risk list has no mitigations, two sections give different amounts. Put the biggest risk to the decision first. Point to the problem and suggest a direction; don't rewrite the author's strategy. Note what is well argued, so the author knows what to keep.

## 3. Report

```
## Memo review: <file> — <Ready | Ready with caveats | Not ready | Not assessable>
<one-line reason> | Decision: <ask> | Decides: <who> | Brief: <file or none>

| # | Severity | Status | Location | Finding | Fix |
|---|---|---|---|---|---|
| 1 | critical | needs review | §2 Thesis | No outcome would disprove "demand is growing fast" | state the demand level by year 3 that the case needs |

### Well argued
<sections that pass, one line each>
```

Severity follows the shared rules: `critical` when the gap would change the decision, `major` when it weakens the case, `minor` for framing.
