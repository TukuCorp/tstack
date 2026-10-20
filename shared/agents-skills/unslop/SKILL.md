---
name: unslop
description: Cut AI tells from prose meant for human readers (docs, reports, emails, slides, chat replies). Skip code, identifiers, quoted or reviewer text, and a skill's or domain's defined vocabulary.
disable-model-invocation: true
---

# Unslop

Edit text to remove AI patterns and add human voice. This applies to prose meant for human readers. Leave code, identifiers, commands, quoted text and reviewer comments as they are.

These patterns are tells, not proof. One hit means little. A cluster of different kinds means a lot. Fixing a tell means putting back the missing specific, not swapping a synonym: the model's habit is to replace a precise fact with a generic one, and a new word over the same empty sentence still reads as slop. Surface marks (em dashes, curly quotes, boldface, emoji, Title Case, Markdown) are the weakest signals alone, since people produce them too, so rules 13 to 19 are house style first and tells second. Clean grammar, formal register and ordinary transition words are not tells.

## Process

1. Find the house voice. If the text belongs to an organization or a series, such as a training deck, a client report or a docs site, read that organization's existing documents of the same kind first. Note how they title things, how long headings run and what register the body uses. Where the house style contradicts a rule below, the house style wins.
2. Respect defined vocabulary. A domain glossary (such as a project's `CONTEXT.md`) or a skill's glossary overrides the rules below. If codebase-design defines "leverage" and "surface" as terms, keep them, even though rules 26 and 31 would cut them.
3. Scan for the patterns below.
4. Rewrite. Preserve meaning, match intended tone.
5. Add soul (see next section), within the register the house voice allows.
6. Self-audit: "What makes this obviously AI generated?" Fix remaining tells.
7. Mechanical check before finishing. Grep the draft for em dashes, curly quotes, bracketed placeholders and the flagged words from rules 7, 23, 26, 31 and 36 to 38, then fix each hit unless a glossary or quoted text covers it:

```bash
grep -nE '—|[“”‘’]' draft.md
grep -niwE 'additionally|crucial|delve|enduring|enhance|fostering|garner|interplay|intricate|landscape|pivotal|showcase|tapestry|testament|underscore|vibrant|substrate|wedge|vector|locus|vantage|nexus|primitive|harness|surface|bedrock|scaffolding|modality|paradigm|gold-plating|ratchet|evacuate|endgame|north star|flywheel|utilize|leverage|facilitate|numerous|in the event that|bolstered|boasts|meticulous|meticulously|robust|multifaceted|deep dive|worth noting|important to note|associated with|plays a role|finds you well' draft.md
grep -nE '\[(Your|Insert|Describe|Name)[^]]*\]' draft.md
```

For text that isn't in a file, write it to a temp file first or run the same check by eye, word by word.

When revising a deliverable against reviewer feedback, also follow `references/review-feedback.md`.

## Adding soul

Removing patterns is half the job. Sterile, voiceless writing is just as obvious.

- **Have opinions.** React to facts instead of neutrally listing pros and cons.
- **Vary rhythm.** Short sentences. Then longer ones that take their time. Mix it up.
- **Acknowledge complexity.** "Impressive but also kind of unsettling" beats "impressive."
- **Use "I" when it fits.** First person isn't unprofessional.
- **Let some mess in.** Perfect structure looks machine-made.
- **Be specific.** Not "this is concerning" but "there's something unsettling about agents churning away at 3am."
- **Write the way people do.** Plain "is" and "has", "wrote" and "used" over "authored" and "utilized", "one of the best" or "was the first" when true, and an occasional "perhaps" or "very".

Calibrate this to the audience. Opinions, first person and deliberate mess suit essays, posts and internal notes. Institutional deliverables such as training slides, client reports and proposals get their personality from specifics and accurate framing, not from a quippy narrator. Reviewers of those read punchy one-liners and fragments as machine-made.

## Patterns to detect and fix

### Content

1. **Puffery.** "pivotal moment", "testament to", "evolving landscape", "setting the stage for", "indelible mark", "deeply rooted", "key turning point", "focal point", "reflects broader", "symbolizing its enduring", "plays a vital role", "a significant shift". Cut puffery, state what happened.
2. **Name-dropping.** Listing media outlets without context. Pick one, say what was said. Also cut "active social media presence", "featured in X and other outlets", "profiled in trade publications" and "independent coverage". Models credit their own thin analysis to the source, so check what the source actually says.
3. **Superficial -ing phrases.** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering...", "contributing to...", "encompassing...", "further enhancing its significance". A tacked-on participle clause that says what the fact means is the tell. Delete or expand with real sources.
4. **Promotional language.** "nestled", "vibrant", "breathtaking", "groundbreaking", "renowned", "stunning", "must-visit", "boasts a", "rich", "profound", "exemplifies", "commitment to", "diverse array", "in the heart of", "seamlessly". Newer models are subtler than "the best", and quiet positivity counts. Use neutral descriptions.
5. **Vague attributions.** "Experts believe", "Industry reports suggest", "Some critics argue", "Observers have cited", "several sources", "described in scholarship". Also plurals for a single source ("scholars" when one is cited). Name the source or delete.
6. **Formulaic challenges.** "Despite challenges... continues to thrive." Replace with specific facts. The tell is the rigid formula, not a mention of challenges. Also cut "Future Prospects" and "Future Outlook" closers.

### Language

7. **AI vocabulary.** Additionally, crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore, vibrant, align with, boasts, bolstered, deep dive, emphasizing, highlight (as a verb), key (as an adjective), meticulous, multifaceted, robust, valuable, and "Additionally" opening a sentence. Replace with plain words. The list drifts by model generation (delve faded in 2025, newer models lean on multifaceted, foster, prioritize, quietly), so judge by clusters: one or two may be coincidence, many together are among the strongest tells. A synonym of a flagged word is not itself a tell, and a word in its literal sense is fine ("underscore" as a punctuation mark).
8. **Fancy ways to say "is".** "serves as", "stands as", "boasts", "features", "marks", "functions as", "represents", "holds the distinction of being", and the definition opener "X refers to...". Just say "is" or "has".
9. **"Not just X, but Y."** Also "not only... but also", "It's not X, it's Y", "Y rather than X" and "no X, no Y, just Z". State the point directly instead.
10. **Rule of three.** Forcing ideas into groups of three. Use the natural number. It makes a thin analysis look comprehensive, and it is a stronger tell where a person would not have bothered.
11. **Synonym cycling.** Protagonist, main character, central figure, hero all in one paragraph. Pick one, repeat it. A weaker tell today, so judge it with other signs.
12. **False ranges.** "from X to Y" where X and Y aren't on a meaningful scale ("from the bustling streets of Dhaka to the serene beaches of Cox's Bazar"). List topics directly.

### Style

13. **Em dash overuse.** Avoid em dashes entirely. Use periods or commas only (no parentheses, no en dashes, no hyphen-as-dash substitutes). Em dashes are an AI tell, and reaching for parentheses instead just trades one tell for another. If a thought needs separation, end the sentence or use a comma.
14. **Colon overuse.** Colons are fine before a list or example. Not as mid-sentence connectors. "If you're coming from traditional automation: instead of registering event handlers, you describe conditions" adds nothing with the colon. Rewrite to let the point stand on its own without comparison framing. "Describing when the scheduler should fire works best as plain English." Same meaning, no crutch punctuation. A colon in a title that follows a house "Label: Subject" pattern, like "DPPA: The Pathway to Green Procurement", is not a tell.
15. **Boldface overuse.** Don't bold every proper noun or acronym.
16. **Inline-header lists.** The tell is a bold label and colon that restates the line: "**Performance:** Performance improved...". Convert those to prose. A bold lead-in that ends in a period, names the item, and is followed by genuinely new detail ("**Schema in TypeScript.** Tables live in one file.") is fine, not a tell.
17. **Title case headings.** Use sentence case, unless the house documents use Title Case. Then match them.
18. **Decorative emojis.** Remove from headings and bullets.
19. **Curly quotes.** Replace with straight quotes. They prove little alone, since word processors and phones add them, but keep one style.

### Communication artifacts

20. **Chatbot phrases.** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!", "Would you like...", "Here is a...", "Is there anything else". Remove.
21. **Cutoff and source-availability disclaimers.** "While specific details are limited...", "based on available information", "aren't widely documented", "maintains a low profile". Find sources, say plainly what you could not find, or remove.
22. **Sycophantic tone.** "Great question! You're absolutely right!" Respond directly.

### Filler

23. **Filler phrases.** "In order to" becomes "To". "Due to the fact that" becomes "Because". "It is important to note that" gets deleted. "Worth noting", "it's crucial to remember" and "may vary" go the same way: give the fact itself.
24. **Excessive hedging.** "could potentially possibly be argued that it might" becomes "may". Cut stacked and disclaimer-style hedges, not every qualifier: a plain "perhaps", "very" or "tends to" is how people write.
25. **Generic conclusions.** "The future looks bright." State specific plans or facts. Also "In summary", "In conclusion", "Overall", and a closing line that restates each section's point.

### Jargon

26. **Abstract metaphor nouns.** Substrate, wedge, vector, locus, vantage, nexus, primitive (as noun), harness (as metaphor), surface (as in "API surface"), bedrock, scaffolding (as metaphor), modality, paradigm, gold-plating, ratchet (as metaphor), evacuate (for moving code), endgame, north star, flywheel. These read as technical but usually have a plainer concrete word. "Substrate" becomes "base". "Wedge in" becomes "add". "Vector" becomes "way" or "method". "Gold-plating" becomes "more than the job needs". "Ratchet" becomes the mechanism's real name or "a limit that only tightens". "Evacuate" becomes "move out". "Endgame" becomes "the last phase". Pick the concrete word.

### Plain speech

27. **Say what it does, not how it feels.** "the database stays close at hand", "SQL you can read", "types that follow your schema" name a feeling. The fix names the mechanism or a number: "`.toSQL()` returns the exact string sent to the database", "a column rename fails the build". Ask what the sentence tells the reader to do or know, then write that. If you can't restate it as a concrete instruction, fact, or number, cut it. One more check: if the sentence could appear unchanged in another project's docs, it says nothing about this one. Cut it. The model's default is to swap a precise fact for a generic one, so "inventor of the first train-coupling device" becomes "a revolutionary titan of industry". Put the specific back.
28. **Shorten or split dense sentences.** If the reader has to backtrack to parse a sentence, break it in two or drop clauses. One idea per sentence. Vary the length: a run of sentences of about the same size reads as machine-made too.
29. **Active voice.** Prefer it. Catch "is/are/was/were + past participle" and name the actor: "queries are validated" becomes "the compiler validates queries", "the file is parsed by the loader" becomes "the loader parses the file". Passive is fine only when the actor is unknown or genuinely doesn't matter.
30. **Cut adverbs, or use a stronger verb.** "runs quickly" becomes "is fast" or the number. "significantly improves" becomes the measured delta. An adverb propping up a weak verb means the verb is wrong. Keep a plain intensifier where a person would say it.
31. **Prefer the plain word.** "utilize" becomes "use", "leverage" becomes "use", "facilitate" becomes "help", "numerous" becomes "many", "in the event that" becomes "if". The fancier synonym is rarely clearer.

### Titles, slides and figures

32. **Conversational titles.** Headings written as a spoken aside, a setup or a line addressed to the reader: "So who do you actually call", "And soon it will cost you not to", "Where the cooling money is". A managing partner reviewing a training deck called the first one a weird tone that did not match the house style. A title names the topic, usually in 2 to 7 words, and follows the convention of the surrounding documents: "Efficiency Resources and Next Steps", "Refrigeration and Cooling are Key Cost Drivers". Never open a title with "So" or "And".
33. **Slogans in body copy.** Lines built to be quoted rather than to inform: "The cheapest kWh is the one you don't use", "That valve is where your money goes", "Catch the heat you already paid for before it leaves the site". A reviewer marked the last one awkward and replaced it with "Recover usable heat before it leaves through stacks, drains or ventilation." State the mechanism. In anything spoken, move the good line into the speaker notes instead of deleting it.
34. **Telegraphic fragments.** Body copy chopped into verbless pieces for punch: "Switch off what nothing is using.", "Heat. Boilers, dyeing, drying, finishing.", "Tower alone, chiller off." The first drew an "awkward" and became "Turn off idle equipment and unnecessary loads." Write full sentences. Fragments are fine in labels, table cells and chart annotations.
35. **Figures that do not reconcile.** Numbers on the same page that disagree, like "−50 kW you no longer buy" beside "−15%" and "750 kWp less"; a bar drawn at 20% for a 15% cut; a time or session number nobody confirmed; a label that contradicts its source, like "declared peak" for a peak the utility meters. Confident specifics nobody checked are slop too. Check every figure against the others on the page and against its source. If a fact is not confirmed, use a visible placeholder such as "Session X.Y" and flag it.

### Framing and register

36. **Stock correspondence.** "I hope this message finds you well", "I am writing to", "Dear [team]", and the clerk register: "apologizing for any inconvenience", "please point out any issues and I will try to resolve them". Start with the point and say what you did and what you need. Check that no bracketed placeholder such as "[Your Name]" is left.
37. **Tenuous significance.** A minor subject said to "play a role in" or "contribute to" something larger ("contributes to the broader history of early aviation"), or a fact said to have "generated debate", "prompted broader reflection" or "raised questions". Name the mechanism, or who argued what, or cut. Cut preambles that admit low importance and then claim importance.
38. **Vague connection.** "associated with", "connected to", "in connection with", "ventured into", "began his career as". State the relation: "was CEO of", "taught at", "ran for office".
39. **Section scaffolding.** Headings and blocks built from a template: "Challenges and Opportunities", "Future Outlook", "Key takeaways", "Questions to consider", a `---` rule between every section, emoji-labelled blocks, and a small table holding a handful of facts that fit in a sentence. Name each heading for its content and use prose for a few facts.
40. **Caveats that tell the reader how to read a claim.** "should be treated as X rather than Y", "does not by itself establish". State the claim at its real strength.

Rules 36 to 40 and the additions to rules 1 to 12, 19 to 25 and 27 to 30 draw on Wikipedia, "Signs of AI writing" (en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing, CC BY-SA 4.0), read 2026-10-21.
