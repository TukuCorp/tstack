---
name: hermes-nous-web-routing
description: Hermes live config is %LOCALAPPDATA%/hermes/config.yaml (not ~/.hermes); since 2026-10-21 web.backend=nous routes search to Perplexity via the Nous free tool pool
metadata:
  node_type: memory
  type: project
  originSessionId: fe7eaa52-4e78-43f9-976b-d8ad29ec1033
  modified: 2026-10-20T21:37:55.024Z
---

- Hermes reads `%LOCALAPPDATA%\hermes\config.yaml`; `~/.hermes/config.yaml` is a different file (the one tstack mirrors). Use `hermes config get/set/unset` to avoid editing the wrong one.
- 2026-10-21: signed in with `hermes auth add nous` (free Nous Portal account, OAuth device code; `hermes auth upgrade` only reports the anonymous session and is not this login). Free pool is live: coverage firecrawl/fal/openai-audio/browser-use/modal true.
- Set `web.backend: nous` and removed the old `web.search_backend: ddgs` pin (user chose global, cron jobs included). Result: web_search -> Perplexity Search API via `https://perplexity-gateway.nousresearch.com` ("managed"), web_extract -> Nous-managed Firecrawl. Verified with a live provider call.
- Undo: `hermes config set web.search_backend ddgs` and `hermes config unset web.backend`. The original `web.backend` value, if any, was not captured.
- Plan in progress: use this for the research skill ([[cross-tool-skill-mirrors]]): Perplexity fallback in `wide_pass.py` + Hermes workers in Herdr tabs for the deep pass.
