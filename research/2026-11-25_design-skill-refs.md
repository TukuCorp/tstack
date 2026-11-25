# Design-skill references: lessons digest for a new /design skill

Date: 2026-11-25. Purpose: input for a brainstorm interview on a `/design` skill (generate several HTML UI options, mash up existing examples, pick one, refine). All files read raw from `HEAD` on 2026-11-25. Citations are `repo:path`.

## Licenses (for attribution if we copy text)

| Repo | License | Note |
| --- | --- | --- |
| emilkowalski/skills | MIT, (c) 2026 Emil Kowalski | `LICENSE` at root |
| cursor/plugins | MIT per README "License" section | Root has no LICENSE file (404); the README tree lists per-plugin LICENSE files. Confirm in the `pstack` folder before copying text |
| addyosmani/agent-skills | MIT, (c) 2025 Addy Osmani | `LICENSE` at root |
| humanlayer/skills | MIT, (c) 2026 HumanLayer | `LICENSE` at root |
| t3dotgg/tstack | MIT, (c) 2026 Theo Browne | `LICENSE` at root |

Ideas are not copyrightable, so paraphrase and steal the patterns freely. Keep the attribution line only if we copy wording or the picker CSS verbatim.

---

## emilkowalski/skills

### prototype (`skills/prototype/SKILL.md` + `PICKER.md`) - the closest match to /design
- **What it does:** builds 3 (max 5) genuinely different versions of ONE UI piece behind a visual picker; user flips live, picks, winner is promoted (`skills/prototype/SKILL.md`).
- **Steps:** Scope (one piece per run, restate brief in one sentence) > Recon (stack, tokens, personality, context) > Choose directions (name + axis each, before any code) > Build picker harness > Verify and hand off (table) > Promote on selection.
- **Divergence rule:** each variant must differ on a named axis (layout, density, personality, motion, interaction model). Two variants differing only in accent color or copy count as one; replace one. Names describe the direction ("Quiet", "Editorial"), never "Option A/B/C".
- **Honest tradeoff table:** columns Variant / Axis / When it's the right choice / Its cost. The agent never pre-picks a favorite; if asked, it answers from the product's personality, not aesthetics.
- **Picker harness (`PICKER.md`):** floating dark pill, bottom-center; number keys 1-N and arrows switch, R replays; selection persisted in URL `?v=2`; one variant at a time, full size, in realistic context (never thumbnails); switching is instant. Picker styling is fixed "chrome" so it never reads as a contestant. Standalone mode = one self-contained HTML file.
- **Round 2:** `riff <variant>` keeps the harness and diverges around the favored direction; `keep <variant>` promotes and deletes the prototype surface.
- **Rules worth copying:** never touch production code during exploration; every variant fully works with realistic content (no lorem ipsum, no dead buttons); no project means a restrained default look (neutral grays, one accent, system font).

### learn-taste (`skills/learn-taste/SKILL.md`)
- **What it does:** turns a session's design corrections into rules-with-why, written to `DESIGN.md`, a project skill, or a lint check. Proposes, then stops; writes only what the user approves.
- **Five correction signals:** explicit correction, silent edit (user changed `400` to `200`), repeated nudge (record where they landed, not the steps), revert or rejection (including picking variant B over A), confirmed non-obvious choice.
- **Filter tree:** would a fresh agent on a different component repeat this mistake? Existing rule already says it? Then rewrite stricter, do not duplicate. Contradiction? Show both, user picks.
- **Generalize to class level:** "raised surfaces use `shadow-raised`, never a solid border", not the instance and not "never use borders". Self-test: could an agent that knows nothing else still produce the wrong thing?
- **Distinctive mechanisms:** "never invent a why" (inferred whys are marked and confirmed); "a check beats a sentence" (prefer lint or token restriction); each rule carries a dated HTML comment holding the user's exact words; ensure CLAUDE.md or AGENTS.md says "read DESIGN.md before building UI".
- **Direct input to the refine loop:** the pick and the edits in /design are taste signals worth feeding here.

### break-ui (`skills/break-ui/SKILL.md`, references `CATALOG.md`)
- **What it does:** adversarial pass; renders a component with realistic worst-case data behind a dev-only "Demo data / Worst case" toggle and reports what broke.
- **Mechanisms:** field map table (value, source, limit, optional?), a worst-case fixture injected at the data boundary (never hand-edit markup), extra states Empty / One / 1,000 rows, checks at real container width, 320px, widest, 200% zoom, dark, RTL.
- **Failure-signature table:** symptom > cause > fix (squished avatar = `flex-shrink: 0`; overflow = `min-width: 0`; "1 members" = `Intl.PluralRules`; jittering numbers = `tabular-nums`).
- **Output:** What broke (severity Broken/Ugly/Fragile) / Decisions for you / What held up. Reports first and fixes only on request (`fix 1, 3`).
- **Fit for /design:** a cheap "stress the chosen option" step after pick; worst-case data also stops variants from being judged on flattering demo content.

