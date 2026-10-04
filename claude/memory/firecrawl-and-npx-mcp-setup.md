---
name: firecrawl-and-npx-mcp-setup
description: Firecrawl personal API key locations across tools; npx is unreliable for MCP servers on this machine — install globally instead
metadata: 
  node_type: memory
  type: project
  originSessionId: 2abae44b-89ce-43cd-8c29-d4d810eacea0
---

The personal Firecrawl API key (`<REDACTED_KEY>`, free/hobby tier ~1000 credits/mo) originates from Hermes (`C:\Users\tukum\AppData\Local\hermes\.env`). As of 2026-07-09 it is also configured in:
- Claude Code user scope (`claude mcp add --scope user firecrawl ... -- cmd /c firecrawl-mcp`)
- Opencode global config (`C:\Users\tukum\.config\opencode\opencode.json`, `mcp.firecrawl`)

Both use the globally installed `firecrawl-mcp` binary (`npm install -g firecrawl-mcp`), NOT `npx`: npm 11.6.2 on this machine hits the `ECOMPROMISED: Lock compromised` libnpmexec bug when MCP hosts spawn `npx -y <pkg>`. Prefer global installs (or bun) for any new stdio MCP server here.

**As of 2026-07-12**, the same key is also a Windows **user environment variable** `FIRECRAWL_API_KEY` (via `setx`), independent of the MCP configs above. This powers a REST integration in the shared `research` skill's `scripts/wide_pass.py` (mirrored byte-identical across all four tools — see [[cross-tool-skill-mirrors]]): a `firecrawl_search()` function calls `POST https://api.firecrawl.dev/v2/search` (metadata-only, `limit=30`, `sources:["web"]`) to fill the `industry`/`web` source buckets during `/research --depth exhaustive`, replacing each harness's quota-limited fallback (WebSearch in Claude Code, browsing in Codex, WebFetch-seed-domains in Opencode/Hermes) as the primary backend. Response shape is `data.web[]` with `url`/`title`/`description`; query operators like `site:*.gov` and `filetype:pdf` pass through and work. On missing/invalid key or exhausted credits the script reports `firecrawl: "unavailable: <reason>"` and each harness's skill text falls back to its old behavior — this is documented, not a bug.

**Non-obvious finding:** unlike OpenAlex/`gh` (stable indexes), Firecrawl's live web search returns a *different* result set on repeated identical queries (confirmed: re-running the same query added many new non-duplicate URLs rather than ~0). Dedup-by-URL still holds correctly — this just means re-running a query is a legitimate way to reach saturation faster for these buckets, not a sign of a broken cache.
