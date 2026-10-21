---
name: cross-tool-skill-mirrors
description: "The brainstorm/plan/report/research/explain skills are mirrored across Claude Code, Codex, Opencode, and Hermes — changes to one must propagate to all, adapted per tool, with no cross-tool references"
metadata: 
  node_type: memory
  type: project
  originSessionId: f17ad96e-f79f-4aab-9802-1c005097b22b
  modified: 2026-10-20T21:29:54.177Z
---

Tung maintains the same authoring skill set (brainstorm, plan, report, research, explain) in four agent tools. When any of these skills changes in Claude Code, mirror the change to the others in the same session.

**Locations:**
- Claude Code: `~/.claude/skills/{plan,brainstorm,research,verify,teach}/SKILL.md` + `plan/assets/plan-template.md` + `research/{references/,scripts/}` + `teach/references/*-FORMAT.md` (migrated from `~/.claude/commands/` on 2026-10-18 because every file under commands/ registered as its own slash command; `~/.agents/skills/source-command-*` migration stubs were archived the same day). Many skills also have a copy in `~/.agents/skills/` (read by Codex) — include it when mirroring.
- Codex: `~/.codex/skills/{plan,brainstorm,report,research}/SKILL.md` + `plan/assets/plan-template.md` + `research/{references/,scripts/}`
- Opencode: `~/.config/opencode/skills/{plan,brainstorm,report,research}/SKILL.md` + `plan/assets/plan-template.md` + `research/{references/,scripts/}` — **NOT a git repo** (has a `.gitignore` but no `.git`; verified 2026-07-12, corrects an earlier wrong assumption — do not attempt `git commit` here)
- Hermes: `%LOCALAPPDATA%/hermes/skills/software-development/plan/SKILL.md` + `plan/templates/plan-template.md`; brainstorm/report/research under `%LOCALAPPDATA%/hermes/skills/opencode/`

- verify: Claude Code + `~/.codex/skills/verify`, `~/.config/opencode/skills/verify`, `~/.agents/skills/verify`. Since 2026-10-21 each copy carries `scripts/verify_run.py` (deterministic runner) and `tests/test_verify_run.py`; these are byte-identical across copies, only SKILL.md wording and self-paths differ per tool.
- codebase + codebase-design: Claude Code, `~/.config/opencode/skills`, `~/.agents/skills` (adds `disable-model-invocation: true`), Hermes `%LOCALAPPDATA%/hermes/skills/engineering/` (support files under `references/`, own short descriptions, some files CRLF). No Codex copy. Mirrors say "Load the `X` skill" instead of Skill-tool calls and drop the Artifact-tool sentence.

- research: also `~/.github/skills/research` (GitHub-style project skills dir; omp lists it as `github/research`, hidden behind `~/.agents`). It sat on the April version until 2026-10-21, when it was replaced by the `~/.agents` copy; update it with the others. omp has no own research copy: it loads `~/.agents/skills/research` and `codex/research`. `~/.agents/skills/synced/<org>/research` is a claude.ai download (manifest.json), still the old version: change it on claude.ai, not locally.

**How to apply:** Mirrors must be self-contained with NO reference to Claude Code (or any other tool). Adapt per tool: Codex/Opencode read `AGENTS.md` (not CLAUDE.md); Hermes saves plans to `.hermes/plans/` (its cc-nightly automation depends on that path) and uses Hermes frontmatter (version/author/metadata). The plan template content is tool-agnostic and byte-identical across all four copies. As of 2026-07-08 all four are on the portable-plan design (no Grill Me, binding-default ASMs, Environment & Conventions, portability audit — see [[portable-plan-design]]); /handoff was deleted everywhere. Hermes orchestration skills (agent-plans-execution, multi-phase-plan-implementation) still document legacy Grill Me pre-answering — deliberately left untouched. Research skill specifics: [[firecrawl-and-npx-mcp-setup]]. When mirroring text edits between tools, apply as a section-by-section edit set, not whole-file copy — baselines diverge per harness's available tools (Claude Code: WebSearch; Codex: web browsing; Opencode/Hermes: WebFetch against seed domains) and self-referencing paths (e.g. "next to this skill, e.g. `<path>`") must point to each mirror's own install location, not be copy-pasted from another mirror — this was found broken (Codex pointing at Opencode's path) and fixed 2026-07-12.


`explain` (added 2026-09-27, adapted from an external show-me skill): `~/.claude/skills/explain/SKILL.md`, `~/.codex/skills/explain/SKILL.md`, `~/.config/opencode/skills/explain/SKILL.md`, `%LOCALAPPDATA%/hermes/skills/opencode/explain/SKILL.md`. Body is byte-identical across all four; only frontmatter differs.

`reflect` (added 2026-10-04, adapted from pstack @ 12d587d, MIT): `~/.claude/skills/reflect/`, `~/.codex/skills/reflect/`, `~/.config/opencode/skills/reflect/`, `%LOCALAPPDATA%/hermes/skills/software-development/reflect/`. `references/*.md` (4 reviewer/synthesizer templates) are byte-identical across all four; SKILL.md differs per tool (transcript digest source, subagent mechanism, frontmatter). Backlog goes to the project's `lessons.md`.

Since 2026-10-21 `/reflect` defaults to **audit mode** (adapted from Warp skill-doctor, MIT, `NOTICE-warp-skill-doctor.txt` kept in each copy; it must NOT be named LICENSE* because tstack/sync.py skips any skill folder containing a LICENSE* file as vendored, which silently dropped reflect from the mirror once on 2026-10-21) and the old flow is `/reflect --session`. New byte-identical files in all four copies: `scripts/{collect_sessions,render_report}.py` + their tests, `scorers/*.md`, `references/audit-mode.md`, `references/audit-edit-gate.md`. The collector scans Claude Code, Codex and Hermes history only (Opencode/omp not parsed), so the audit docs name those tools by necessity, an exception to the no-cross-tool-references rule. Reports go to `reports/reflect-<date>/` in cwd; transcripts stay in a temp dir. Not yet synced to tstack as of that date.

`unslop`: `~/.claude/skills/unslop/`, `~/.agents/skills/unslop/` (adds `disable-model-invocation: true`), `~/.config/opencode/skills/unslop/`, `%LOCALAPPDATA%/hermes/skills/unslop/` (top level, not under a category). SKILL.md bodies are byte-identical (only the `.agents` frontmatter differs), plus `references/review-feedback.md`. On 2026-10-21 rules 36 to 40 and edits to rules 1-12, 19-25, 27-30 were added from Wikipedia "Signs of AI writing" (CC BY-SA 4.0, attributed at the end of the skill); step 7 greps were extended. Not yet synced to tstack at that point.
