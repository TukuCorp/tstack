---
name: report
description: "Generate a self-contained HTML report in one of two explicit modes: end-of-phase reporting from the active session, or final reporting from a multi-phase markdown plan. Use only when the user explicitly asks for a report or invokes `/report`, such as `/report phase-name` for a phase artifact or `/report final path/to/plan.md optional-report-name` for a client-shareable final report."
---

# Report

## Purpose

Generate a polished, self-contained HTML report using one of two explicit modes:

- `phase` mode for a compact end-of-phase artifact derived primarily from the active session.
- `final` mode for a client-shareable synthesis derived primarily from a multi-phase markdown plan plus the surrounding session context.

Keep both outputs as single-file HTML artifacts with inline CSS and inline JavaScript.

## Trigger

- Use this skill only when the user explicitly asks for a report or invokes `/report`.
- Do not use it for ordinary progress updates or speculative summaries.
- Route by arguments:
  - If the first argument is exactly `final`, run final-report mode.
  - Otherwise run phase mode.
- Preserve backward compatibility: `/report`, `/report auth-refactor`, and `/report sprint-wrap-up` must continue to behave as phase mode.

## Mode Routing

### Phase Mode

- Invocation shapes:
  - `/report`
  - `/report [phase-name]`
- Treat the entire argument string as the preferred phase name source.
- If no phase name is provided, derive a short phase label from session context and sanitize it into lowercase ASCII kebab-case.

### Final Mode

- Invocation shapes:
  - `/report final [plan-file]`
  - `/report final [plan-file] [report-name]`
- Treat the first token after `final` as the markdown plan path.
- Treat the remaining tokens, if any, as the preferred report name.
- If no report name is provided, derive one from the plan title or filename and sanitize it into lowercase ASCII kebab-case.
- If the plan path is missing, stop and ask for exactly that missing path.

## Source-of-Truth Rules

### Phase Mode Sources

- Use the active session as the primary source of truth.
- Do not read files merely to reconstruct what happened; the work already exists in session memory.
- Read files only when a small factual gap genuinely blocks required metadata, such as the repository name or project identifier.
- Prefer concise factual reconstruction over exhaustive narration.

### Final Mode Sources

- Use the referenced markdown plan as the primary source of truth.
- Use the active session as supporting context for decisions, outputs, validations, and follow-through that the plan alone does not fully capture.
- Read only the files needed to understand the plan, confirm important facts, and identify named deliverables or evidence.
- Do not fabricate completion, findings, metrics, or recommendations beyond what the plan and session support.
- If the plan is partially complete or contains unresolved steps, surface that honestly in assumptions, limitations, and open questions.

## Output Contract

- Save one HTML file to `reports/` in the current repository.
- Create `reports/` if it does not exist.
- Keep the report in a single HTML file with inline CSS and inline JavaScript.
- Load Chart.js from a CDN script tag when charts are used.
- Render Mermaid in the same file when a logic or decision diagram is used.
- Keep each mode on its own base template rather than rebuilding the page shell from scratch.

### Phase Mode Output

- Use the filename format `YYYY-MM-DD-[phase-name].html`.
- Use `phase-report` if no better phase name can be derived.
- Start from `assets/report-template.html`.

### Final Mode Output

- Use the filename format `YYYY-MM-DD-final-[report-name].html`.
- Use `final-report` if no better report name can be derived.
- Start from `assets/final-report-template.html`.

## Phase Mode Structure

Always include all nine sections in this exact order, even when some sections have little data. Use explicit empty states rather than omitting a section.

1. Phase Header
2. Input -> Output Summary
3. Logic Flow
4. Math / Algorithm Used
5. Tools / Formulas / Methods
6. Results & Visualizations
7. Limitations / Second-Best Alternative
8. Errors / Warnings / Flags Encountered
9. Open Questions / Next Phase Seeds

## Final Mode Structure

Always include all eleven sections in this exact order, even when some sections have light content. Write for a colleague, client, or stakeholder who may know nothing about the project.

1. Title Hero
2. Executive Summary
3. Background & Objective
4. Inputs & Scope
5. Assumptions & Constraints
6. Methodology
7. Phase-by-Phase Analysis
8. Findings & Recommendation
9. Implementation Path
10. Risks / Open Questions
11. Appendices / Evidence Notes

