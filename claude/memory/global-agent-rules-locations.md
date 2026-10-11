---
name: global-agent-rules-locations
description: Where each harness's global instruction file lives (Claude Code, Opencode, Codex, omp, Hermes); shared rules like the Testing block must be mirrored to all
metadata:
  type: reference
---

- Claude Code: `~/.claude/CLAUDE.md`
- Opencode: `~/.config/opencode/AGENTS.md`
- Codex: `~/.codex/AGENTS.md`. The user emptied it on 2026-09-27 to start fresh; it has held only the Testing block since 2026-10-05.
- omp (oh-my-pi, `~/.bun/bin/omp`): `~/.omp/agent/AGENTS.md`. omp ignores the other tools' files unless they are enabled as foreign providers, and `config.yml` enables only `commands.*`.
- Hermes: `%LOCALAPPDATA%/hermes/SOUL.md` holds persona only ("procedures live in skills"), so rules go into the relevant skills. The `~/.hermes/SOUL.md` copy is different from the live one and may be stale.

On 2026-10-05 a shared Testing rule (E2E → integration → golden → unit for pure logic only; red/green at that level) was added to all five. Related: [[cross-tool-skill-mirrors]].