### emil-design-eng (`skills/emil-design-eng/SKILL.md`)
- **What it does:** large craft reference (motion, press states, popover origin, clip-path, gestures, perf, a11y). Serves as the quality bar every prototype variant must meet.
- **Mechanisms:** animation decision framework (frequency > purpose > easing > duration), strict Before/After/Why review table, review checklist, "review your work the next day", slow-motion and frame-by-frame debugging.
- **Concrete defaults:** UI motion under 300ms, `ease-out` never `ease-in`, never animate from `scale(0)`, `scale(0.97)` on `:active`, custom easing curves.
- **Fit:** motion-heavy. For /design, steal "the craft bar applies to every variant, divergence is no excuse for sloppiness", not the content.

### apple-design (`skills/apple-design/SKILL.md`)
- **What it does:** translates Apple's WWDC fluid-interface talks to the web (springs, interruptibility, velocity handoff, materials, typography).
- **Mechanisms:** eight principles as vocabulary (Purpose, Agency, Responsibility, Familiarity, Flexibility, Simplicity-not-minimalism, Craft, Delight); tactical rules (wayfinding questions, grouping and mapping, specific labels over generic "Home").
- **Process section 17:** "an interactive demo is worth a million static designs"; design interaction and visuals together. This is the argument for HTML prototypes over static mockups.
- **Fit:** the eight principles work as a scoring rubric for options; spring and gesture detail is out of scope for a first /design.

### pick-ui-library (`skills/pick-ui-library/SKILL.md`)
- **What it does:** lookup table task > one library (Sonner, Vaul, cmdk, base-ui, motion, recharts...). Check `package.json` first; recommend one, not a menu; say so when leaving the curated list.
- **Fit:** an opinionated default list stops the agent re-deciding stack questions mid-design.

### find-animation-opportunities (`skills/find-animation-opportunities/SKILL.md`)
- **What it does:** read-only sweep that proposes motion; its main job is rejecting candidates through a 4-question gate (frequency, purpose, speed, function).
- **Mechanisms:** hard cap of 5-7 suggestions; required "Rejected candidates" section naming which gate killed each; "short list beats wishlist"; "nothing survives" is a good result.
- **Fit:** the restraint-first, reject-with-reason pattern applies equally to option generation.

### ui-cheatsheet (`ui-cheatsheet.md`)
- 11-row Problem > Solution table (tabular-nums, `-0.02em` heading tracking, `65ch` line cap, eased gradients, plurals). Tiny, high-signal; a good shape for a polish-pass checklist.

---

## cursor/plugins (pstack)

### arena (`pstack/skills/arena/SKILL.md`)
- **What it does:** N parallel candidates at the same task, pick a base, graft the best parts of the losers into it.
- **Steps:** Frame (artifact, 3-6 gradeable rubric criteria derived per task, candidates see only the task) > Fan out (all in one message, background, each with its own output dir or worktree, each writes a rationale naming rejected alternatives) > Cross-judge (read-only judge from a different vendor than the parent scores each candidate per criterion) > Pick base (read every candidate end to end, score per criterion, not holistic feel) > Graft (1-2 things per loser, folded in by hand so it stays coherent) > Verify.
- **Distinctive:** pick the base a future maintainer can extend most easily; if candidates converge, ship the consensus; if they wildly diverge, the frame was under-specified, reframe and re-run rather than averaging; output carries a synthesis note (base, grafts and sources, rejections, dropouts).
- **Direct template for "mash up existing examples":** pick a base, then graft.

### principle-exhaust-the-design-space (`pstack/skills/principle-exhaust-the-design-space/SKILL.md`)
- Two-sentence principle: for a novel interaction with no precedent, build 2-3 competing prototypes and compare side by side before committing. Confirms the 3-option default.

### principle-experience-first (`pstack/skills/principle-experience-first/SKILL.md`)
- Prefer delight over implementation convenience; "design decisions are cheaper in throwaway HTML than production code"; ship fewer polished features; every control must be justified; "the user is whoever consumes the work".

### make-bot-ui (`pstack/skills/make-bot-ui/SKILL.md`)
- **Not a design skill.** It builds a click-UI that POSTs to a webhook to wake a bot (secret handling, Tailscale hosting). Only reusable habit: probe the live page once before declaring it live. Skip it.

