---
name: cross-tool-skill-mirrors
description: "The brainstorm/plan/report/research/explain skills are mirrored across Claude Code, Codex, Opencode, and Hermes — changes to one must propagate to all, adapted per tool, with no cross-tool references"
metadata: 
  node_type: memory
  type: project
  originSessionId: f17ad96e-f79f-4aab-9802-1c005097b22b
---

Tung maintains the same authoring skill set (brainstorm, plan, report, research, explain) in four agent tools. When any of these skills changes in Claude Code, mirror the change to the others in the same session.

**Locations:**
- Claude Code: `~/.claude/commands/{plan,brainstorm,report,research}.md` + `~/.claude/commands/plan/assets/plan-template.md` + `~/.claude/commands/research/{references/,scripts/}`
- Codex: `~/.codex/skills/{plan,brainstorm,report,research}/SKILL.md` + `plan/assets/plan-template.md` + `research/{references/,scripts/}`
- Opencode: `~/.config/opencode/skills/{plan,brainstorm,report,research}/SKILL.md` + `plan/assets/plan-template.md` + `research/{references/,scripts/}` — **NOT a git repo** (has a `.gitignore` but no `.git`; verified 2026-07-12, corrects an earlier wrong assumption — do not attempt `git commit` here)
- Hermes: `%LOCALAPPDATA%/hermes/skills/software-development/plan/SKILL.md` + `plan/templates/plan-template.md`; brainstorm/report/research under `%LOCALAPPDATA%/hermes/skills/opencode/`

**How to apply:** Mirrors must be self-contained with NO reference to Claude Code (or any other tool). Adapt per tool: Codex/Opencode read `AGENTS.md` (not CLAUDE.md); Hermes saves plans to `.hermes/plans/` (its cc-nightly automation depends on that path) and uses Hermes frontmatter (version/author/metadata). The plan template content is tool-agnostic and byte-identical across all four copies. As of 2026-07-08 all four are on the portable-plan design (no Grill Me, binding-default ASMs, Environment & Conventions, portability audit — see [[portable-plan-design]]); /handoff was deleted everywhere. Hermes orchestration skills (agent-plans-execution, multi-phase-plan-implementation) still document legacy Grill Me pre-answering — deliberately left untouched. Research skill specifics: [[firecrawl-and-npx-mcp-setup]]. When mirroring text edits between tools, apply as a section-by-section edit set, not whole-file copy — baselines diverge per harness's available tools (Claude Code: WebSearch; Codex: web browsing; Opencode/Hermes: WebFetch against seed domains) and self-referencing paths (e.g. "next to this skill, e.g. `<path>`") must point to each mirror's own install location, not be copy-pasted from another mirror — this was found broken (Codex pointing at Opencode's path) and fixed 2026-07-12.


`explain` (added 2026-09-27, adapted from an external show-me skill): `~/.claude/commands/explain.md`, `~/.codex/skills/explain/SKILL.md`, `~/.config/opencode/skills/explain/SKILL.md`, `%LOCALAPPDATA%/hermes/skills/opencode/explain/SKILL.md`. Body is byte-identical across all four; only frontmatter differs.
