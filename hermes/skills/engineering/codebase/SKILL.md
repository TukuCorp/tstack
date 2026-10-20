---
name: codebase
description: "Scan a codebase for deepening opportunities, render an HTML report, and grill the one you pick. Use for an architecture review or to find refactors across a codebase; for a single module's interface, use codebase-design."
---

# Improve Codebase Architecture

Surface architectural friction and propose **deepening opportunities**: refactors that turn shallow modules into deep ones. The aim is testability, AI-navigability, and fewer wrong choices left open to the next agent: an enforced deep interface narrows what an agent can get wrong.

This command is _informed_ by the project's domain model and built on a shared design vocabulary:

- Load the `codebase-design` skill for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, the constraint test, "the interface is the test surface", "one adapter = hypothetical seam, two = real", "an abstraction is not a seam"). Use these terms exactly in every suggestion, and don't drift into "component," "service," "API," or "boundary."
- The domain language in `CONTEXT.md` gives names to good seams; ADRs in `docs/adr/` record decisions this command should not re-litigate.

## Process

### 1. Explore

**Scope before you scan: YAGNI.** Deepening a module pays off by making future changes to it easier, so put extra weight on the parts of the codebase that have recently changed. Decide *where* to look before you look:

- If the user named a direction (a module, a subsystem, a pain point), take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots, the files and areas that keep coming up, and let those paths pull your attention first. If the changes are scattered with no clear hot spot, widen the net.
- Weigh a second signal alongside change frequency: **where agents went wrong**. Reverts, `fix` commits that follow soon after another change to the same files, review comments, `lessons.md`, and the rules in `CLAUDE.md`/`AGENTS.md` (a written rule usually records a mistake that happened). A mistake class counts once it has happened twice. Those areas are where an enforced interface removes the most wrong choices.

Read the project's domain glossary (`CONTEXT.md`) and any ADRs in the area you're touching first.

Then spawn a sub-agent to walk the codebase. Don't follow rigid heuristics; explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow**, with an interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?
- Where would an agent that sees only one file go wrong? Look for two ways to do one task, internals importable from outside, hand-synced lists, and state with more than one writer.

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want. Apply the **constraint test** too: would the deepened interface remove wrong choices the next agent could make? A candidate can earn its place on either test.

### 2. Present candidates as an HTML report

Write a self-contained HTML file to `<project>/reports/architecture-review-<timestamp>.html` so each run gets a fresh file. Create `reports/` if it doesn't exist; if the project shouldn't commit reports, add `reports/` to `.gitignore` rather than writing the file anywhere else. Open it for the user (`xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows) and tell them the project-relative path.

The report uses **Tailwind via CDN** for layout and styling, and **Mermaid via CDN** for diagrams where a graph/flow/sequence reliably communicates the structure. Mix Mermaid with hand-crafted CSS/SVG visuals: use Mermaid when relationships are graph-shaped (call graphs, dependencies, sequences), and hand-built divs/SVG when you want something more editorial (mass diagrams, cross-sections, collapse animations). Each candidate gets a **before/after visualisation**. Be visual.

For each candidate, render a card with:

- **Files**: which files/modules are involved
- **Problem**: why the current architecture is causing friction
- **Solution**: plain English description of what would change
- **Benefits**: explained in terms of locality and leverage, and how tests would improve
- **Enforcement**: how the deepened shape stays deep once agents start editing it, at the highest level that works (architecture, then types, then a lint whose error names the fix, then a test, docs last; see the `codebase-design` enforcement ladder). Name the concrete mechanism for this repo's language and tooling, not a category
- **Before / After diagram**: side-by-side, custom-drawn, illustrating the shallowness and the deepening
- **Recommendation strength**: one of `Strong`, `Worth exploring`, `Speculative`, rendered as a badge

End the report with a **Top recommendation** section: which candidate you'd tackle first and why.

**Use CONTEXT.md vocabulary for the domain, and the `/codebase-design` vocabulary for the architecture.** If `CONTEXT.md` defines "Order," talk about "the Order intake module," not "the FooBarHandler," and not "the Order service."

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly in the card (e.g. a warning callout: _"contradicts ADR-0007, but worth reopening because…"_). Don't list every theoretical refactor an ADR forbids.

See [HTML-REPORT.md](references/HTML-REPORT.md) for the full HTML scaffold, diagram patterns, and styling guidance.

Do NOT propose interfaces yet. After the file is written, ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, load the `grilling` skill to walk the decision tree with them: constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize; load the `domain-modeling` skill to keep the domain model current as you go:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR, framed as: _"Want me to record this as an ADR so future architecture reviews don't re-suggest it?"_ Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing; skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Candidate agreed?** Offer to land its enforcement check first, in its own commit: make it fail on a real past mistake (or a scratch change that reintroduces one) before trusting it, and run the same command locally and in CI. Then add a row to a "rule → enforced by" table in the project's `CLAUDE.md`/`AGENTS.md`, so a later correction can tell whether the rule already had teeth.
- **Want to explore alternative interfaces for the deepened module?** Load the `codebase-design` skill and use its design-it-twice parallel sub-agent pattern.