---

## addyosmani/agent-skills

### frontend-ui-engineering (`skills/frontend-ui-engineering/SKILL.md`)
- **What it does:** production-quality UI construction guidance (components, state, a11y, responsive, loading states).
- **Reference-led UI (the mashup recipe):** (1) search a trusted catalogue or use supplied references; (2) study 2-3 relevant screens and record decisions on hierarchy, density, navigation, controls, responsive behavior, states; (3) write a short design contract (screen's job, primary action, required states, responsive rules, patterns to reject); (4) rebuild the useful structure in the product's own tokens and content, never copy branding, text, imagery or exact layout. "References as evidence, not templates."
- **"Avoid the AI aesthetic" table:** purple/indigo everything, excess gradients, `rounded-2xl` everywhere, generic hero, lorem ipsum, oversized padding, stock card grids, shadow-heavy. Each with the reason and the production alternative.
- **Gates:** breakpoints 320/768/1024/1440; loading, empty, error, success, permission states; semantic color tokens; contrast 4.5:1; "Common rationalizations" and "Red flags" tables.

### accessibility-engineering (`skills/accessibility-engineering/SKILL.md`)
- **What it does:** audits an existing UI against WCAG 2.2 AA, then remediates verified violations. Explicitly not for building new UI (routes that to frontend-ui-engineering).
- **Steps:** automated pass (pinned `@axe-core/cli`, `pa11y`) > severity triage (Critical/Serious/Moderate/Minor) > manual keyboard and screen-reader audit > remediate verified issues only. States automated checks are "a smoke test, not proof".
- **Fit:** run the axe step on the chosen option as a final gate; skip screen-reader depth for an exploration tool.

### idea-refine (`skills/idea-refine/SKILL.md`)
- **What it does:** divergent then convergent loop: restate as "How Might We", ask 3-5 sharpening questions, generate 5-8 variations through named lenses (inversion, constraint removal, audience shift, combination, simplification, 10x, expert lens), cluster to 2-3 directions, stress-test (user value, feasibility, differentiation), surface assumptions, ship a one-pager with a "Not Doing" list.
- **Distinctive:** 5-8 considered ideas beat 20 shallow ones; "be honest, not a yes-machine"; the Not Doing list is called the most valuable part; user confirms before saving.
- **Fit:** the lens list is a ready-made generator for the named axes in prototype; the Not Doing list suits a design brief.

---

## humanlayer/skills

### show-me (`plugins/show-me/skills/show-me/SKILL.md`)
- **What it does:** explains the current topic with the smallest useful visual: pseudocode, call tree, component tree, file tree, Mermaid, diffs; for dense UI or state comparisons, one focused HTML file opened for the user.
- **Mechanisms:** "smallest view that makes the key point"; match product colors, type and spacing; real labels and data; desktop and mobile; diff blocks when only the delta matters.
- **Fit:** the design brief and decision summary can be a component-tree diff, not prose.

### visual-pr (`plugins/visual-pr/skills/visual-pr/SKILL.md`)
- **What it does:** writes a PR description from a fixed template: exactly one sentence "Why", 1-3 "Special things to note", and a compact show-me-style "Change outline" (only views that changed).
- **Fit:** the same structure can summarize the chosen option and what was promoted. Otherwise PR-specific.

### design-control-loop (`plugins/design-control-loop/skills/design-control-loop/SKILL.md`)
- **Not UI design.** It interviews the user to design a scheduled agent loop (set point, sensor, controller, actuator, dampener) and builds it. Relevant ideas only: read the repo before asking; propose options with trade-offs; write the agreed design down before building; make each piece runnable locally before wiring; a human steers via a memory file and `/iterate`; bound work-in-progress to one open PR.
- **Fit:** its memory/feedback file loaded each run is the same idea as learn-taste's DESIGN.md.

---

## t3dotgg/tstack

### council (`skills/council/SKILL.md`)
- **What it does:** three delegates from three different providers, each at high reasoning effort, run in parallel on the same request; the driver summarizes findings, disagreements and next steps.
- **Mechanisms:** if three providers are not reachable, report it, do not substitute; read-only delegates; check each result against the code as it arrives instead of idling; scores out of 10 per round in a table; do not edit while a delegate still reviews the checkout; "fight to keep scope limited".
- **Fit:** swap review for generation: one option per provider gives real stylistic divergence (different priors) instead of one model's three tints. Also usable as a final multi-model critique of the chosen option.

---

## Patterns worth stealing (ranked)

1. **Divergence by named axis, with names not letters.** State each option's axis (layout, density, personality, interaction model) before coding; two options that differ only in color or copy count as one and one is replaced. Default 3, cap 5. (emilkowalski/skills:skills/prototype/SKILL.md)
2. **Live picker harness, one full-size option at a time.** Keyboard 1-N and arrows, `?v=` URL persistence, instant swap, realistic surrounding context, fixed neutral chrome that is not part of the design. Single self-contained HTML when there is no project. (emilkowalski/skills:skills/prototype/PICKER.md)
3. **Pick a base, then graft.** Choose the base by rubric, then port 1-2 specific strengths from each loser by hand; if options converge, ship the consensus; if they scatter wildly, the frame was weak, so reframe instead of averaging. This is the "mash up" mechanic. (cursor/plugins:pstack/skills/arena/SKILL.md)
4. **Reference-led design contract before coding.** Study 2-3 reference screens, record decisions (hierarchy, density, controls, states), write a short contract including "patterns to reject", rebuild in the product's own tokens, never copy branding or text. (addyosmani/agent-skills:skills/frontend-ui-engineering/SKILL.md)
5. **Rubric of 3-6 gradeable criteria derived per task, hidden from generators, used by the picker.** Score per criterion, not on feel; optionally a cross-vendor read-only judge. (cursor/plugins:pstack/skills/arena/SKILL.md)
6. **Honest tradeoff table, no pre-picked favorite.** Per option: axis / when it wins / what it costs. The choice stays with the user; if asked, answer from product personality. (emilkowalski/skills:skills/prototype/SKILL.md)
7. **Taste capture from the pick and the edits.** Treat the chosen option, silent edits and rejections as signals; generalize to a class-level rule with the user's own why, mark inferred whys, propose then stop, write to `DESIGN.md`, prefer a lint check over a sentence. (emilkowalski/skills:skills/learn-taste/SKILL.md)
8. **Anti-slop table as a generation constraint and a review gate.** Name the AI defaults (purple/indigo, gradient noise, `rounded-2xl` everywhere, stock card grid, lorem ipsum, oversized padding) with the replacement for each. (addyosmani/agent-skills:skills/frontend-ui-engineering/SKILL.md)
9. **Multi-model fan-out for real divergence.** One option per provider at high effort, in parallel, read-only; report an unreachable provider instead of substituting. (t3dotgg/tstack:skills/council/SKILL.md, cursor/plugins:pstack/skills/arena/SKILL.md)
10. **Refine round diverges around the winner.** `riff <variant>` keeps the harness and generates a new set around the chosen direction; `keep <variant>` promotes and deletes the scratch surface. (emilkowalski/skills:skills/prototype/SKILL.md)
11. **Stress the winner with worst-case data, then run an automated a11y pass.** Dev-only toggle Demo / Worst case / Empty / One / 1,000 rows injected at the data boundary; axe-core as a smoke test; report before fixing. (emilkowalski/skills:skills/break-ui/SKILL.md, addyosmani/agent-skills:skills/accessibility-engineering/SKILL.md)
12. **Restraint with a rejected list.** Cap suggestions, require a "rejected, and which gate killed it" section, treat "nothing needed" as a valid result; end the brief with a "Not Doing" list. (emilkowalski/skills:skills/find-animation-opportunities/SKILL.md, addyosmani/agent-skills:skills/idea-refine/SKILL.md)

## Pitfalls / what to avoid

1. **Fake divergence.** Three tints of one idea teach nothing. Gate on the axis statement and drop duplicates before building. (prototype; idea-refine: 5-8 considered beats 20 shallow)
2. **Judging at postage-stamp size or on flattering data.** Thumbnail grids distort spacing; demo data hides overflow, plurals and empty states. Render full size with realistic, product-shaped content. (prototype; break-ui)
3. **Letting picker or review chrome look like a design choice.** Keep it fixed and neutral, separate from the options. (prototype PICKER.md)
4. **Adding rules the user did not express.** Generic good-practice rules are the agent's taste, which is exactly what the user was correcting; never invent a why, never write without approval. (learn-taste)
5. **Averaging or paste-merging options.** Mechanical grafts and averaged divergence produce incoherent results; fold grafts in by hand under one mental model, or reframe. (arena)
6. **Over-scope and over-process.** Prototype handles one piece per run; idea-refine warns against adding steps; council says to fight scope creep. Also skip the motion-heavy references (emil-design-eng, apple-design) in v1, and ignore make-bot-ui and design-control-loop, which are not UI design despite the names.
