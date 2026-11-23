# Near-controlled English (~80% ASD-STE100)

ASD-STE100 (Simplified Technical English) was written for aircraft maintenance
manuals, where a misread sentence is dangerous. Its constraints make any text
easier for non-specialists and non-native readers. Full compliance (approved
dictionary only) reads stiff, so aim for about 80%: keep the structural rules,
relax the vocabulary where a common word is clearer than the approved one.

## Rules to keep

1. **One idea per sentence.** Split at "and", "which", "while".
2. **Short sentences.** ≤20 words for descriptions, ≤20 for instructions; most
   should be 8–15.
3. **Short paragraphs.** ≤6 sentences; one topic each.
4. **Active voice.** Name who does it. "BIDV calculates", not "is calculated".
5. **Present tense** for how things work; past tense only for what happened.
6. **Instructions as imperatives**, one action per sentence: "Check these first."
7. **One word, one meaning.** Pick a term ("code", "sector", "coder") and never
   swap in a synonym. Define it at first use; list it in the glossary.
8. **Common words over jargon.** "use" not "utilise", "about" not "approximately",
   "agreement after removing luck" before "Cohen's kappa".
9. **No noun stacks** longer than three words ("emission factor database row" →
   "a row in the emission-factor database").
10. **Digits for numbers**, units always attached, dates unambiguous (5 Oct 2026).
11. **Say why** after a rule, in a separate sentence: "Coal and gas emit very
    differently. So two codes help."
12. **Put the condition first**: "If the purpose is known, use that sector."

## Before / after

| Before | After |
|---|---|
| Disagreements were adjudicated against NAICS definitions and the official concordance chain, with majority vote not being determinative. | For each disagreement, we read the official sector definitions. Then we follow the official code chain. The majority does not decide: the definitions decide. |
| Exact-sector κ of 0.80 clears the pre-registered 0.61 threshold. | After we remove agreement that could happen by luck, the score is 0.80. Before the check we set a pass mark of 0.61. It passes. |
| Utilisation of client-level physical activity data is recommended for high-materiality exposures. | For large clients, use their production or fuel data. A sector average is weak here. |

## Analogies

One analogy per page, introduced early, reused later. Good analogies map
structure, not just mood:

- translation between two dictionaries → any code or schema mapping
- two examiners marking the same paper separately → blind review, inter-rater checks
- a recipe vs the meal → model/method vs output
- a map vs the territory → summary vs data
- a relay race hand-off → pipeline stages and ownership boundaries