### Final Mode Section Requirements

#### 1. Title Hero

- Show the report title, date, project name, repository name, and a one-line takeaway.
- Present this as the visual hero block.

#### 2. Executive Summary

- Lead with the answer, not the process.
- Summarize what was analyzed, what matters, and the recommended direction.
- Make this section understandable on its own in under two minutes.

#### 3. Background & Objective

- Explain the context, why the work mattered, and the specific objective of the multi-phase effort.

#### 4. Inputs & Scope

- List the major plan inputs, research inputs, artifacts, decision boundaries, and out-of-scope items.

#### 5. Assumptions & Constraints

- State known assumptions, missing data, environmental constraints, and confidence-limiting factors.

#### 6. Methodology

- Explain how the analysis progressed across phases.
- Describe the reasoning, frameworks, comparisons, checks, or evaluation methods that materially shaped the result.

#### 7. Phase-by-Phase Analysis

- Synthesize the phases into one coherent story rather than a diary dump.
- Show what each phase contributed, what changed, and why those transitions mattered.
- Include a Mermaid logic or decision diagram when it materially improves comprehension.

#### 8. Findings & Recommendation

- Present the major findings in plain language.
- Include tradeoffs, rejected options, and the chosen recommendation.
- If quantitative evidence exists, visualize it without inventing numbers.

#### 9. Implementation Path

- Translate the recommendation into practical next steps, dependencies, ordering, and suggested owners when they can be reasonably inferred.

#### 10. Risks / Open Questions

- State unresolved issues, major risks, key caveats, and questions that remain open.

#### 11. Appendices / Evidence Notes

- Include compact evidence tables, source notes, glossary items, or method notes needed for traceability.
- Keep appendices supportive rather than overwhelming.

## Build Procedure

### Phase Mode Procedure

1. Determine the phase name.
2. Determine the current date in `YYYY-MM-DD` format.
3. Determine project and repository labels from context or a quick metadata lookup.
4. Extract the phase narrative from the session itself: goals, constraints, major edits, notable commands, validations, and outcomes.
5. Extract any math, algorithm, heuristic, or scoring logic that materially influenced the phase, or determine that none was needed.
6. Decide whether the phase produced quantitative data that deserves Chart.js visualization.
7. Identify the main limitations, tradeoffs, and second-best alternative if one exists.
8. Identify any errors, warnings, blockers, or flags encountered and note their outcome.
9. Draft a Mermaid flowchart that matches the actual reasoning and decision path.
10. Write the responsive HTML document using the phase template.
11. Save the report to `reports/YYYY-MM-DD-[phase-name].html`.

### Final Mode Procedure

1. Parse the explicit invocation `/report final [plan-file] [report-name]`.
2. Read the referenced markdown plan and identify its phases, objectives, deliverables, and completion state.
3. Determine the current date in `YYYY-MM-DD` format.
4. Determine project and repository labels from the plan, current context, or a quick metadata lookup.
5. Extract supporting facts from the active session only where needed to clarify outcomes, validations, or rationale.
6. Build a client-safe narrative arc: background -> scope -> assumptions -> methodology -> synthesized analysis -> recommendation -> implementation path.
7. Decide whether quantitative evidence deserves Chart.js visualization and whether a Mermaid diagram materially helps explain the decision path.
8. Make uncertainty explicit instead of smoothing it away.
9. Write the responsive HTML document using the final-report template.
10. Save the report to `reports/YYYY-MM-DD-final-[report-name].html`.

## HTML Requirements

- Make the page self-contained: inline CSS, inline markup, inline initialization code.
- Use semantic HTML sections with stable headings.
- Keep desktop and mobile layouts readable.
- Keep long reports scroll-safe by avoiding fixed page overlays, `mask-image`, repeated `backdrop-filter` blur, and unnecessarily heavy box shadows.
- Add print CSS for PDF replication: preserve hierarchy, reduce ornamental effects, and encourage sensible page breaks.
- Prefer real text, tables, and structured cards over layout tricks that collapse in print.
- Avoid external local assets and avoid separate CSS or JavaScript files.

## Template Assets

### Phase Template

