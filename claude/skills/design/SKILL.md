---
name: design
description: Design studio for UI before building it. Turns a brief into 3-5 genuinely different HTML options (web pages, artifacts, dashboards, app screens, slide and doc layouts), made in parallel by Claude, agy and Codex, gated for overflow, accessibility and AI-slop, scored on a rubric by a model that did not make them, shown in a picker, then mashed up (pick a base, graft parts from the others or from reference sites), riffed and kept, while it learns my taste into the wiki. Use for "/design", "design options for", "show me a few layouts", "mock up", "what could this page look like", "mash up these references", "riff on option B", or any request to explore how a UI, page, deck or doc should look before it is built. `--lean` skips the multi-model fan-out and judging. Stops at the chosen mockup; it does not port it into product code or build native .pptx/.docx.
---

# Design

A studio step that comes before building. One-shot agent UI tends to fall back on the same defaults (purple gradients, `rounded-2xl` everywhere, stock card grids). The fix is to see real alternatives, combine their best parts, and remember why I liked one. Each run ends at a mockup I chose. Porting that mockup into a repo is a separate task.

## This harness

- Harness: **Claude Code**. Skill folder: `DESIGN=~/.claude/skills/design`.
- Default picker: **artifact**, published with the Artifact tool; load `artifact-design` first. Use `--picker local|static` to override.
- Default `--models self,agy,codex`: you (or a subagent of yours) make one option, and agy and Codex each make one (`references/fanout.md`).
- Local picker sends: run `design.py serve` under the Monitor tool, so each Send arrives as an event.
- Write files with the Write tool. Run Python as `python -X utf8`.

## Commands

| Command | Does |
|---|---|
| `/design <brief>` | Full loop (below). |
| `/design --lean <brief>` | Brief, options from you alone, gates, picker. No fan-out or rubric. |
| `/design refs <urls\|files>` | Add references to the current run. |
| `/design options [--n 3-5]` | Make a fresh option set for the current brief. |
| `/design mash <base> +<part> from <X> ...` | Graft parts onto a base option. |
| `/design riff <option>` | Make a new set of options around one option. |
| `/design keep <option>` | Promote it, propose taste and swipe entries, clean up scratch options. |
| `/design taste` | Show and edit the taste rules. |

Flags: `--picker artifact|local|static`, `--models` (any subset of `self,claude,agy,codex`; default in "This harness"), `--n 3-5` (default 3).

Every run keeps its state in `.design/<slug>/` in the current folder: `brief.md`, `refs/`, `options/<name>/index.html`, `gates.json`, `scores.json`, `picks.jsonl`. Any verb resumes from there. When only one run exists, verbs act on it. When several exist, ask which one.

## Full loop

### 1. Brief and design contract

Run `python -X utf8 $DESIGN/scripts/design.py new --slug <slug> --brief "<one line>"`. It creates the run folder and prints its path.

Write `brief.md` with the following:

- **Goal and audience:** what the screen or page is for and who uses it.
- **Surface and size:** the kind of surface (web page, app screen, artifact, slide at 1920x1080, doc at A4 or Letter) and the devices it must work on.
- **Content:** real sample content. Take it from the repo, the user's files or the brief. Never use lorem ipsum, because fake text hides layout problems.
- **Taste, in order of precedence:** the project's `DESIGN.md` if one exists, then `~/wiki/wiki/design/taste.md`. Quote the rules that apply.
- **Contract:** hierarchy, density, controls, required states (empty, loading, error) and **patterns to reject**. Fill this after studying the references in step 2.
- **Rubric:** 3-6 criteria that a judge can grade and that come from this brief, such as "the next action is obvious within 3 seconds on a phone". Keep the rubric out of the generator prompts. Generators that see the rubric make options that match it instead of options that differ.

Ask the user at most 2 questions, and only about what the repo and files can't answer.

### 2. References

Read `references/references.md`. Capture each URL or file the user gave (screenshot, layout notes and tokens, never branding or copy). Then search the swipe file at `~/wiki/design/swipe/` for entries that match the brief. Record what each reference contributes in the contract: "B's dense table header", not "make it like Linear". With no references and no swipe hits, say so and go on.

