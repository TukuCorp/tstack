# Lesson HTML contract (verified against tools/verify_workspace.py + working lessons)

## Files & numbering
- Lessons: `lessons/NNNN-<kebab-slug>.html`; NNNN = max(existing)+1, zero-padded 4 digits.
- Learning records: `learning-records/NNNN-<kebab-slug>.md`, contiguous from 0001.
- Lesson numbers are assigned at authoring time; intended study order lives in LESSON-MAP.md —
  read it before assigning a number.

## Required lesson elements (verifier checks, in order)
1. `<link rel="stylesheet" href="../assets/style.css">`
2. The literal text "Primary source"
3. `href="../MISSION.md"` (mission link)
4. `<section class="quiz">`

## Quiz markup (the contract assets/quiz.js binds)
```html
<section class="quiz">
<ol>
<li class="q">
<p class="qtext">Question text</p>
<pre><code>optional code</code></pre>
<ul class="options">
<li data-answer="true">Right option</li>
<li data-answer="false">Wrong option</li>
<li data-answer="false">Wrong option</li>
<li data-answer="false">Wrong option</li>
</ul>
<p class="explain">Explanation revealed after answering</p>
</li>
</ol>
</section>
```
- Options are `<li>` inside `<ul class="options">` — NOT `<button>` elements.
- assets/quiz.js behavior: on click, adds `.correct` to the `data-answer="true"` option,
  `.wrong` to a picked false one, `.disabled` to the rest, adds `.answered` to the `li.q`
  (CSS then shows its `p.explain`), and updates the `.quiz-score` div.
- The `.explain` reveal was added to quiz.js later; older lessons without `.explain` are
  unaffected.

## Author rules (no formatting clues)
- Every option in one question must have the SAME word count.
- Correct-answer positions must be shuffled across questions — never a consistent index.
- 4 options per question is the norm.

## Other shared styles used by lessons
- `.meta` (track · source · minutes · mission link), `.lede` (italic framing),
  `.callout` (mission tie), `.primary-source` (cite local PDF path + YouTube link),
  `.callout.ask` (follow-up prompt to the agent), `.lesson-nav` (links to sibling lessons +
  quickref).
- Primary sources cite the local curriculum PDFs (e.g.
  `.../01-intro-to-eecs-1-6.01SC/other/MIT6_01SCS11_chap04.pdf`) + YouTube links from
  `videos.txt`; the curriculum tree is READ-ONLY, zips extract under `work/<course>/`.

## Verify
```
python teach-workspace/tools/verify_workspace.py teach-workspace
python teach-workspace/tools/test_verify_workspace.py   # 17 unit tests
```
