# Audit mode

Grade the installed skills by scoring recent local agent conversations, then draft the skill edits the evidence justifies and render one HTML report. Adapted from the skill-doctor skill in warpdotdev/common-skills (MIT), see `NOTICE-warp-skill-doctor.txt`.

Everything runs locally. Never upload transcripts, session files, or excerpts of them anywhere. Let `SKILL_ROOT` be the directory containing `SKILL.md`. Run every Python script with `python -I`.

## 0. Scope

If the user passed flags, use them and skip the questions: `--all` (all conversations), `--repo PATH` (repeatable), `--days N`, `--project-skills-only`. Otherwise check for a git repo (`git rev-parse --show-toplevel`) and ask, with the harness's question tool when it has one:

1. **Which conversations?** This repository (default when in a repo) / All conversations / Choose project paths (each must be a git repository).
2. **Which skills?** Project + global skills (default) / Project skills only.

Then proceed without further questions.

Two directories, one fresh per run:

- `WORK` in the scratchpad or system temp dir. The collector writes `inventory.json` and `transcripts/` here. Transcripts hold private session content, so they never go into a project folder.
- `REPORT_DIR` = `reports/reflect-<YYYY-MM-DD>/` under the working directory. `report.json`, `report.html` and `proposed/` go here. The report quotes session excerpts, so if the working directory is a git repository and `reports/` is not ignored, tell the user before they commit it. Do not edit `.gitignore` unasked.

## 1. Collect

```bash
python -I "$SKILL_ROOT/scripts/collect_sessions.py" --out "$WORK" \
  --repo "$REPO" [--repo ...] | --all-conversations \
  [--include-global-skills] [--days N] [--max-sessions N]
```

Defaults: 45 days, 12 sampled sessions, `--harness auto` (Claude Code, Codex and Hermes, whichever exist locally). Opencode and omp history is not scanned. Read `$WORK/inventory.json` (counts are under `stats`; each skill lists every path it was found at in `paths`). If `stats.sessions_sampled` is 0, say there is nothing recent in that scope (suggest `--days` or another scope) and stop. If `stats.skills_found` is 0, continue: the report becomes a case for creating skills and `skill_coverage` is 0. Hermes sessions without a recorded working directory only appear with `--all`.

## 2. Score each transcript

Rubrics: `scorers/efficiency.md`, `scorers/code-quality.md`, `scorers/procedure-compliance.md`, `scorers/verbosity.md`. For each file in `$WORK/transcripts/`, record per scorer: label, numeric score from the rubric's table, and a 1 to 3 sentence reason citing specifics. Code quality applies only where the transcript shows code changes; otherwise record `insufficient_evidence` and exclude it from that average and from the failed-conversation filter.

Transcripts are large. If the harness has subagents, delegate batches of about 4 transcripts to one subagent each, run in parallel, passing the four rubrics and asking for a compact JSON result per transcript. Otherwise score them in-process in batches. Subagents read only the files they are handed and edit nothing.

## 3. Aggregate

- `raw_*` = mean of each scorer across sessions (code quality excludes `insufficient_evidence`; if none had evidence use 0.5 and say so).
- `curve(x) = 0.5 + 0.5 * x`; `efficiency`, `code_quality`, `procedure_compliance`, `verbosity` = curve of the raw means.
- `skill_coverage` = fraction of sampled sessions where at least one installed skill was detected (0 if `skills_found` is 0).
- `overall = 0.25*efficiency + 0.25*code_quality + 0.2*procedure_compliance + 0.15*verbosity + 0.15*skill_coverage`.
- `failed_conversations`: any applicable raw scorer result below 0.5 (`insufficient_evidence` never fails one). Only these feed edit suggestions.
- `top_findings`: the 3 most impactful, specific patterns, one short concrete sentence each.

## 4. Draft edits

Follow `references/audit-edit-gate.md`. For each suggestion that clears the gate:

1. Read the skill's current file (path in `inventory.json`).
2. Write the full improved SKILL.md to `$REPORT_DIR/proposed/<skill-name>/SKILL.md`, changing only what the evidence justifies.
3. Put `diff -u current proposed` in the suggestion's `diff` field.
4. If `inventory.json` lists the skill at several paths (this user mirrors skills across tools), list the matching edit for each copy, adapted to its frontmatter, paths and tool names.

Never modify the real skill files in this step. Cite the failed session, scorer and moment behind every suggestion.

## 5. Report

Write `$REPORT_DIR/report.json` (the renderer's schema: title, generated_at, harness, handle, stats, scores as curved values with literal `skill_coverage`, top_findings, suggestions, optional `mode_note`). Its `stats` are `sessions_analyzed` (sessions you scored), `sessions_scanned` (`stats.sessions_in_scope`), `skills_found`, `skills_used`, `window_days`. Then:

```bash
python -I "$SKILL_ROOT/scripts/render_report.py" "$REPORT_DIR/report.json" --open
```

Tell the user the overall grade, the three findings and the report path as plain text, and list anything better enforced by a lint, hook or script as a Backlog candidate (see Applying edits in `SKILL.md`). End by asking whether to apply the suggestions.
