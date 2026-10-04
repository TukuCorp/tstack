---
name: skills-sh-serves-stale-pages
description: skills.sh serves pages for skills deleted from the source repo — always verify against the upstream main branch before importing a skill
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4a4c8b50-888f-4e15-abd3-db9e6d4def61
  modified: 2026-09-06T08:37:05.942Z
---

skills.sh renders a live-looking page (description, install command, security scans) for skills that have been **deleted from the source repository**. Verified 2026-09-06: `skills.sh/mattpocock/skills/request-refactor-plan` served a full page for a skill deleted from `mattpocock/skills@main` on 2026-08-05 (commit `c66bdee`), superseded by `/to-spec` and `/improve-codebase-architecture`. Tung dropped the import once told.

**Why:** importing a retired skill mirrors dead tooling into all of Tung's harnesses at once (see [[cross-tool-skill-mirrors]]), which is expensive to undo — and the author retired it because something better replaced it.

**How to apply:** before importing any skill from a registry page, check the source repo's default branch for the skill path (`gh api "repos/<owner>/<repo>/git/trees/main?recursive=1"`). If it's absent, read the removing commit + changeset — this repo's convention is that the changeset names the replacement. Surface the finding and the successor to Tung before installing anything.

Two false-trail notes for next time: skills.sh is a Next.js SPA whose flight payload embeds a 404 error-boundary template on **every** page, so grepping the HTML for "This page could not be found" gives a false positive — check for real content (the `application/ld+json` block carries name + description) instead. And a skill missing from `main` may still exist on a side branch, which is not evidence it is live.
