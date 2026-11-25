---
title: "/design skill: multi-model UI options, mashup and taste"
date: "2026-11-25"
type: "brainstorm"
depth: "standard"
source_request: "a /design skill, built first in Claude Code then mirrored to other agents with per-harness adjustments; substeps like UI options in HTML and mashup from existing examples; lessons from t3dotgg/tstack, cursor/plugins pstack, addyosmani/agent-skills, humanlayer/skills, emilkowalski/skills"
slug: "design-skill"
---

# Brainstorm: /design skill

## Statement of Intent
- **Outcome:** a `/design` skill that turns a brief into distinct HTML options on named axes (web UI, slide and doc layouts).
  - Options come from Claude, agy and Codex. Inside Herdr each gets its own pane; outside Herdr they run as headless CLIs.
  - Every option must pass hard gates and gets a cross-model rubric score.
  - You compare the options in a picker, mash up the best parts with references and the swipe file, riff on the winner, and keep the one you choose.
  - Each run adds to a taste store in the wiki.
- **User:** me, in any of the five harnesses (Claude Code, agy, Codex, Opencode, Hermes).
- **Why now:** single-shot agent UI keeps coming out generic. I want real alternatives to choose from, and taste that builds up across runs.
- **Success:**
  - A run gives 3 options that clearly differ and pass the gates.
  - Mashing and refining yields a mockup I would actually pick.
  - Over time the taste rules mean fewer rounds.
- **Out of scope:**
  - Porting the winner into product code.
  - Building native .pptx/.docx files (the deck and doc skills do that).
  - Searching public galleries for references.

## Problem & Why Now
Agents design one thing at a time, using defaults: purple gradients, `rounded-2xl` on everything, stock card grids. Nothing records why I liked or rejected a direction, so each session starts from zero. I want a studio step that comes before building: show me real alternatives, let me combine parts of them, and remember my taste across all my agents.

## Current vs Desired State
- **Current state:** no design skill exists. What does exist:
  - `grill-with-ui` (local browser page server, monitor, Send to Agent) and `brainstorm --ui` (its Visualize prototype).
  - Claude's built-in `artifact-design`.
  - `verify/scripts/shot.py` (real-phone emulation plus overflow flags).
  - `coop` (Claude + agy in Herdr panes) and `necro` (Codex in Herdr tabs).
  - `present`/`apdeck`/`pptx`/`docx` for native decks and docs.
  - The wiki (`~/wiki`), which every harness already reads.
  - The reference lessons are in `research/2026-11-25_design-skill-refs.md`.
- **Desired state:** `design/` in all five skill folders. Each copy holds its own picker and server scripts, the gates, and the rubric prompts, is mirrored by tstack, and has a parity test for its shared sections.
- **Key repo surfaces:**
  - Skills: `~/.claude/skills/design/` (first), `~/.gemini/config/skills/`, `~/.codex/skills/`, `~/.config/opencode/skills/`, `AppData/Local/hermes/skills/`.
  - tstack: `sync.py` (entries) and `tests/` (parity plus `test_self_contained`).
  - Wiki: `~/wiki/wiki/design/taste.md`, `~/wiki/design/swipe/`.

## Resolved Decisions
- **DEC-001:** Targets:
  - mockups come first, for web UI (pages, artifacts, dashboards, app screens) and beyond web (slide and doc layouts).
  - Inside a repo, the mockup uses the repo's look.
  - Rationale: one exploration step serves every output.
- **DEC-002:** Two depths:
  - **Full (default):** brief, design contract, references, multi-model options, gates and rubric, picker, mash, riff, stress, keep, taste.
  - **`--lean`:** options plus the picker only.
  - Rationale: the full loop for real design work, a fast path for quick picks.
- **DEC-003:** In full mode, other models produce options in Herdr panes, reusing the `coop`/`necro` plumbing.
  - Each writes one option into `.design/<slug>/options/` and reports back with `herdr agent prompt`.
  - Rationale: visible and steerable, and it uses plumbing that already exists.
