# Explainer page — section patterns

Each section is a claim the reader can push back on. Keep an eyebrow label
("3 · The method"), a plain heading, an optional native-language subtitle, then
one visual with short prose beside it. Class names refer to
`assets/explainer-template.html`.

## 1. Answer first (`header.hero`)
- Eyebrow: project · audience · "status at <date>".
- H1: the reader's question as a statement ("How we match X to Y").
- `.answer`: 2–4 sentences. Bold the one-line essence. State the boundary
  (what does *not* come to us / what we do not do) here if trust matters.
- `.status` pills: done (green), waiting (amber). Max 3.
- `.kpis`: 3–4 numbers with a plain label each. Prefer numbers the reader can
  act on ("4 + 42 codes for you to review") over vanity totals.

## 2. Problem by analogy (`.analogy`)
Two cards side by side with 3 real rows each, an arrow between, labelled with
your deliverable. Then a ≤6-node Mermaid flow following one real item end to
end, with your piece coloured via `classDef`. Caption: "The blue box is the only
piece we supply."

## 3. Roles and boundaries (`.grid2 .side`)
Two cards: "We deliver" / "You keep and do". 3–5 bullets each. Then a `.lock`
callout naming exactly what data you did and did not see. Skip if one party.

## 4. The method
- One Mermaid `flowchart TD` of the steps, with counts on the branch edges
  ("yes: 471", "no: 116").
- `.steplist` cards numbered 1..n: heading + 2–4 plain sentences. When several
  actors run in parallel (coders, teams, models), show `.coders` sub-cards, each
  with its stable colour.
- If a step relies on an external standard or chain, give it its own small
  `flowchart TB` and a caption explaining any surprising hop.

## 5. Worked examples (`#tabs` + `#ex`)
4–6 real cases in the `EX` array, ordered easy → hard:
- 2–3 where everyone agrees (shows the normal case and a useful nuance),
- 1 where the majority was wrong and the method caught it,
- 1 where your first answer was wrong (honesty builds trust),
- 1 genuinely ambiguous case and how the reader resolves it.
Each: id, native label, plain English label, each actor's pick with ✓/✗,
a verdict badge, 2–3 sentence takeaway.

## 6. Quality signals (`.grid3 .conf`)
One card per level (High/Medium/Low or similar): count and share, what it
means in one sentence, what the reader should do. Add one calibration fact if
you have it ("when both said High, 202 of 203 agreed").

## 7. Results
- `.bars` for pairwise or category rates (label · bar · value).
- One sentence turning any statistic into plain words, plus the pass mark and
  when it was set.
- `.split` stacked bar for how disputes/outcomes resolved, with a legend in
  plain words.
- One sentence on where problems cluster and why.

## 8. What we need from you
- A: decisions table (id · item · current · proposed · why).
- B: a Mermaid decision rule (`flowchart LR`, yes/no diamonds) for cases the
  reader must judge themselves.
- C: `.todo` tick-list of open questions; flag the one that blocks a deadline.
- `.timeline`: done (green) · now (amber) · next (grey), with dates.

## 9. Limits (`.grid2 .panel`)
3–4 cards: heading = the limit, body = consequence + what to do instead.
One muted line for out-of-scope items.

## 10. Glossary (`details`)
Only terms that appear on the page. One or two sentences each, no new jargon.

## 11. Footer
Scope statement (what you do / do not do), sources with dates, working files.
Keep any mandatory disclaimers (e.g. synthetic data) here and in the hero.