### 3. Options on named axes

Pick one axis per option before writing any code: layout, density, personality, interaction model, or information order. Name each option after its axis (`dense-table`, `editorial`, `command-first`), not with a letter. If two options would differ only in color or copy, they are one option, so replace one of them.

- **Full mode:** follow `references/fanout.md`. You make one option yourself, and each other model makes one in parallel, on its own axis, from the same brief without the rubric. If a model is unreachable or below its quota floor, report it and make that option yourself instead of skipping it silently.
- **Lean mode:** make all options yourself.

Each option goes in `options/<name>/index.html`: one self-contained file with inline CSS and no build step. It carries `<meta name="design-axis" content="<axis>: <one line>">`, `<html lang>` and a `<title>`, because the picker and the a11y gate read them. It uses the real content and the tokens from the contract, plus a dev-only toggle for the states `Demo / Empty / One / Many / Long text` (see `references/gates.md`). For decks and docs, read `references/decks-docs.md`.

### 4. Gates, then rubric

Run `python -X utf8 $DESIGN/scripts/gates.py .design/<slug>`. It checks each option for AI-slop patterns, overflow on phone and desktop, and accessibility violations, and it writes `gates.json` and PNGs. An option that fails is fixed by whoever made it, or by you when the fix is small, and gates run again. Look at the PNGs yourself, because the gates catch defects, not ugliness.

- **Full mode:** a model that did not make an option scores it against the rubric. Each criterion gets a score from 1 to 5 and one line of evidence, saved to `scores.json` (`references/fanout.md`, "Judge").
- **Lean mode:** skip scoring.

### 5. Picker

Run `python -X utf8 $DESIGN/scripts/design.py picker .design/<slug>`. It builds `picker.html`, which shows one option at full size at a time:

- `1`-`N` and the arrow keys switch options, and `?v=<name>` keeps the choice in the URL;
- a phone/desktop toggle;
- gate badges and rubric scores per option;
- per-option notes;
- click-to-tag regions ("take this header").

Then deliver the picker as described in `references/picker.md`, which also covers how the user's picks come back to you.

Show a short tradeoff table next to it, with no favorite picked: option / axis / when it wins / what it costs. The user chooses. If they ask for your opinion, answer from the product's personality and the taste rules.

### 6. Mash and riff

The user picks a base and tags parts to graft onto it. Graft each tagged part by hand into a copy of the base (`options/<base>+<n>/`), rebuilt in the base's tokens rather than pasted. Then gate it again and refresh the picker.

- If the options converged, say so and offer the shared design.
- If they scattered widely, the brief was weak: tighten the contract and run step 3 again instead of averaging them.
- `riff <option>` makes a new set of options around one option, varying its weakest rubric criteria. It keeps the same picker.

### 7. Keep and taste

`keep <option>`:
1. Copies the option to `.design/<slug>/final/`.
2. Deletes the other options, leaving `picks.jsonl` and `brief.md` as the record.
3. Prints the path to the final option.

For decks and docs, the final output is a layout spec for the deck or doc skill (`references/decks-docs.md`).

Then read `references/taste.md` and **propose** what should be remembered:
- class-level taste rules, each with the user's own reason, marking any reason you inferred;
- swipe entries for references or parts the user tagged "keep".

Write them only after the user says OK.

Finish with these lines:
- final path;
- options made, and by which model;
- gate results;
- what was grafted from where;
- taste rules proposed and written.

## Rules of thumb

- Rebuild references in your own tokens. Never copy a site's branding, logos, text or images.
- Use real content, and test every option on a phone, because most layout bugs only show there.
- Restraint is a valid option. "This page needs less" can be one of the axes.
- Don't edit product code. If the user asks to build it, finish `keep` and treat the port as a new task.

<!-- Patterns adapted (MIT) from emilkowalski/skills (prototype, learn-taste, break-ui), cursor/plugins pstack (arena),
addyosmani/agent-skills (frontend-ui-engineering, accessibility-engineering, idea-refine), humanlayer/skills (show-me),
t3dotgg/tstack (council). See NOTICE.md. -->
