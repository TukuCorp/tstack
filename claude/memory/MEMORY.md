# Memory Index

- [Cross-tool skill mirrors](cross-tool-skill-mirrors.md) — brainstorm/plan/report/research/explain skills exist in Claude Code, Codex, Opencode, AND Hermes; changes must propagate to all four, adapted per tool, no cross-tool references
- [Firecrawl & npx MCP setup](firecrawl-and-npx-mcp-setup.md) — personal Firecrawl key from Hermes now in Claude Code + Opencode; use global installs not npx for MCP servers (npm lock bug)
- [NotebookLM MCP setup](notebooklm-mcp-setup.md) — `nlm` CLI install/auth details; MCP server was deregistered 2026-07-30 but is RE-ADDED as `notebooklm-mcp` without the headless guard, still leaking temp dirs and unused — disable it, don't re-add without NOTEBOOKLM_HEADLESS=true
- [skills.sh serves stale pages](skills-sh-serves-stale-pages.md) — registry pages render for skills deleted upstream; verify against the source repo's main branch before importing
- [NotebookLM: CLI only](notebooklm-cli-preference.md) — use `nlm` CLI directly, not the mcp__notebooklm__* tools, per explicit user instruction
- [gws scope replacement breaks VN Weekly](gws-scope-replacement-vn-weekly.md) — `gws auth login` wipes unnamed scopes; job needs spreadsheets + gmail.modify
- [Concise, deliverable first](concise-deliverable-first.md) — lead with the tight deliverable; minimal commentary after
- [Global agent rules locations](global-agent-rules-locations.md) — CLAUDE.md/AGENTS.md paths for Claude Code, Opencode, Codex, omp, Hermes; mirror shared rules to all
