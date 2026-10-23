# Brief template for one /swarm lane

Copy this to `<prefix>-brief-<lane>.md` in the project folder and fill the angle brackets. Write it in UTF-8. Keep the agent's prompt short ("read this brief and execute it"); the work lives in the file because long prompts get mangled by terminals and a file does not.

```markdown
# Brief <lane>: <one-line scope>

Folder: this folder. Output file: `<prefix>-<lane>.md`. Throwaway files go in `_<prefix>/`. Today is <date> (<timezone>).
Context: <who the work is for, in two or three sentences>. Another agent (`<other-lane>`) covers <its slice>; stay on <this slice>.

## Task
1. <Build the candidate list: what to include, target count, how many to keep after ranking.>
2. <For each item, the exact fields to collect.>
3. <Scoring rubric: criteria, scale, maximum, tie-break, caps (for example "no independent evidence caps that criterion at 1").>
4. <Any extra table the reader needs.>

## Evidence rules
- Allowed, by weight: <official documents, primary sources, dated news from named outlets, ...>.
- Excluded as evidence: <forums, social media, anonymous testimonials, SEO list sites that copy each other, ...>.
- Label every claim: VERIFIED (independent or primary source seen; URL and date), PARTIAL, CLAIMED (the subject's own page only), NOT FOUND, UNVERIFIED. Never invent figures, names, licence numbers or contact details. NOT FOUND is an acceptable answer.

## Hard rules
1. Do not print or paste raw page dumps, raw HTML or raw JSON into the terminal or any file. Extract fields with a script and write short rows.
2. No personal contact details of private individuals. A business hotline or domain is allowed as an identifier.
3. Search and read sources in <language> first. Write findings in <language> (headers may be English).
4. UTF-8 for all files; in Python pass encoding="utf-8" and reconfigure stdout. Avoid the dollar sign in shell text.
5. No dozens of browser tabs; fetch with scripts and keep only the fields you need.

## Output
`<prefix>-<lane>.md`: Method and evidence limits; Candidate table (fields, labels, URL, date); Scores and ranking; <extra sections>; What the sources agree on (5 bullets); Where sources conflict or are thin; Sources (numbered).

## Last action (mandatory)
When the file is finished, as your very last action run:
herdr agent prompt <caller-pane-id> "<lane> finished: N rows, file <prefix>-<lane>.md"
(replace N with the real row count; do not use --wait). If you could not finish, still run it with the true state, for example "<lane> finished: partial, file <prefix>-<lane>.md".
```

Why each part exists:

- **Context and the other lane's slice** keep lanes from overlapping and let the agent see the purpose behind the task.
- **Labels and "NOT FOUND is acceptable"** stop agents filling gaps with plausible inventions; a table full of honest NOT FOUND rows is more useful than a complete-looking one that is wrong.
- **Hard rules 1-2** exist because earlier agents were stopped by content filters and by runaway output when briefs left them out.
- **The last action** is how the caller learns the lane is done without polling.
