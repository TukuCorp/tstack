---
name: personal-wiki
description: Read or add durable context about the user, their projects and past decisions from the private personal wiki at ~/wiki. Use when a task needs background on the user or their work, or when asked to remember something durable.
version: 1.0.0
author: Tung Ho
---

# Personal wiki

`~/wiki` (private) holds durable context about the user, gathered from every agent they use.
Its schema and workflows are in `~/wiki/AGENTS.md`.

- **Read:** open `~/wiki/index.md`, then the pages it points to. Cite page names.
- **Write:** save durable facts to your own memory (`memories/MEMORY.md`, `memories/USER.md`) as usual;
  a daily sync copies them into `~/wiki/raw/hermes-memory/` and folds them into the wiki pages.
- Do not edit `~/wiki/raw/` or `~/wiki/scripts/`.