- **DEC-004:** Pickers:
  - **Available:** published Artifact, local picker page (grill-with-ui style server: one option full size, keys 1-N, `?v=`, phone/desktop toggle, click to tag regions for grafting, per-option notes, Send to Agent) and static single-file HTML.
  - **Defaults:** Artifact in Claude Code (selections and comments come back through ArtifactComments or the page's ask/db capability). Local picker elsewhere.
  - **Override:** `--picker artifact|local|static`.
- **DEC-005:** Outside Herdr (`HERDR_ENV` unset), the other models run as headless CLIs (`agy -p`, `codex exec`, `claude -p`) in the background.
  - An unreachable provider is reported, not silently replaced.
  - quota-axi is checked before fan-out.
- **DEC-006:** References combine on-demand inputs with a swipe file that keeps growing.
  - **On demand:** my URLs (agent-browser screenshot plus extracted layout and tokens), images or screenshots, past artifacts, repo pages.
  - **Swipe file:** grows whenever I tag a ref or a picked option as keep, and future runs search it.
  - Designs are rebuilt in my own tokens and never copy branding or text.
  - Source: Addy's design contract, with its "patterns to reject" list.
- **DEC-007:** Taste store:
  - **Global:** `~/wiki/wiki/design/taste.md` (class-level rules with my own why; inferred whys are marked) and `~/wiki/design/swipe/` (compressed webp thumbnails of about 150 KB or less, plus notes).
  - **Per project:** `DESIGN.md` (tokens, personality, rejects) overrides the global store.
  - **Updates:** are proposed at the end of a run and written only after my OK (Emil's `learn-taste`).
  - Rationale: the wiki is the store all harnesses already share.
- **DEC-008:** Decks and docs:
  - options are fixed-size HTML mockups (1920x1080 slides, A4/Letter pages) shown in the same picker;
  - the winner becomes a layout spec (grid, hierarchy, chart types, per slide) that `present`/`apdeck`/`pptx`/`docx` build natively;
  - "Allotrope format" still means the house template.
- **DEC-009:** Judging in full mode.
  - **Hard gates on every option:**
    - `shot.py` phone and desktop, for overflow and off-screen controls;
    - axe-core accessibility;
    - an anti-slop lint: purple/indigo gradients, `rounded-2xl` everywhere, lorem ipsum, stock card grid, oversized padding.
  - **Rubric:** 3-6 criteria derived from the brief and hidden from the generators. A model that did not make the option scores it.
  - **Display and choice:** scores show in the picker, nothing is pre-picked, and I always decide.
- **DEC-010:** Mirrors: all 5 harnesses get the full studio, each adapted to its own tools, paths and default picker. Each copy is self-contained.
- **DEC-011:** `/design` always ends at the chosen mockup and never edits product code.
  - The stress pass (a toggle for Demo / Worst case / Empty / One / 1,000 rows / long text, plus the gates) still runs on the mockup.
  - Porting is a separate task.
- **DEC-012:** Command surface:
  - `/design <brief>` (full) and `--lean`.
  - Verbs: `refs <urls|files>`, `options [--n 3-5]`, `mash <base> +<part from X>`, `riff <option>`, `keep <option>`, `taste`.
  - Flags: `--picker`, `--models claude,agy,codex`.
  - State lives in `.design/<slug>/`, so any step can resume.
- **DEC-013:** Option count: 3 by default, capped at 5.
  - Each option states its axis (layout, density, personality, interaction model) before any code is written.
  - Two options that differ only in color or copy count as one, so one is replaced (Emil's `prototype`).
  - In full mode, each model gets one option on a different axis.
  - (Auto-decided from the refs.)
- **DEC-014:** The mash mechanic: I pick a base, then graft 1-2 tagged strengths from the losing options.
  - Options that converge are a signal to ship the consensus.
  - Options that scatter mean the brief was weak, so reframe instead of averaging them (pstack `arena`).
  - Riff generates a new set around the winner.
  - (Auto-decided from the refs.)
- **DEC-015:** Each copy carries its own picker and server scripts, adapted from `grill-with-ui`, with no cross-harness file references. Claude Code loads `artifact-design` before publishing. (Auto-decided from the self-contained-harness rule.)

## Assumptions & Constraints
- **ASM-001:** agy and Codex can be driven headlessly (`agy -p`, `codex exec`) on this machine, the way `necro` and `coop` already do.
- **ASM-002:** axe-core can run through agent-browser or a small npm script without a heavy install.
- **ASM-003:** the wiki repo can take small webp thumbnails without bloating.
- **CON-001:** Self-contained harnesses: every mirror copy uses only its own files. The wiki is the shared data store, not a shared code location.
- **CON-002:** Skill rules: code files stay at 1000 lines or fewer, no shouting in prose, rendered output is verified with `shot.py`, and unslop runs on prose.
- **CON-003:** Licences: all reference repos are MIT. Attribute adapted wording with a NOTICE comment, like `reflect` does. The `cursor/plugins` repo has no LICENSE file of its own, so confirm its license before copying any pstack wording.

## Approaches Considered
- **Chosen:** a single `/design` skill covering the full studio, with a lean mode and substep verbs.
  - Options come from Herdr panes, falling back to headless CLIs.
  - The picker depends on the harness, and the taste store lives in the wiki.
  - Why: it covers every substep I asked for, keeps one trigger, and builds up taste.
- **ALT-001:** an options-only picker. It lacks mashup, taste and judging, and those are the point.
- **ALT-002:** mashup-first. References matter, but generating options from scratch has to stay first-class.
- **ALT-003:** a separate skill per substep. That means more triggers to maintain across five harnesses.
- **ALT-004:** same-model subagents for fan-out. They give less real divergence across model families. This survives only as the outside-Herdr fallback, via CLIs.
- **ALT-005:** porting the winner into product code. Rejected: `/design` stops at the mockup.
- **ALT-006:** taste stored inside each skill copy. The copies would drift as each harness learns separately.

## Out of Scope
- Porting a mockup into product code (do it as a separate task or `/plan`).
- Building native .pptx/.docx files (hand off to `present`/`apdeck`/`pptx`/`docx`).
- Public gallery search for references.
- Animation design (Emil's animation skills cover that; this may come back later as a riff axis).

## Open Questions
1. **Q-001:** Should `brainstorm --ui` Visualize and `/explain` call `/design options` when a page's look matters?
   - **Recommended default:** no for v1. Add it once `/design` has proved itself.
   - **Why this matters:** it changes those skills' cost and how much they depend on each other.
2. **Q-002:** How does the Artifact picker return grafts to Claude: ArtifactComments, or a db/ask capability on the page?
   - **Recommended default:** page selections saved to the artifact db, which Claude reads after "Send". Fall back to comments.
   - **Why this matters:** it decides how smoothly the mash loop works in Claude Code. Settle it while building v1.
3. **Q-003:** Is there a quota floor for the full fan-out?
   - **Recommended default:** if quota-axi shows a provider under 20%, drop that provider and say so.
   - **Why this matters:** full mode runs 3 models plus a judge on every round.