- Use `assets/report-template.html` as the phase template.
- Replace these tokens: `{{PHASE_NAME}}`, `{{DATE}}`, `{{PROJECT}}`, `{{REPO}}`, `{{INPUT_OUTPUT_CONTENT}}`, `{{MERMAID_DIAGRAM}}`, `{{MATH_ALGORITHM_SECTION}}`, `{{TOOLS_METHODS}}`, `{{CHARTS_SECTION}}`, `{{LIMITATIONS_ALTERNATIVES}}`, `{{ERRORS_WARNINGS_FLAGS}}`, `{{OPEN_QUESTIONS}}`.

### Final Template

- Use `assets/final-report-template.html` as the final-report template.
- Replace these tokens: `{{REPORT_TITLE}}`, `{{DATE}}`, `{{PROJECT}}`, `{{REPO}}`, `{{ONE_LINE_TAKEAWAY}}`, `{{EXECUTIVE_SUMMARY}}`, `{{BACKGROUND_OBJECTIVE}}`, `{{INPUTS_SCOPE}}`, `{{ASSUMPTIONS_CONSTRAINTS}}`, `{{METHODOLOGY}}`, `{{PHASE_ANALYSIS}}`, `{{FINDINGS_RECOMMENDATION}}`, `{{IMPLEMENTATION_PATH}}`, `{{RISKS_OPEN_QUESTIONS}}`, `{{APPENDICES_EVIDENCE}}`, `{{OPTIONAL_MERMAID_BLOCK}}`, `{{OPTIONAL_CHARTS_BLOCK}}`.

## Content Requirements

- Write from facts, not generic management filler.
- Mention the why behind major decisions, not just the what.
- Make uncertainty explicit when work ended with open questions.
- Do not fabricate metrics, certainty, source coverage, or completion status.
- For final mode, write in language a non-technical stakeholder can follow without losing technical precision where it matters.

## Visualization Rules

- Include Chart.js only when there is meaningful quantitative data.
- Derive chart labels and values directly from plan facts, session facts, or validated supporting material.
- Do not fabricate metrics to make the page look full.
- If no chart is justified, use a visually consistent empty state instead.
- Give canvases a fixed stable height so layout and resize work stay cheap while scrolling.
- Place every Chart.js canvas inside a dedicated chart wrapper such as `.viz-frame` or `.chart-frame`; never drop report charts into generic prose or table wrappers.
- Set low-cost Chart.js defaults before any chart creation: `Chart.defaults.devicePixelRatio = 1`, `Chart.defaults.animation = false`, `Chart.defaults.resizeDelay = 150`, `Chart.defaults.normalized = true`, and `Chart.defaults.maintainAspectRatio = false`.
- Mirror those performance settings in each chart config with `animation: false`, `resizeDelay: 150`, and `normalized: true` unless a report has a documented reason to differ.
- Ensure chart bootstrap code runs after any wrapper-normalization script so canvases size against the intended container.

## Mermaid Rules

- Use Mermaid syntax that renders reliably in a single embedded diagram.
- Prefer the most compact layout that preserves readability; for long linear phase narratives, default to `flowchart LR` rather than a tall `TD` chain.
- For final mode, use Mermaid only when it clarifies phase progression, reasoning branches, or option selection.
- Keep labels short enough to remain readable.
- Render Mermaid after the DOM is ready and constrain the resulting SVG to the container width.
- Keep Mermaid inside a bounded frame with a viewport-style max height so one diagram never consumes multiple screens.

## Reporting Heuristics

- Prefer one strong artifact over a verbose archive.
- Translate commands and implementation details into understandable outcomes.
- Keep the report visually striking but still professional.
- For final mode, treat phases as inputs to one story, not as separate mini-reports.
- Start final mode with the answer, then provide supporting evidence, then provide deeper traceability.

## Completion Checklist

- Ensure the skill ran only because `/report` was explicitly invoked.
- Ensure the chosen mode matches the argument shape.
- Ensure the HTML file exists in `reports/` with the mode-appropriate filename format.
- Ensure the selected template matches the selected mode.
- Ensure the page remains self-contained and print-safe.
- Ensure Chart.js and Mermaid are used only when justified and are backed by real content.
- Ensure the report is understandable without opening companion files.
- Ensure backward compatibility for legacy phase invocations.

## Example Invocation

- `/report auth-refactor`
- `/report sprint-wrap-up`
- `/report`
- `/report final plans/project-analysis.md`
- `/report final plans/project-analysis.md stakeholder-final`
